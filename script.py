from dotenv import load_dotenv
load_dotenv()
import os
import requests
import sqlite3
from datetime import datetime, timezone

# --- Configuration ---
DB_PATH = "taux_change.db"
API_KEY = os.environ.get("EXCHANGERATE_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Le seuil est maintenant configurable via variable d'environnement,
# avec 50.0 comme valeur par défaut si tu n'en définis pas.
SEUIL_ALERTE = float(os.environ.get("SEUIL_ALERTE", 50.0))


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS taux (
            date_heure TEXT,
            devise TEXT,
            taux REAL,
            source TEXT
        )
    """)
    conn.commit()
    return conn


def get_taux_try_usd():
    if not API_KEY:
        raise ValueError("Clé API manquante : définis EXCHANGERATE_API_KEY")

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("result") != "success":
        raise RuntimeError(f"Réponse API inattendue : {data}")

    return data["conversion_rates"]["TRY"]


def get_dernier_taux(conn, devise="TRY"):
    cur = conn.execute(
        "SELECT taux FROM taux WHERE devise = ? ORDER BY date_heure DESC LIMIT 1",
        (devise,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def inserer_taux(conn, taux, devise="TRY", source="exchangerate-api.com"):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO taux (date_heure, devise, taux, source) VALUES (?, ?, ?, ?)",
        (now, devise, taux, source)
    )
    conn.commit()


def envoyer_telegram(message):
    """Envoie un message via le bot Telegram. Ne plante pas le script si ça échoue."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram non configuré (token ou chat_id manquant) — message non envoyé.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        resp = requests.post(
            url,
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=10
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        # On log l'erreur mais on ne fait pas planter tout le script pour ça
        print(f"Erreur lors de l'envoi Telegram : {e}")


def main():
    conn = init_db()
    taux_actuel = get_taux_try_usd()
    dernier = get_dernier_taux(conn)

    print(f"Taux actuel USD→TRY : {taux_actuel}")
    print(f"Dernier taux stocké : {dernier}")
    print(f"Seuil d'alerte configuré : {SEUIL_ALERTE}")

    if dernier is None or abs(taux_actuel - dernier) > 0.0001:
        inserer_taux(conn, taux_actuel)
        print("Nouvelle valeur insérée.")
    else:
        print("Taux inchangé, rien à insérer.")

    # --- Message systématique toutes les 6h (peu importe si ça a changé) ---
    message = f"💱 Point USD→TRY : {taux_actuel:.4f}"
    envoyer_telegram(message)

    # --- Alerte séparée si le seuil est dépassé ---
    if taux_actuel >= SEUIL_ALERTE:
        message_alerte = f"⚠️ Seuil dépassé ! TRY/USD a atteint {taux_actuel:.4f} (seuil : {SEUIL_ALERTE})"
        print(message_alerte)
        envoyer_telegram(message_alerte)

    conn.close()


if __name__ == "__main__":
    main()