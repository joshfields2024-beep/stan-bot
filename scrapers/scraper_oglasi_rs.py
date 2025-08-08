import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def search_oglasi_rs(settings):
    # Podesi default vrednosti ako env var ne postoje
    browser_endpoint = os.getenv("BROWSER_WEBDRIVER_ENDPOINT", "https://chrome.browserless.io/webdriver")
    browser_token = os.getenv("BROWSER_TOKEN", "OVDE_STAVI_TVOJ_TOKEN")

    if not browser_endpoint or not browser_token:
        raise RuntimeError("BROWSER_WEBDRIVER_ENDPOINT i/ili BROWSER_TOKEN nisu postavljeni i nemaju default!")

    print("[DEBUG] Pokrećem Selenium scraper preko Browserless")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Remote(
        command_executor=f"{browser_endpoint}?token={browser_token}",
        options=chrome_options
    )

    try:
        driver.get("https://www.oglasi.rs")
        # Ovde ide tvoj scraping logika
        results = driver.title  # primer
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    settings = {}
    print(search_oglasi_rs(settings))
