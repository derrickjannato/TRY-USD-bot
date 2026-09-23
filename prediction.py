
"""
Prédiction simple de la tendance du taux USD/TRY à partir des données récentes.
 
Méthode : régression linéaire (numpy.polyfit) sur les derniers points.
- La pente donne la tendance (hausse / baisse / stable).
- Le R² (qualité de l'ajustement) est converti en "pourcentage de confiance" :
  plus les points récents suivent une droite nette, plus la confiance est haute.
  Ce n'est PAS une probabilité statistique rigoureuse, juste un indicateur de
  fiabilité de la tendance observée — à traiter comme une estimation, pas une vérité.
"""
from datetime import datetime, timedelta
import numpy as np
 
from database import get_historique
 
SEUIL_STABLE = 0.0005  # variation par heure en dessous de laquelle on considère "stable"
 
 
def predire_tendance(conn, devise="TRY", limit=50, horizon_heures=6):
    historique = get_historique(conn, devise=devise, limit=limit)
 
    if len(historique) < 5:
        return {
            "dispo": False,
            "raison": "Pas assez de données pour une prédiction fiable (5 points minimum)."
        }
 
    dates = [datetime.fromisoformat(d) for d, _ in historique]
    taux = np.array([t for _, t in historique])
 
    t0 = dates[0]
    x = np.array([(d - t0).total_seconds() / 3600 for d in dates])  # en heures
 
    # Régression linéaire : taux = pente * heure + ordonnée
    pente, ordonnee = np.polyfit(x, taux, 1)
 
    # Qualité de l'ajustement (R²)
    taux_predit_sur_historique = pente * x + ordonnee
    ss_res = np.sum((taux - taux_predit_sur_historique) ** 2)
    ss_tot = np.sum((taux - np.mean(taux)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    r2 = max(0.0, min(1.0, r2))
 
    # Confiance affichée : R² pondéré par le nombre de points dispo (plus de points = plus fiable)
    facteur_volume = min(1.0, len(historique) / 30)
    confiance_pct = round(r2 * facteur_volume * 100, 1)
 
    # Prédiction à horizon_heures dans le futur
    x_futur = x[-1] + horizon_heures
    taux_predit = pente * x_futur + ordonnee
 
    dernier_taux = taux[-1]
    variation = taux_predit - dernier_taux
    variation_pct = (variation / dernier_taux) * 100
 
    if abs(pente) < SEUIL_STABLE:
        tendance = "stable"
    elif pente > 0:
        tendance = "hausse"
    else:
        tendance = "baisse"
 
    return {
        "dispo": True,
        "tendance": tendance,
        "pente_par_heure": pente,
        "dernier_taux": dernier_taux,
        "taux_predit": taux_predit,
        "variation_pct": variation_pct,
        "confiance_pct": confiance_pct,
        "horizon_heures": horizon_heures,
        "nb_points": len(historique),
    }
 
 
def formater_prediction(resultat, devise="TRY"):
    if not resultat["dispo"]:
        return f"📉 Prédiction indisponible : {resultat['raison']}"
 
    emoji = {"hausse": "📈", "baisse": "📉", "stable": "➡️"}[resultat["tendance"]]
 
    texte = (
        f"{emoji} Tendance : {resultat['tendance']} "
        f"(sur les {resultat['nb_points']} derniers points)\n"
        f"Taux actuel : {resultat['dernier_taux']:.4f}\n"
        f"Prévision dans {resultat['horizon_heures']}h : {resultat['taux_predit']:.4f} "
        f"({resultat['variation_pct']:+.2f}%)\n"
        f"Confiance dans cette tendance : {resultat['confiance_pct']:.0f}%\n"
        f"⚠️ Estimation basée sur la régression linéaire des dernières valeurs, "
        f"pas une prévision financière garantie."
    )
    return texte
 
