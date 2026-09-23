"""
Gestion de la base SQLite : insertion et lecture des taux.
"""
import sqlite3
from datetime import datetime, timezone

DB_PATH = "taux_change.db"


def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
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


def inserer_taux(conn, taux, devise="TRY", source="exchangerate-api.com"):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO taux (date_heure, devise, taux, source) VALUES (?, ?, ?, ?)",
        (now, devise, taux, source)
    )
    conn.commit()


def get_dernier_taux(conn, devise="TRY"):
    cur = conn.execute(
        "SELECT taux FROM taux WHERE devise = ? ORDER BY date_heure DESC LIMIT 1",
        (devise,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_historique(conn, devise="TRY", limit=200):
    """
    Retourne les `limit` derniers points (date_heure, taux), triés du plus ancien au plus récent.
    Utilisé pour le graphe et la prédiction.
    """
    cur = conn.execute(
        """SELECT date_heure, taux FROM taux
           WHERE devise = ?
           ORDER BY date_heure DESC
           LIMIT ?""",
        (devise, limit)
    )
    rows = cur.fetchall()
    rows.reverse()  # du plus ancien au plus récent
    return rows