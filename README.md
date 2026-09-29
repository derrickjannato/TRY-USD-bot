Python bot that monitors the USD→TRY exchange rate in real time, logs it to a local database, and sends Telegram alerts when a critical threshold is crossed.

Why this project
After arriving in Turkey in October 2025 on the Türkiye Bursları scholarship, I converted the little USD I had into Turkish lira (TRY). Within six months, local inflation had eroded a significant share of that money's value.

Living in a country that runs on TRY, it's impossible to fully avoid currency exchanges on a daily basis — holding money exclusively in USD isn't a realistic option. This bot came out of that experience: instead of passively riding the USD/TRY market's swings, I wanted real-time notifications on its movement to make more informed exchange decisions and limit inflation's impact on my budget.

Next step: build a prediction model to identify the best moments to exchange, minimizing fees and losses tied to the exchange rate.

Features
Fetches the USD→TRY exchange rate via ExchangeRate-API
Logs historical rates to a local SQLite database
Automatic Telegram notifications:
A regular update on the current rate
A dedicated alert when the rate crosses a configurable threshold
Tech stack
Python 3
requests — API calls
python-dotenv — environment variable management
sqlite3 — local storage (standard library)
Installation
Clone the repo:
   git clone https://github.com/derrickjannato/TRY-USD-bot.git
   cd TRY-USD-bot
Install dependencies:
   pip install -r requirements.txt
Create a .env file in the project root (see .env.example) and fill in your keys:
EXCHANGERATE_API_KEY=your_api_key TELEGRAM_TOKEN=your_telegram_bot_token TELEGRAM_CHAT_ID=your_chat_id SEUIL_ALERTE=50.0

Usage
python script.py
The script can be run manually or scheduled (e.g. via cron on Linux/Mac or Task Scheduler on Windows) for automatic periodic tracking.

How to read the USD/TRY rate
The rate shown indicates how many TRY it takes to buy 1 USD. Its direction determines the best action to take:

Rate goes up (e.g. 48 → 50) → TRY weakens against the dollar. It's a good time to convert USD to TRY if you need to spend in lira — you get more lira for the same amount of dollars.
Rate goes down (e.g. 50 → 48) → TRY strengthens. It's a good time to buy dollars (convert TRY to USD) if you want to save or preserve value.
In short: high rate → sell dollars; low rate → buy dollars.



<img width="618" height="1280" alt="WhatsApp Image 2026-09-30 at 01 00 05" src="https://github.com/user-attachments/assets/73277c01-e0b6-4621-97ab-a7a4d4c626a2" />

