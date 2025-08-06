import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8266970831:AAEAS5x1pfDSlm3UvA80PCsGsPgb_6nXW2E"
CHAT_ID = "586131374"

LOKACIJE = [
    "grbavica", "sajam", "zeleznicka-stanica", "novo-naselje", "nova-detelinara"
]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        print(f"[TELEGRAM] Status: {response.status_code}")
    except Exception as e:
        print("❌ Greška pri slanju poruke:", e)

def validan_oglas(naziv):
    naziv = naziv.lower()
    return (
        any(x in naziv for x in ["trosoban", "četvorosoban", "petosoban", "troiposoban", "višesoban"]) and
        any(x in naziv for x in ["garaža", "parking", "garažu", "garaza", "parking mesto", "mesto"]) and
        not any(x in naziv for x in ["izdavanje", "lokal"])
    )

def fetch_4zida():
    stanovi = []
    try:
        for lok in LOKACIJE:
            for page in range(1, 10):
                url = f"https://www.4zida.rs/prodaja-stanova/novi-sad/{lok}?strana={page}"
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                oglasi = soup.find_all("a", class_="StyledLink-sc-16btg2-2")
                for oglas in oglasi:
                    naslov = oglas.get_text(strip=True)
                    if validan_oglas(naslov):
                        link = "https://www.4zida.rs" + oglas.get("href", "")
                        stanovi.append({"naziv": naslov, "link": link, "izvor": "4zida.rs"})
    except Exception as e:
        print("❌ 4zida.rs:", e)
    return stanovi

def fetch_oglasi_rs():
    stanovi = []
    try:
        for lok in LOKACIJE:
            for page in range(1, 10):
                url = f"https://www.oglasi.rs/oglasi/nekretnine/prodaja-stanova/novi-sad/{lok}/page/{page}"
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                oglasi = soup.find_all("div", class_="oglasi-item")
                for oglas in oglasi:
                    a_tag = oglas.find("a", href=True)
                    if a_tag:
                        naslov = a_tag.get_text(strip=True)
                        if validan_oglas(naslov):
                            link = "https://www.oglasi.rs" + a_tag["href"]
                            stanovi.append({"naziv": naslov, "link": link, "izvor": "oglasi.rs"})
    except Exception as e:
        print("❌ oglasi.rs:", e)
    return stanovi

def fetch_nekretnine_rs():
    stanovi = []
    try:
        for lok in LOKACIJE:
            for page in range(1, 10):
                url = f"https://www.nekretnine.rs/prodaja-stanova/novi-sad/{lok}/?page={page}"
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                oglasi = soup.find_all("div", class_="StyledListingCard-sc-12g7x8e-0")
                for oglas in oglasi:
                    a_tag = oglas.find("a", href=True)
                    if a_tag:
                        naslov = a_tag.get_text(strip=True)
                        if validan_oglas(naslov):
                            link = "https://www.nekretnine.rs" + a_tag["href"]
                            stanovi.append({"naziv": naslov, "link": link, "izvor": "nekretnine.rs"})
    except Exception as e:
        print("❌ nekretnine.rs:", e)
    return stanovi

def fetch_halooglasi():
    stanovi = []
    try:
        for lok in LOKACIJE:
            for page in range(1, 10):
                url = f"https://www.halooglasi.com/nekretnine/prodaja-stanova/novi-sad/{lok}?page={page}"
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                oglasi = soup.find_all("article", class_="product-list-item")
                for oglas in oglasi:
                    a_tag = oglas.find("a", href=True)
                    if a_tag:
                        naslov = a_tag.get_text(strip=True)
                        if validan_oglas(naslov):
                            link = "https://www.halooglasi.com" + a_tag["href"]
                            stanovi.append({"naziv": naslov, "link": link, "izvor": "halooglasi.com"})
    except Exception as e:
        print("❌ halooglasi.com:", e)
    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n<a href='{stan['link']}'>🔗 Pogledaj oglas ({stan['izvor']})</a>"

if __name__ == "__main__":
    print("🔍 Tražim stanove u odabranim delovima Novog Sada...")

    svi_oglasi = fetch_4zida() + fetch_oglasi_rs() + fetch_nekretnine_rs() + fetch_halooglasi()

    if not svi_oglasi:
        send_telegram_message("⚠️ Nema oglasa koji ispunjavaju tvoje kriterijume.")
    else:
        for oglas in svi_oglasi:
            send_telegram_message(format_message(oglas))
            time.sleep(1)
