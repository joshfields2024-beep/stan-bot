import requests
from bs4 import BeautifulSoup

def search_oglasi_rs(settings):
    url = ("https://www.oglasi.rs/nekretnine/prodaja-stanova/novi-sad/"
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
           "&d[Parking,%20garaža]=1")

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        return [f"❌ Greška pri konekciji sa oglasi.rs: {e}"]

    soup = BeautifulSoup(resp.text, "lxml")
    listings = soup.select("div[class*=article-body]")
    print(f"[DEBUG] Pronadjeno oglasa sa filterom: {len(listings)}")

    results = []
    for item in listings:
        title_tag = item.select_one("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Oglas"
        price = item.select_one("span.price")
        price_text = price.get_text(strip=True) if price else ""
        link_tag = item.select_one("a")
        href = link_tag["href"] if link_tag else ""
        url_full = "https://www.oglasi.rs" + href

        msg = f"<b>{title}</b>\n{price_text}\n<a href='{url_full}'>Otvori oglas</a>"
        results.append(msg)

    return results
