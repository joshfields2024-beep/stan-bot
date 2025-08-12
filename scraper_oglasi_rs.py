# -*- coding: utf-8 -*-
"""
Scraper za oglasi.rs BEZ browsera (requests + BeautifulSoup).
Gradi IDENTIČAN URL kao u primeru (lokacije, sobnost, kvadratura, terasa, lift, parking).
Expose-uje search_oglasi_rs(criteria) -> list[dict].
"""

from __future__ import annotations
from typing import Dict, Any, List, Iterable
import re
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup


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
    tip = criteria.get("tip", "prodaja")
    vrsta = criteria.get("vrsta", "stan")
    grad = criteria.get("grad", "")

    tip_seg = "prodaja" if tip == "prodaja" else "izdavanje"
    vrsta_seg = "prodaja-stanova" if vrsta == "stan" and tip == "prodaja" else (
        "izdavanje-stanova" if vrsta == "stan" else ("prodaja-kuca" if tip == "prodaja" else "izdavanje-kuca")
    )
    # njihov URL format za prodaju stanova je /prodaja-stanova/<grad>[/kvart+kvart...]
    city_seg = _latin_slug(grad)

    neighs: Iterable[str] = criteria.get("lokacije") or []
    neigh_seg = "+".join(_neighborhood_slug(n) for n in neighs) if neighs else ""

    base = f"https://www.oglasi.rs/nekretnine/{vrsta_seg}/{city_seg}"
    if neigh_seg:
        base += f"/{neigh_seg}"

    pr_params = {}
    if criteria.get("min_cena") is not None:
        pr_params["pr[s]"] = int(criteria["min_cena"])
    if criteria.get("max_cena") is not None:
        pr_params["pr[e]"] = int(criteria["max_cena"])
    pr_params["pr[c]"] = criteria.get("valuta", "EUR")

    d_params = {}
    if criteria.get("sobnost"):
        d_params["d[Sobnost]"] = list(criteria["sobnost"])
    if criteria.get("kvadratura"):
        d_params["d[Kvadratura]"] = [int(x) for x in criteria["kvadratura"]]
    if criteria.get("terasa"):
        d_params["d[Terasa]"] = 1
    if criteria.get("lift"):
        d_params["d[Lift]"] = 1
    if criteria.get("parking"):
        d_params["d[Parking, garaža]"] = 1

    query: Dict[str, Any] = {}
    query.update(pr_params)
    query.update(d_params)

    qs = urlencode(query, doseq=True)
    return f"{base}?{qs}" if qs else base


# ------------ HTTP / Parse ------------

_HDRS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "sr-RS,sr;q=0.9,en;q=0.8",
}

def _fetch(url: str) -> str:
    r = requests.get(url, headers=_HDRS, timeout=25)
    r.raise_for_status()
    return r.text

def _abs(base: str, href: str) -> str:
    try:
        return urljoin(base, href)
    except Exception:
        return href

def _parse_list(html: str, base_url: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")

    # probaj više “kontejnera“ za kartice
    cards = []
    # 1) generički članci/karte
    cards.extend(soup.select("article, .card, li, .oglas, .result"))
    # 2) fallback: svi linkovi ka /nekretnine/
    links_fallback = soup.select("a[href*='/nekretnine/']")
    if not cards and links_fallback:
        cards = links_fallback

    results: List[Dict[str, Any]] = []
    seen = set()

    for el in cards:
        # link
        a = el.select_one("a[href]")
        href = a.get("href") if a else None
        if not href:
            continue
        url = _abs(base_url, href)
        if "/nekretnine/" not in url:
            continue
        if url in seen:
            continue
        seen.add(url)

        # naslov
        title = ""
        for sel in ["h2", "h3", "h4", ".title", ".naslov", "strong"]:
            t = el.select_one(sel)
            if t and t.get_text(strip=True):
                title = t.get_text(strip=True)
                break

        # cena
        price = ""
        for sel in [".cena", ".price", "b", "strong", ".amount"]:
            p = el.select_one(sel)
            if p and p.get_text(strip=True):
                price = p.get_text(strip=True)
                break

        # lokacija
        location = ""
        for sel in [".lokacija", ".location", ".meta", ".detalji"]:
            l = el.select_one(sel)
            if l and l.get_text(strip=True):
                location = l.get_text(strip=True)
                break

        results.append(
            {
                "title": title,
                "price": price,
                "location": location,
                "url": url,
                "source": "oglasi.rs",
            }
        )

    return results


# ------------ Public API ------------

def search_oglasi_rs(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Vraća listu oglasa (title, price, location, url, source) na osnovu criteria.
    Radi bez browsera; robustan na manje izmene HTML-a.
    """
    url = _build_url(criteria)
    try:
        html = _fetch(url)
    except Exception as e:
        print(f"[scraper_oglasi_rs] HTTP error: {e}")
        return []
    try:
        return _parse_list(html, url)
    except Exception as e:
        print(f"[scraper_oglasi_rs] Parse error: {e}")
        return []
