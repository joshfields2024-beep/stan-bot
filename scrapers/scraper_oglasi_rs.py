import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def search_oglasi_rs(settings):
    endpoint = os.getenv("BROWSER_WEBDRIVER_ENDPOINT", "https://production-sfo.browserless.io/webdriver")
    token = os.getenv("BROWSER_TOKEN")

    if not token:
        raise RuntimeError("BROWSER_TOKEN nije postavljen u Railway Variables.")

    remote_url = f"{endpoint}?token={token}"
    print("[DEBUG] Pokrećem Selenium scraper preko Browserless:", remote_url)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)
    try:
        driver.get("https://www.oglasi.rs")
        return driver.title  # primer; ovde ide tvoja logika
    finally:
        driver.quit()
