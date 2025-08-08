# -*- coding: utf-8 -*-
"""
Selenium scraper za oglasi.rs sa potpunom podrškom za napredne filtere.
Gradi IDENTIČAN URL kao u primeru (lokacije, sobnost, kvadratura, terasa, lift, parking).
Expose-uje search_oglasi_rs(criteria) -> list[dict].
"""

from __future__ import annotations
from typing import Dict, Any, List, Iterable
import time
import re
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


# ------------ Helperi za URL/slug ------------

_DIACRITICS = {
    "č": "c", "ć": "c", "ž": "z", "š": "s", "đ": "dj",
    "Č": "c", "Ć": "c", "Ž": "z", "Š": "s", "Đ": "dj",
}

def _latin_slug(s: str) -> str:
    s = "".join(_DIACRITICS.get(ch, ch) for ch in s)
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s\-\+]", "", s)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")

# Povoljni slugovi za kvartove ako nešto specifično traže
_NEIGHBORHOOD_SLUG_OVERRIDES = {
    "Železnička stanica": "zeleznicka-stanica",
    "Nova Detelinara": "nova-detelinara",
    "Novo naselje": "novo-naselje",
    "Grbavica": "grbavica",
    "Sajam": "sajam",
    "Rotkvarija": "rotkvarija",
}

def _neighborhood_slug(name: str) -> str:
    return _NEIGHBORHOOD_SLUG_OVERRIDES.get(name, _latin_slug(name))


# ------------ URL gradnja ------------

def _build_url(criteria: Dict[str, Any]) -> str:
    """
    Primer kriterijuma:
    {
        "tip": "prodaja" | "izdavanje",
        "vrsta": "stan" | "kuca",
        "grad": "Novi Sad",
        "min_cena": None,
        "max_cena": 180000,
        "valuta": "EUR",
        "lokacije": ["Grbavica", "Železnička stanica", ...],
        "sobnost": ["Trosoban", "Četvorosoban i više", "Troiposoban"],
        "kvadratura": [60, 70, 80, 90, 100, 110, 120],
        "terasa": True,
        "lift": True,
        "parking": True,
    }
    """

    tip = criteria.get("tip", "prodaja")
    vrsta = criteria.get("vrsta", "stan")
    grad = criteria.get("grad", "")

    # segmenti putanje
    tip_seg = "prodaja" if tip == "prodaja" else "izdavanje"
    vrsta_seg = "stanova" if vrsta == "stan" else "kuca"
    city_seg = _latin_slug(grad)

    # opcioni segment za više lokacija, spajaju se sa '+'
    neighs: Iterable[str] = criteria.get("lokacije") or []
    neigh_seg = "+".join(_neighborhood_slug(n) for n in neighs) if neighs else ""

    path = f"https://www.oglasi.rs/nekretnine/{tip_seg}-{vrsta_seg}/{city_seg}"
    if neigh_seg:
        path += f"/{neigh_seg}"

    # query parametri (koristimo doseq=True za ponavljajuće ključeve)
    pr_params = {}
    if criteria.get("min_cena") is not None:
        pr_params["pr[s]"] = int(criteria["min_cena"])
    if criteria.get("max_cena") is not None:
        pr_params["pr[e]"] = int(criteria["max_cena"])
    pr_params["pr[c]"] = criteria.get("valuta", "EUR")

    d_params = {}
    # Sobnost – više vrednosti
    if criteria.get("sobnost"):
        d_params["d[Sobnost]"] = list(criteria["sobnost"])
    # Kvadratura – više predefinisanih opsega kao u linku
    if criteria.get("kvadratura"):
        d_params["d[Kvadratura]"] = [int(x) for x in criteria["kvadratura"]]
    # Bools
    if criteria.get("terasa"):
        d_params["d[Terasa]"] = 1
    if criteria.get("lift"):
        d_params["d[Lift]"] = 1
    if criteria.get("parking"):
        # Ključ na sajtu je "Parking, garaža"
        d_params["d[Parking, garaža]"] = 1

    # spoj u jedan dict sa listama gde treba
    query: Dict[str, Any] = {}
    query.update(pr_params)
    query.update(d_params)

    qs = urlencode(query, doseq=True)
    return f"{path}?{qs}" if qs else path


# ------------ Selenium setup ------------

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


# ------------ Public API ------------

def search_oglasi_rs(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Vraća listu oglasa (title, price, location, url, source) na osnovu criteria.
    Ne ruši app na greške – vraća praznu listu i loguje problem.
    """
    url = _build_url(criteria)

    try:
        driver = _build_driver()
    except WebDriverException as e:
        print(f"[scraper_oglasi_rs] Driver init failed: {e}")
        return []

    results: List[Dict[str, Any]] = []
    try:
        driver.get(url)
        time.sleep(2.5)

        # više fallback selektora zbog promena na sajtu
        card_selectors = [
            "article[class*='oglas']",
            "div[class*='oglas']",
            "li[class*='oglas']",
            "div[class*='card']",
            "div[data-entity*='oglas']",
        ]
        cards = []
        for sel in card_selectors:
            cards = driver.find_elements(By.CSS_SELECTOR, sel)
            if len(cards) >= 5:
                break
        if not cards:
            cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/nekretnine/']")

        for el in cards[:80]:
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

            for psel in ["[class*='cena']", "[class*='price']", "strong", "b"]:
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
