from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

def search_oglasi_rs(settings):
    options = Options()
    options.headless = True
    driver = Chrome(options=options)

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
    driver.get(url)
    time.sleep(5)  # da se svi oglasi učitaju

    items = driver.find_elements(By.CSS_SELECTOR, "div.article")
    print(f"[DEBUG] Selenium pronašao oglasa: {len(items)}")

    results = []
    for item in items:
        try:
            a = item.find_element(By.TAG_NAME, "a")
            href = a.get_attribute("href")
            title = a.text.strip()
            price = item.find_element(By.CSS_SELECTOR, ".price").text.strip()
        except Exception:
            continue

        results.append(f"<b>{title}</b>\n{price}\n<a href='{href}'>Otvori oglas</a>")

    driver.quit()
    return results
