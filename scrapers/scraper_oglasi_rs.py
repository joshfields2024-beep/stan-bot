# scraper_oglasi_rs.py
import requests
from bs4 import BeautifulSoup

def search_oglasi_rs(settings):
    base_url = "https://www.oglasi.rs/nekretnine/izdavanje/stanovi?"

    params = {
        "price_to": settings["max_price"],
        "rooms_from": settings["room_count"],
        "area_from": settings["min_size"],
        "location": "novi-sad",
        "ad_type": "prodaja"
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return [f"❌ Greska pri konekciji sa oglasi.rs: {str(e)}"]

    soup = BeautifulSoup(response.text, "lxml")
    listings = soup.find_all("div", class_="list-group-item")
    results = []

    for item in listings:
        try:
            title_tag = item.find("h2")
            link_tag = title_tag.find("a") if title_tag else None
            title = link_tag.text.strip() if link_tag else "N/A"
            url = "https://www.oglasi.rs" + link_tag.get("href") if link_tag else ""
            price = item.find("div", class_="price").text.strip() if item.find("div", class_="price") else "N/A"
            desc = item.find("div", class_="description").text.strip() if item.find("div", class_="description") else ""

            text = f"<b>{title}</b>\n{price}\n{desc}\n<a href='{url}'>Otvori oglas</a>"
            results.append(text)
        except Exception:
            continue

    return results
