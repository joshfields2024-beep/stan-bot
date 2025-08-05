import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8266970831:AAEAS5x1pfDSlm3UvA80PCsGsPgb_6nXW2E"
CHAT_ID = "586131374"  # Fiksiran chat ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, data=payload)
        print(f"[TELEGRAM] Status: {response.status_code}, Odgovor: {response.text}")
    except Exception as e:
        print("❌ Greška pri slanju poruke:", e)

def fetch_from_4zida():
    url = "https://www.4zida.rs/prodaja-stanova/novi-sad?strana=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("a", class_="StyledLink-sc-16btg2-2")

        for oglas in oglasi:
            link = "https://www.4zida.rs" + oglas.get("href", "")
            title = oglas.get_text().strip()
            stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("❌ Greška 4zida:", e)

    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n<a href='{stan['link']}'>🔎 Pogledaj oglas</a>"

if __name__ == "__main__":
    print("🚀 Testiram bot – slanje svih trenutnih oglasa...")

    oglasi = fetch_from_4zida()

    if not oglasi:
        send_telegram_message("⚠️ Nema pronađenih oglasa na 4zida.rs.")
    else:
        for oglas in oglasi:
            msg = format_message(oglas)
            send_telegram_message(msg)
            time.sleep(1)  # mali delay da izbegneš spam blokadu
