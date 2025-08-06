import requests
import time
from bs4 import BeautifulSoup
import re

BOT_TOKEN = "8266970831:AAEAS5x1pfDSlm3UvA80PCsGsPgb_6nXW2E"
CHAT_ID = "586131374"
SENT_LISTINGS = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        print(f"[TELEGRAM] Status: {response.status_code}, Odgovor: {response.text}")
    except Exception as e:
        print("❌ Greška pri slanju poruke:", e)

def get_all_pages(base_url, page_param="strana"):
    page = 1
    all_results = []
    while True:
        url = f"{base_url}&{page_param}={page}"
        print(f"Scraping: {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        if "4zida.rs" in base_url:
            oglasi = soup.find_all("a", class_="StyledLink-sc-16btg2-2")
            if not oglasi:
                break
            for oglas in oglasi:
                link = "https://www.4zida.rs" + oglas.get("href", "")
                title = oglas.get_text().strip()
                if link not in SENT_LISTINGS:
                    all_results.append({"naziv": title, "link": link, "izvor": "4zida.rs"})
                    SENT_LISTINGS.add(link)
        elif "oglasi.rs" in base_url:
            oglasi = soup.find_all("div", class_="oglasi-item")
            if not oglasi:
                break
            for oglas in oglasi:
                a_tag = oglas.find("a", href=True)
                if a_tag:
                    link = "https://www.oglasi.rs" + a_tag["href"]
                    title = a_tag.get_text().strip()
                    if link not in SENT_LISTINGS:
                        all_results.append({"naziv": title, "link": link, "izvor": "oglasi.rs"})
                        SENT_LISTINGS.add(link)
        else:
            break

        page += 1
    return all_results

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n<a href='{stan['link']}'>🔎 Pogledaj oglas ({stan['izvor']})</a>"

if __name__ == "__main__":
    base_urls = [
        "https://www.4zida.rs/prodaja-stanova/novi-sad?soba=3-4-5-6&kvadratura=60-160&cena=0-180000&parking=true&garaza=true&terasa=true&internet=true&lift=true&lokacija=grbavica-novi-sad,sajam-novi-sad,zeleznicka-stanica-novi-sad,novo-naselje-novi-sad,nova-detelinara-novi-sad",
        "https://www.oglasi.rs/oglasi/nekretnine/prodaja-stanova/novi-sad?cena_do=180000&kvadratura_od=60&kvadratura_do=160&parking=1&garaza=1&terasa=1&internet=1&lift=1&sobe=3-4-5-6"
    ]

    print("🚀 Počinjem inicijalnu pretragu svih oglasa...")
    found_any = False
    for base_url in base_urls:
        oglasi = get_all_pages(base_url)
        for oglas in oglasi:
            found_any = True
            send_telegram_message(format_message(oglas))
            time.sleep(1)

    if not found_any:
        send_telegram_message("⚠️ Nema pronađenih oglasa koji ispunjavaju tvoje kriterijume.")

    print("⏱️ Ulazim u loop na svakih 10 minuta...")
    while True:
        time.sleep(600)  # 10 minuta
        for base_url in base_urls:
            oglasi = get_all_pages(base_url)
            new_listings = 0
            for oglas in oglasi:
                if oglas['link'] not in SENT_LISTINGS:
                    send_telegram_message(format_message(oglas))
                    SENT_LISTINGS.add(oglas['link'])
                    new_listings += 1
                    time.sleep(1)
            if new_listings == 0:
                print("🔍 Nema novih oglasa za sada.")
