
import requests
import time
from bs4 import BeautifulSoup
import re

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

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\nLokacija: {stan['lokacija']}\nCena: {stan['cena']}\n<a href='{stan['link']}'>🔎 Pogledaj oglas ({stan['izvor']})</a>"

def is_oglas_valid(title, kvadratura, cena, lokacija, opis):
    try:
        kv = int(re.search(r"(\d+)\s?m2", kvadratura).group(1))
        price = int(re.sub(r"[^\d]", "", cena))
        if price > 18000000: return False
        if kv < 60: return False
        if not any(x in lokacija.lower() for x in ["grbavica", "sajam", "detelinara", "naselje", "železnička"]):
            return False
        if not any(x in opis.lower() for x in ["parking", "garaž", "terasa", "internet", "lift"]):
            return False
        if not any(x in title.lower() for x in ["trosoban", "četvorosoban", "troiposoban"]):
            return False
        return True
    except: return False

def fetch_from_oglasi():
    stanovi = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in range(1, 50):  # ide do 50, sve dok ima rezultata
        url = f"https://www.oglasi.rs/oglasi/nekretnine/prodaja-stanova/novi-sad/strana-{page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            oglasi = soup.find_all("div", class_="oglasi-item")

            if not oglasi:
                break

            for oglas in oglasi:
                try:
                    a_tag = oglas.find("a", href=True)
                    if not a_tag: continue
                    link = "https://www.oglasi.rs" + a_tag["href"]
                    title = a_tag.get_text().strip()

                    lokacija = oglas.find("div", class_="lokacija").text.strip() if oglas.find("div", class_="lokacija") else ""
                    kvadratura = oglas.find("div", class_="kvadratura").text.strip() if oglas.find("div", class_="kvadratura") else ""
                    cena = oglas.find("div", class_="cena").text.strip() if oglas.find("div", class_="cena") else ""
                    opis = oglas.text.lower()

                    if is_oglas_valid(title, kvadratura, cena, lokacija, opis):
                        stanovi.append({"naziv": title, "link": link, "izvor": "oglasi.rs", "lokacija": lokacija, "cena": cena})
                except:
                    continue
        except Exception as e:
            print("❌ Greška oglasi.rs:", e)
            continue
    return stanovi

def main_loop():
    poslati_linkovi = set()
    while True:
        print("🔍 Pretrazujem oglase...")
        novi_oglasi = fetch_from_oglasi()

        if not novi_oglasi:
            send_telegram_message("⚠️ Nema oglasa koji ispunjavaju tvoje kriterijume.")
        else:
            for oglas in novi_oglasi:
                if oglas['link'] not in poslati_linkovi:
                    send_telegram_message(format_message(oglas))
                    poslati_linkovi.add(oglas['link'])
                    time.sleep(1)

        time.sleep(600)  # svaka 10 minuta

if __name__ == "__main__":
    main_loop()
