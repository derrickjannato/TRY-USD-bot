from dotenv import load_dotenv
load_dotenv()
 
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
 
from database import init_db, inserer_taux, get_dernier_taux
from graph import generer_graphe
from prediction import predire_tendance, formater_prediction
 
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
 
# --- Configuration ---
API_KEY = os.environ.get("EXCHANGERATE_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # utilisé pour les notifs automatiques
SEUIL_ALERTE = float(os.environ.get("SEUIL_ALERTE", 50.0))
INTERVALLE_NOTIF_SECONDES = int(os.environ.get("INTERVALLE_NOTIF_SECONDES", 6 * 3600))
 
conn = init_db()
 
 
def get_taux_try_usd() -> float:
    if not API_KEY:
        raise ValueError("Clé API manquante : définis EXCHANGERATE_API_KEY")
 
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
 
    if data.get("result") != "success":
        raise RuntimeError(f"Réponse API inattendue : {data}")
 
    return data["conversion_rates"]["TRY"]
 
 
def enregistrer_si_nouveau(taux: float) -> None:
    dernier = get_dernier_taux(conn)
    if dernier is None or abs(taux - dernier) > 0.0001:
        inserer_taux(conn, taux)
 
 
# --- Commandes ---
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    taux = get_taux_try_usd()
    enregistrer_si_nouveau(taux)
    await update.message.reply_text(f"💱 Taux actuel USD→TRY : {taux:.4f}")
 
 
async def graphe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chemin = generer_graphe(conn)
    if chemin is None:
        await update.message.reply_text("Pas encore assez de données pour tracer un graphe.")
        return
    with open(chemin, "rb") as f:
        await update.message.reply_photo(photo=f, caption="📊 Évolution du taux USD/TRY")
 
 
async def prediction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resultat = predire_tendance(conn)
    await update.message.reply_text(formater_prediction(resultat))
 
 
# --- Job périodique (toutes les 6h, indépendamment de l'utilisateur) ---
 
async def notification_periodique(context: ContextTypes.DEFAULT_TYPE):
    if not TELEGRAM_CHAT_ID:
        logger.warning("TELEGRAM_CHAT_ID non configuré, notification périodique ignorée.")
        return
 
    taux = get_taux_try_usd()
    enregistrer_si_nouveau(taux)
 
    message = f"💱 Point USD→TRY : {taux:.4f}"
    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
 
    chemin = generer_graphe(conn)
    if chemin:
        with open(chemin, "rb") as f:
            await context.bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=f)
 
    resultat = predire_tendance(conn)
    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=formater_prediction(resultat))
 
    if taux >= SEUIL_ALERTE:
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"⚠️ Seuil dépassé ! USD/TRY a atteint {taux:.4f} (seuil : {SEUIL_ALERTE})"
        )
 
 
def main():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN manquant dans les variables d'environnement.")
 
    app = Application.builder().token(TELEGRAM_TOKEN).build()
 
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("graphe", graphe))
    app.add_handler(CommandHandler("prediction", prediction))
 
    # Notification toutes les 6h, dès le lancement (first=0)
    app.job_queue.run_repeating(
        notification_periodique,
        interval=INTERVALLE_NOTIF_SECONDES,
        first=0
    )
 
    logger.info("Bot démarré, en écoute...")
    app.run_polling()
 
 
if __name__ == "__main__":
    main()