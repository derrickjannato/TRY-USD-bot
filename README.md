Bot Python qui surveille le taux de change USD→TRY en temps réel, l'enregistre dans une base de données locale, et envoie des alertes Telegram lorsqu'un seuil critique est dépassé.

## Pourquoi ce projet

Après mon arrivée en Turquie en octobre 2025 grâce à la bourse Türkiye Bursları, j'ai converti le peu de dollars que j'avais en livres turques (TRY). Au bout de six mois, l'inflation locale avait fait perdre une part significative de la valeur de cet argent.

Vivant dans un pays qui fonctionne en TRY, il est impossible d'éviter totalement les échanges de devises au quotidien — garder son argent exclusivement en dollars n'est pas une option viable. Ce bot est né de ce constat : plutôt que de subir passivement les fluctuations du marché USD/TRY, j'ai voulu être notifié en temps réel de son évolution afin de prendre des décisions d'échange plus informées, et ainsi limiter l'impact de l'inflation sur mon budget.

**Prochaine étape** : développer un modèle de prédiction pour identifier les meilleurs moments pour échanger, dans le but de minimiser les frais et pertes liés au taux de change.

## Fonctionnalités

- Récupération du taux de change USD→TRY via [ExchangeRate-API](https://www.exchangerate-api.com/)
- Historisation des taux dans une base SQLite locale
- Notifications automatiques via Telegram :
  - Un point régulier sur le taux actuel
  - Une alerte dédiée si le taux dépasse un seuil configurable

## Stack technique

- Python 3
- [`requests`](https://pypi.org/project/requests/) — appels API
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) — gestion des variables d'environnement
- `sqlite3` — stockage local (bibliothèque standard)

## Installation

1. Clonez le repo :
```bash
   git clone https://github.com/derrickjannato/TRY-USD-bot.git
   cd TRY-USD-bot
```

2. Installez les dépendances :
```bash
   pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet (voir `.env.example`) et renseignez vos clés :

EXCHANGERATE_API_KEY=votre_cle_api
TELEGRAM_TOKEN=votre_token_bot_telegram
TELEGRAM_CHAT_ID=votre_chat_id
SEUIL_ALERTE=50.0


## Utilisation

```bash
python script.py
```

Le script peut être lancé manuellement ou planifié (ex: via `cron` sur Linux/Mac ou le Planificateur de tâches sur Windows) pour un suivi automatique régulier.

## Comment lire le taux USD/TRY

Le taux affiché indique **combien de TRY il faut pour obtenir 1 USD**. Sa direction détermine la meilleure action à prendre :

- **Le taux monte** (ex: 48 → 50) → le TRY **s'affaiblit** face au dollar. C'est le bon moment pour **convertir du USD vers du TRY** si vous devez dépenser en lires — vous en obtenez davantage pour le même montant en dollars.
- **Le taux baisse** (ex: 50 → 48) → le TRY **se renforce**. C'est le bon moment pour **acheter des dollars** (convertir du TRY vers du USD) si vous voulez épargner ou préserver de la valeur.

En résumé : **taux haut → vendre des dollars** ; **taux bas → acheter des dollars**.

## Structure du projet

TRY-USD-bot/
├── script.py # Script principal
├── taux_change.db # Base de données SQLite (générée automatiquement)
├── .env # Variables d'environnement (non versionné)
├── .env.example # Modèle de configuration
├── requirements.txt # Dépendances Python
└── README.md

