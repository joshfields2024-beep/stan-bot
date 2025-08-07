import requests
from bs4 import BeautifulSoup
import re

def search_oglasi_rs(settings):
    url = "https://www.oglasi.rs/nekretnine/prodaja-stanova/novi-sad"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return [f"❌ Greška pri konekciji sa oglasi.rs: {e}"]

    soup = BeautifulSoup(resp.text, "lxml")
    listings = soup.select("div.col-12.col-md-6.col-lg-4.item")
    print(f"[DEBUG] Pronađeno oglasa na strani: {len(listings)}")

    results = []
    for item in listings:
        title = item.select_one("h2")
        if not title:
            continue
        text = item.get_text(separator=" | ", strip=True)
        price_match = re.search(r"([\d\.,]+)\s*EUR", text)
        sqm_match = re.search(r"Kvadratura:\s*(\d+)", text)
        rooms_match = re.search(r"Sobnost:\s*([\w\-+]+)", text)

        price = float(price_match.group(1).replace(".", "").replace(",", ".")) if price_match else 0
        sqm = int(sqm_match.group(1)) if sqm_match else 0
        rooms = rooms_match.group(1) if rooms_match else ""

        location = None
        for loc in settings.get("locations", []):
            if loc.split("(")[0].strip().lower() in text.lower():
                location = loc
                break
        if not location:
            continue

        # Check criteria
        if not (settings["min_size"] <= sqm <= 130):
            continue
        if price > settings["max_price"]:
            continue
        # Trosoban ili vise
        if not re.search(r"Trosoban|Troiposoban|Četvorosoban", rooms, re.IGNORECASE):
            continue
        # poruke sa osobinama
        features = settings.get("features", [])
        if not any(feat.lower() in text.lower() for feat in features):
            continue

        link = item.select_one("a")
        href = link["href"] if link else ""
        url_full = f"https://www.oglasi.rs{href}"

        msg = f"<b>{title.get_text(strip=True)}</b>\nCena: {price} EUR | Kvadratura: {sqm} m² | Lokacija: {location}\n<a href='{url_full}'>Otvori oglas</a>"
        results.append(msg)

    return results
