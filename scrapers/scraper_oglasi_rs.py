# -*- coding: utf-8 -*-
"""
Drop-in Selenium setup za oglasi.rs.
Radi headless, bez manuelnog driver path-a (koristi webdriver-manager).
Expose-uje funkciju search_oglasi_rs(criteria) -> list[dict].
"""

from __future__ import annotations
from typing import Dict, Any, List
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def _build_driver() -> webdriver.Chrome:
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_argument("--blink-settings=imagesEnabled=false")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    driver.set_page_load_timeout(30)
    return driver


def search_oglasi_rs(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    base = "https://www.oglasi.rs/nekretnine"
    params = []

    if criteria.get("tip") == "izdavanje":
        params.append("vrsta-nekretnine=izdavanje")
    elif criteria.get("tip") == "prodaja":
        params.append("vrsta-nekretnine=prodaja")

    if criteria.get("vrsta") in {"stan", "kuca"}:
        params.append(f"tip={criteria['vrsta']}")

    if criteria.get("grad"):
        params.append(f"lokacija={criteria['grad']}")

    if criteria.get("min_cena") is not None:
        params.append(f"cena-od={criteria['min_cena']}")
    if criteria.get("max_cena") is not None:
        params.append(f"cena-do={criteria['max_cena']}")

    url = base + (("?" + "&".join(params)) if params else "")

    try:
        driver = _build_driver()
    except WebDriverException as e:
        print(f"[scraper_oglasi_rs] Driver init failed: {e}")
        return []

    results: List[Dict[str, Any]] = []
    try:
        driver.get(url)
        time.sleep(2.5)

        card_selectors = [
            "article[class*='oglas']",
            "div[class*='oglas']",
            "li[class*='oglas']",
            "div[class*='card']",
        ]
        cards = []
        for sel in card_selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if len(cards) >= 5:
                break
        if not cards:
            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/nekretnine/']")

        for el in cards[:50]:
            try:
                link_el = el.find_element(By.CSS_SELECTOR, "a[href]")
            except NoSuchElementException:
                link_el = el

            url_ad = link_el.get_attribute("href") or ""
            title = ""
            price = ""
            location = ""

            for tsel in ["h2", "h3", "h4", "[class*='title']"]:
                try:
                    title = el.find_element(By.CSS_SELECTOR, tsel).text.strip()
                    if title:
                        break
                except NoSuchElementException:
                    continue

            for psel in ["[class*='cena']", "[class*='price']", "strong"]:
                try:
                    price = el.find_element(By.CSS_SELECTOR, psel).text.strip()
                    if price:
                        break
                except NoSuchElementException:
                    continue

            for lsel in ["[class*='lokacija']", "[class*='location']"]:
                try:
                    location = el.find_element(By.CSS_SELECTOR, lsel).text.strip()
                    if location:
                        break
                except NoSuchElementException:
                    continue

            if url_ad or title or price:
                results.append(
                    {
                        "title": title,
                        "price": price,
                        "location": location,
                        "url": url_ad,
                        "source": "oglasi.rs",
                    }
                )

    except (TimeoutException, WebDriverException) as e:
        print(f"[scraper_oglasi_rs] Page error: {e}")
        results = []
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return results
