from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

def search_oglasi_rs(settings):
    endpoint = os.getenv("BROWSER_WEBDRIVER_ENDPOINT")
    token = os.getenv("BROWSER_TOKEN")

    if not endpoint or not token:
        raise RuntimeError("Missing env vars: BROWSER_WEBDRIVER_ENDPOINT or BROWSER_TOKEN")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.set_capability("browserless:token", token)

    driver = webdriver.Remote(
        command_executor=endpoint,
        options=options
    )

    url = settings["search_url"]
    driver.get(url)
    time.sleep(5)  # može se kasnije zameniti WebDriverWait

    items = driver.find_elements(By.CSS_SELECTOR, "div.article")
    results = []
    for item in items:
        try:
            a = item.find_element(By.TAG_NAME, "a")
            title = a.text.strip()
            href = a.get_attribute("href")
            price = item.find_element(By.CSS_SELECTOR, ".price").text.strip()
            results.append(f"<b>{title}</b>\n{price}\n<a href='{href}'>Otvori oglas</a>")
        except Exception:
            continue

    driver.quit()
    return results
