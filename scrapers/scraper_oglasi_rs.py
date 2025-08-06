# scraper_oglasi_rs.py
import requests
from bs4 import BeautifulSoup

def search_oglasi_rs(settings):
    base_url = "https://www.oglasi.rs/nekretnine/prodaja/stanovi"
    params = {
        "price_to": settings["max_price"],
        "rooms_from": settings["room_count"],
        "area_from": settings["min_size"]
    }

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return [f"❌ Greška pri konekciji sa oglasi.rs: {e}"]

    soup = BeautifulSoup(resp.text, "lxml")
    # Prilagodi ako se HTML promenio
    listings = soup.find_all("div", class_="list-group-item")
    results = []

    for item in listings:
        title_tag = item.find("h2")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.find("a")
        url = "https://www.oglasi.rs" + (link["href"] if link and link.get("href") else "")
        price = item.find("div", class_="price")
        price_text = price.get_text(strip=True) if price else ""
        desc = item.find("div", class_="description")
        desc_text = desc.get_text(strip=True) if desc else ""

        message = f"<b>{title}</b>\n{price_text}\n{desc_text}\n<a href='{url}'>Otvori oglas</a>"
        results.append(message)

    return results
