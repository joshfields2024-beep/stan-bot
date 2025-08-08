import os
from playwright.sync_api import sync_playwright

def search_oglasi_rs(settings):
    ws_endpoint = os.getenv("BROWSERLESS_WS_ENDPOINT", "wss://production-sfo.browserless.io")
    token = os.getenv("BROWSER_TOKEN")
    if not token:
        raise RuntimeError("BROWSER_TOKEN nije postavljen.")

    ws_url = f"{ws_endpoint}?token={token}"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        try:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto("https://www.oglasi.rs", wait_until="domcontentloaded", timeout=60000)

            # >>> OVDE TVOJA SCRAPE LOGIKA <<<
            title = page.title()

            return {"title": title}
        finally:
            browser.close()
