import requests
import time

TELEGRAM_TOKEN = "8203967152:AAF6d3JldWam3TphxHYrofxquzUQsf3FI2M"
TELEGRAM_CHAT_ID = "your_chat_id_here"  # <- ZAMENI sa tvojim pravim chat ID ako već nisi

already_sent = set()

def fetch_from_4zida():
    url = "https://api.4zida.rs/api/search/real-estates?city=novi-sad&types%5B%5D=flat&structure%5B%5D=three_rooms&size_from=65&price_to=180000"
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    oglasi = []
    for item in data.get("data", []):
        id = item.get("id")
        title = item.get("attributes", {}).get("title", "")
        link = f"https://www.4zida.rs/real-estate/{id}"
        cena = item.get("attributes", {}).get("price", {}).get("value", "")
        kvadratura = item.get("attributes", {}).get("size", "")
        struktura = item.get("attributes", {}).get("structure", "")
        oglasi.append({
            "id": id,
            "naziv": title,
            "cena": cena,
            "kvadratura": kvadratura,
            "struktura": struktura,
            "link": link
        })
    return oglasi

def send_telegram_message(poruka):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": poruka,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def format_message(oglas):
    return f"""🏠 *{oglas['naziv']}*
📐 {oglas['kvadratura']} m² | {oglas['struktura']}
💶 {oglas['cena']} €
🔗 [Pogledaj oglas]({oglas['link']})
"""

if __name__ == "__main__":
    while True:
        print("🔍 Proveravam nove oglase...")
        novi_oglasi = fetch_from_4zida()
        for oglas in novi_oglasi:
            if oglas["id"] not in already_sent:
                poruka = format_message(oglas)
                send_telegram_message(poruka)
                already_sent.add(oglas["id"])
        time.sleep(300)  # ⏱ pauza 5 minuta
