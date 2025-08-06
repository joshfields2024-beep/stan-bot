import json
import time
from scrapers.scraper_4zida import search_4zida
from telegram_bot import send_telegram_message

def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    settings = load_settings()
    all_results = []

    for scraper in [search_4zida]:
        results = scraper(settings)
        all_results.extend(results)

    if not all_results:
        send_telegram_message("⚠️ Nema pronađenih oglasa koji ispunjavaju tvoje kriterijume.")
    else:
        for result in all_results:
            send_telegram_message(result)

if __name__ == "__main__":
    main()
