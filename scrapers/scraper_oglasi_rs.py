import requests
import re
from bs4 import BeautifulSoup

def search_oglasi_rs(settings):
    url = (
        "https://www.oglasi.rs/nekretnine/prodaja-stanova/novi-sad/"
        "grbavica+zeleznicka-stanica+sajam+rotkvarija+nova-detelinara+novo-naselje"
        "?pr[e]=180000&pr[c]=EUR"
        "&d[Sobnost][0]=Trosoban"
        "&d[Sobnost][1]=Cetvorosoban+i+više"
        "&d[Sobnost][2]=Troiposoban"
        "&d[Kvadratura][0]=60"
        "&d[Kvadratura][1]=70"
        "&d[Kvadratura][2]=80"
        "&d[Kvadratura][3]=90"
        "&d[Kvadratura][4]=100"
        "&d[Kvadratura][5]=110"
        "&d[Kvadratura][6]=120"
        "&d[Terasa]=1"
        "&d[Lift]=1"
        "&d[Parking,%20garaža]=1"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return [f"❌ Greška pri konekciji sa oglasi.rs: {e}"]

    text = BeautifulSoup(resp.text, "lxml").get_text(separator="\n", strip=True)
    blocks = re.split(r"\n(?=\d{1,3}(?:\.\d{3})*,\d{2}\s*EUR\n)", text)
    results = []

    for block in blocks[1:]:
        price_match = re.search(r"([\d\.\,]+)\s*EUR", block)
        sqm_match = re.search(r"Kvadratura:\s*(\d+)", block)
        rooms_match = re.search(r"Sobnost:\s*([\w \+\-]+)", block)

        if not all([price_match, sqm_match, rooms_match]):
            continue

        price = float(price_match.group(1).replace(".", "").replace(",", "."))
        sqm = int(sqm_match.group(1))
        rooms = rooms_match.group(1)

        if price > settings["max_price"] or not (settings["min_size"] <= sqm <= 130):
            continue
        if not re.search(r"Trosoban|Troiposoban|Četvorosoban", rooms, re.IGNORECASE):
            continue

        # Najbolji naslov — linija do cene
        title = block.split(price_match.group(0))[0].strip().split("\n")[-1]
        url_full = "https://www.oglasi.rs"

        msg = f"<b>{title}</b>\nCena: {price} EUR | {sqm} m² | Sobnost: {rooms}\n<a href='{url_full}'>Otvori oglas</a>"
        results.append(msg)

    print(f"[DEBUG] Parser pronašao oglasa: {len(results)}")
    return results
