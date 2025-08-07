import requests
import json

def send_telegram_message(message):
    with open("settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    token = config["telegram_bot_token"]
    chat_id = config["telegram_chat_id"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=payload)
