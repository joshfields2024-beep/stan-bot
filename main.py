import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8203967152:AAf6d3JldWam3TphxHYrofxquzUQs3f3I2M"
CHAT_ID = "586131374"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Greška pri slanju poruke:", e)

def fetch_from_4zida():
    url = "https://www.4zida.rs/prodaja-stanova/novi-sad?strana=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("a", class_="StyledLink-sc-1b6t9b2-2")
        for oglas in oglasi:
            link = "https://www.4zida.rs" + oglas.get("href", "")
            title = oglas.get_text().strip()
            stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("Greška 4zida:", e)
    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n🔗 <a href='{stan['link']}'>Pogledaj oglas</a>"

if __name__ == "__main__":
    while True:
        print("🔍 Proveravam nove oglase...")
        novi_oglasi = fetch_from_4zida()
        for stan in novi_oglasi:
            message = format_message(stan)
            send_telegram_message(message)
        time.sleep(300)
