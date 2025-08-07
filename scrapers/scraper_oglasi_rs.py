from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time

def search_oglasi_rs(settings):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.set_capability("browserless:token", os.environ["BROWSER_TOKEN"])
    driver = webdriver.Remote(
        command_executor=os.environ["BROWSER_WEBDRIVER_ENDPOINT"],
        options=options
    )
    url = settings["search_url"]
    driver.get(url)
    time.sleep(5)
    items = driver.find_elements("css selector", "div.article")
    results = []
    for item in items:
        try:
            a = item.find_element("tag name", "a")
            title = a.text.strip()
            href = a.get_attribute("href")
            price = item.find_element("css selector", ".price").text.strip()
            results.append(f"<b>{title}</b>\n{price}\n<a href='{href}'>Otvori oglas</a>")
        except:
            continue
    driver.quit()
    return results
