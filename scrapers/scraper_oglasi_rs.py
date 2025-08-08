import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def search_oglasi_rs(settings):
    # Preuzmi env var ili koristi default
    browser_endpoint = os.getenv("BROWSER_WEBDRIVER_ENDPOINT", "https://chrome.browserless.io/webdriver")
    browser_token = os.getenv("BROWSER_TOKEN", "")

    if not browser_token:
        raise RuntimeError("BROWSER_TOKEN nije postavljen! Generiši ga na https://www.browserless.io i dodaj u Railway Variables.")

    print("[DEBUG] Pokrećem Selenium scraper preko Browserless")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Ispravno sklapanje URL-a
    remote_url = f"{browser_endpoint}?token={browser_token}"

    driver = webdriver.Remote(
        command_executor=remote_url,
        options=chrome_options
    )

    try:
        driver.get("https://www.oglasi.rs")
        # Ovde ide tvoja scraping logika
        results = driver.title  # primer
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    settings = {}
    print(search_oglasi_rs(settings))
