# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Any, List
import re
from urllib.parse import urljoin

import requests
import backoff
from bs4 import BeautifulSoup

_HDRS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept-Language": "sr-RS,sr;q=0.9,en;q=0.8",
}

@backoff.on_exception(backoff.expo, (requests.RequestException,), max_time=60)
def _fetch(url: str) -> str:
    r = requests.get(url, headers=_HDRS, timeout=25)
    r.raise_for_status()
    return r.text

def _abs(base: str, href: str) -> str:
    try: return urljoin(base, href)
    except Exception: return href

def _parse_page(html: str, base_url: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("article, .AdCard, .ad-card, li, .card, .result")
    if not cards:
        cards = soup.select("a[href]")

    out: List[Dict[str, Any]] = []
    seen = set()

    for el in cards:
        a = el.select_one("a[href]") if el.name != "a" else el
        if not a: continue
        href = a.get("href") or ""
        url = _abs(base_url, href)
        if "4zida.rs" not in url: continue
        if any(p in url for p in ["/pretraga", "/prodaja-stanova?"]): 
            continue
        if url in seen: 
            continue
        seen.add(url)

        # title
        title = ""
        for sel in ["h3","h2","h4",".title","[data-testid='ad-title']","strong"]:
            t = el.select_one(sel) if el.name != "a" else None
            if t and t.get_text(strip=True):
                title = t.get_text(strip=True); break
        if not title:
            title = a.get_text(strip=True) or "Oglas"

        # price
        price = ""
        for sel in ["[data-testid='ad-price']", ".price", ".cena", "b", "strong", "span"]:
            p = el.select_one(sel)
            if p and "€" in p.get_text():
                price = p.get_text(strip=True); break

        # location
        location = ""
        for sel in ["[data-testid='ad-location']", ".location", ".lokacija", ".meta"]:
            l = el.select_one(sel)
            if l and l.get_text(strip=True):
                location = l.get_text(strip=True); break

        out.append({"title": title, "price": price, "location": location, "url": url, "source": "4zida"})
    return out

def _next_url(html: str, current_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    cand = soup.select_one("a[rel='next'], a.next, li.next a, .pagination a.next")
    if cand and cand.get("href"):
        return _abs(current_url, cand["href"])
    # 4zida često koristi ?stranica=2
    if "stranica=" in current_url:
        m = re.search(r"(?:[?&])stranica=(\d+)", current_url)
        if m:
            n = int(m.group(1)) + 1
            return re.sub(r"(?:[?&])stranica=\d+", f"?stranica={n}", current_url, count=1)
    sep = "&" if "?" in current_url else "?"
    return f"{current_url}{sep}stranica=2"

def search_4zida(criteria: Dict[str, Any], max_pages: int = 5) -> List[Dict[str, Any]]:
    url = criteria.get("url_4zida")
    if not url:
        return []
    out: List[Dict[str, Any]] = []
    pages = 0
    while url and pages < max_pages:
        try:
            html = _fetch(url)
            out.extend(_parse_page(html, url))
            pages += 1
            nxt = _next_url(html, url)
            if not nxt or nxt == url:
                break
            url = nxt
        except Exception as e:
            print(f"[scraper_4zida] Error: {e}")
            break
    return out
