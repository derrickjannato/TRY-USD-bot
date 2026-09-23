"""
Génère un graphe PNG de l'évolution du taux USD/TRY à partir de l'historique en base.
"""
import matplotlib
matplotlib.use("Agg")  # pas d'affichage graphique, juste génération de fichier
import matplotlib.pyplot as plt
from datetime import datetime

from database import get_historique

GRAPH_PATH = "taux_graph.png"


def generer_graphe(conn, devise="TRY", limit=200, output_path=GRAPH_PATH):
    historique = get_historique(conn, devise=devise, limit=limit)
    if len(historique) < 2:
        return None  # pas assez de données pour tracer une courbe

    dates = [datetime.fromisoformat(d) for d, _ in historique]
    taux = [t for _, t in historique]

    plt.figure(figsize=(9, 5))
    plt.plot(dates, taux, color="#1f77b4", linewidth=1.8, marker="o", markersize=2)
    plt.title(f"Évolution du taux USD/{devise}")
    plt.xlabel("Date")
    plt.ylabel(f"1 USD en {devise}")
    plt.grid(alpha=0.3)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=130)
    plt.close()
    return output_path