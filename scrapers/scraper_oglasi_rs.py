import requests
from bs4 import BeautifulSoup

def search_oglasi_rs(settings):
    results = []
    base_url = "https://www.oglasi.rs/nekretnine/prodaja/stanovi"
    
    params = {
        "price_to": settings["max_price"],
        "rooms_from": settings["room_count"],
        "area_from": settings["min_size"],
        "location": "novi-sad",
        "ad_type": "prodaja"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return [f"❌ Greška pri konekciji sa oglasi.rs: {e}"]

    soup = BeautifulSoup(response.text, "lxml")
    listings = soup.select("div.article-body")

    for listing in listings:
        title = listing.select_one("h2.title")
        price = listing.select_one("span.price")
        url_tag = listing.select_one("a")

        if title and price and url_tag:
            title_text = title.get_text(strip=True)
            price_text = price.get_text(strip=True)
            link = "https://www.oglasi.rs" + url_tag["href"]
            results.append(f"<b>{title_text}</b>\n{price_text}\n{link}")

    return results
