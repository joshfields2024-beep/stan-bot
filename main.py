import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8266970831:AAEAS5x1pfDSlm3UvA80PCsGsPgb_6nXW2E"
CHAT_ID = "586131374"

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
            stanovi.append({"naziv": title, "link": link, "izvor": "4zida.rs"})
    except Exception as e:
        print("❌ Greška 4zida:", e)
    return stanovi

def fetch_from_oglasi():
    url = "https://www.oglasi.rs/oglasi/nekretnine/prodaja-stanova/novi-sad"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("div", class_="oglasi-item")

        for oglas in oglasi:
            a_tag = oglas.find("a", href=True)
            if a_tag:
                link = "https://www.oglasi.rs" + a_tag["href"]
                title = a_tag.get_text().strip()
                stanovi.append({"naziv": title, "link": link, "izvor": "oglasi.rs"})
    except Exception as e:
        print("❌ Greška oglasi.rs:", e)
    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n<a href='{stan['link']}'>🔎 Pogledaj oglas ({stan['izvor']})</a>"

if __name__ == "__main__":
    print("🚀 Testiram bot – slanje svih trenutnih oglasa...")

    svi_oglasi = fetch_from_4zida() + fetch_from_oglasi()

    if not svi_oglasi:
        send_telegram_message("⚠️ Nema pronađenih oglasa ni na 4zida.rs ni na oglasi.rs.")
    else:
        for oglas in svi_oglasi:
            send_telegram_message(format_message(oglas))
            time.sleep(1)
