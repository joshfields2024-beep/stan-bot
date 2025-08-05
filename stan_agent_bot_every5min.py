
import requests
import time
from bs4 import BeautifulSoup

BOT_TOKEN = "8203967152:AAF6d3JldWam3TphxHYrofxquzUQsf3FI2M"
CHAT_ID = "586131374"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
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
            if any(loc in title.lower() for loc in ["sajmište", "novo naselje", "detelinara"]):
                stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("Greška 4zida:", e)
    return stanovi

def fetch_from_oglasi_rs():
    url = "https://www.oglasi.rs/nekretnine/prodaja-stanova/novi-sad"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("div", class_="oglas")
        for oglas in oglasi:
            a_tag = oglas.find("a", href=True)
            if a_tag:
                link = "https://www.oglasi.rs" + a_tag["href"]
                title = a_tag.get_text(strip=True)
                if any(loc in title.lower() for loc in ["sajmište", "novo naselje", "detelinara"]):
                    stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("Greška oglasi.rs:", e)
    return stanovi

def fetch_from_halooglasi():
    url = "https://www.halooglasi.com/nekretnine/prodaja-stanova/novi-sad"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("a", class_="product-title")
        for oglas in oglasi:
            link = "https://www.halooglasi.com" + oglas["href"]
            title = oglas.get_text(strip=True)
            if any(loc in title.lower() for loc in ["sajmište", "novo naselje", "detelinara"]):
                stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("Greška halooglasi:", e)
    return stanovi

def fetch_from_sasomange():
    url = "https://sasomange.rs/c/nekretnine/prodaja-stanova/novi-sad"
    headers = {"User-Agent": "Mozilla/5.0"}
    stanovi = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        oglasi = soup.find_all("a", class_="entity-title")
        for oglas in oglasi:
            link = "https://sasomange.rs" + oglas["href"]
            title = oglas.get_text(strip=True)
            if any(loc in title.lower() for loc in ["sajmište", "novo naselje", "detelinara"]):
                stanovi.append({"naziv": title, "link": link})
    except Exception as e:
        print("Greška sasomange:", e)
    return stanovi

def format_message(stan):
    return f"<b>{stan['naziv']}</b>\n🔗 <a href='{stan['link']}'>Pogledaj oglas</a>"

if __name__ == "__main__":
    sent_links = set()
    while True:
        all_listings = []
        all_listings += fetch_from_4zida()
        all_listings += fetch_from_oglasi_rs()
        all_listings += fetch_from_halooglasi()
        all_listings += fetch_from_sasomange()

        for stan in all_listings:
            if stan["link"] not in sent_links:
                send_telegram_message(format_message(stan))
                sent_links.add(stan["link"])

        time.sleep(300)  # 5 minuta
