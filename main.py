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

def passes_filters(title):
    title_lower = title.lower()

    kvadratura_ok = any(x in title_lower for x in ["65", "66", "70", "75", "80", "85", "90", "100", "120"])
    sobe_ok = any(x in title_lower for x in ["3.0", "3.5", "4.0", "troiposoban", "četvorosoban", "petosoban"])
    garaza_ok = any(x in title_lower for x in ["garaža", "parking"])
    return kvadratura_ok and sobe_ok and garaza_ok

def fetch_from_4zida(max_pages=5):
    stanovi = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, max_pages + 1):
        url = f"https://www.4zida.rs/prodaja-stanova/novi-sad?strana={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            oglasi = soup.find_all("a", class_="StyledLink-sc-16btg2-2")

            for oglas in oglasi:
                link = "https://www.4zida.rs" + oglas.get("href", "")
                title = oglas.get_text().strip()
                if passes_filters(title):
                    stanovi.append({"naziv": title, "link": link, "izvor": "4zida.rs"})
        except Exception as e:
            print(f"❌ Greška 4zida, strana {page}:", e)
    return stanovi

def fetch_from_oglasi(max_pages=5):
    stanovi = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, max_pages + 1):
        url = f"https://www.oglasi.rs/oglasi/nekretnine/prodaja-stanova/novi-sad?page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            oglasi = soup.find_all("div", class_="oglasi-item")

            for oglas in oglasi:
                a_tag = oglas.find("a", href=True)
                if a_tag:
                    link = "https://www.oglasi.rs" + a_tag["href"]
                    title = a_tag.get_text().strip()
                    if passes_filters(title):
                        stanovi.append({"naziv": title, "link": link, "izvor": "oglasi.rs"})
        except Exception as e:
            print(f"❌ Greška oglasi.rs, strana {page}:", e)
    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n<a href='{stan['link']}'>🔎 Pogledaj oglas ({stan['izvor']})</a>"

if __name__ == "__main__":
    print("🚀 Pretražujem stanove u Novom Sadu...")

    svi_oglasi = fetch_from_4zida(5) + fetch_from_oglasi(5)

    if not svi_oglasi:
        send_telegram_message("⚠️ Nema oglasa koji ispunjavaju tvoje kriterijume.")
    else:
        for oglas in svi_oglasi:
            send_telegram_message(format_message(oglas))
            time.sleep(1)
