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
    listings = soup.select("div[class*=article-body]")  # selector za svaki oglas
    print(f"[DEBUG] Pronađeno oglasa na strani: {len(listings)}")

    results = []
    for item in listings:
        text = item.get_text(separator=" | ", strip=True)

        price = 0
        sqm = 0
        rooms = ""
        price_match = re.search(r"([\d\.\,]+)\s*EUR", text)
        sqm_match = re.search(r"Kvadratura:\s*(\d+)", text)
        rooms_match = re.search(r"Sobnost:\s*([\w\-+]+)", text)

        if price_match:
            price = float(price_match.group(1).replace(".", "").replace(",", "."))
        if sqm_match:
            sqm = int(sqm_match.group(1))
        if rooms_match:
            rooms = rooms_match.group(1)

        # Lokacija
        location = None
        for loc in settings.get("locations", []):
            if loc.split("(")[0].strip().lower() in text.lower():
                location = loc
                break
        if not location:
            continue

        # Filtri
        if not (settings["min_size"] <= sqm <= settings.get("max_quadrature", 130)):
            continue
        if price > settings["max_price"]:
            continue
        if not re.search(r"Trosoban|Troiposoban|Četvorosoban", rooms, re.IGNORECASE):
            continue
        if not any(feat.lower() in text.lower() for feat in settings.get("features", [])):
            continue

        title = item.select_one("h2")
        title_text = title.get_text(strip=True) if title else "Oglas"
        link = item.select_one("a")
        href = link["href"] if link else ""
        url_full = f"https://www.oglasi.rs{href}"

        msg = f"<b>{title_text}</b>\nCena: {price} EUR | {sqm} m² | Lokacija: {location}\n<a href='{url_full}'>Otvori oglas</a>"
        results.append(msg)

    return results
