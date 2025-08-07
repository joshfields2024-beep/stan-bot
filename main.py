import json
from scrapers.scraper_oglasi_rs import search_oglasi_rs
from telegram_bot import send_telegram_message

def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("[DEBUG] Pokrećem Selenium scraper za oglasi.rs")
    results = search_oglasi_rs(load_settings())

    if not results:
        send_telegram_message("⚠ Nema pronađenih oglasa koji ispunjavaju tvoje kriterijume.")
    else:
        for res in results:
            send_telegram_message(res)

if __name__ == "__main__":
    main()
