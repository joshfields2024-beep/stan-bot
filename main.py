# -*- coding: utf-8 -*-
import json
import os
import time
import html
import pathlib
from typing import Any, Dict, List
import requests

from scrapers.scraper_oglasi_rs import search_oglasi_rs

# --- KONFIG ---
TELEGRAM_BOT_TOKEN = "8203967152:AAF6d3JldWam3TphxHYrofxquzUQsf3FI2M"
TELEGRAM_CHAT_ID = "586131374"

# Parametri iz tvog linka (identični filteri)
DEFAULT_CRITERIA: Dict[str, Any] = {
    "tip": "prodaja",
    "vrsta": "stan",
    "grad": "Novi Sad",
    "min_cena": None,
    "max_cena": 180000,
    "valuta": "EUR",
    "lokacije": [
        "Grbavica",
        "Železnička stanica",
        "Sajam",
        "Rotkvarija",
        "Nova Detelinara",
        "Novo naselje",
    ],
    "sobnost": ["Trosoban", "Četvorosoban i više", "Troiposoban"],
    "kvadratura": [60, 70, 80, 90, 100, 110, 120],
    "terasa": True,
    "lift": True,
    "parking": True,
}

# Datoteka za evidenciju već poslatih oglasa (URL kao ključ)
SENT_DB_PATH = pathlib.Path("data/sent_oglasi.json")


# --- POMOĆNE ---

def _load_sent() -> set:
    try:
        if SENT_DB_PATH.exists():
            data = json.loads(SENT_DB_PATH.read_text(encoding="utf-8"))
            return set(data if isinstance(data, list) else [])
    except Exception:
        pass
    return set()


def _save_sent(urls: List[str]) -> None:
    SENT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENT_DB_PATH.write_text(json.dumps(urls, ensure_ascii=False, indent=2), encoding="utf-8")


def _fmt_msg(item: Dict[str, Any]) -> str:
    title = html.escape(item.get("title") or "Oglas")
    price = html.escape(item.get("price") or "")
    location = html.escape(item.get("location") or "")
    url = item.get("url") or ""
    parts = []
    parts.append(f"<b>{title}</b>")
    meta = " — ".join(x for x in [price, location] if x)
    if meta:
        parts.append(meta)
    if url:
        parts.append(url)
    text = "\n".join(parts)
    # Telegram limit je 4096 karaktera
    return text[:4096]


def _send_telegram(text: str) -> bool:
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(
            api,
            timeout=15,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
        )
        return r.ok
    except Exception:
        return False


# --- MAIN ---

def main() -> int:
    results = search_oglasi_rs(DEFAULT_CRITERIA)

    # Dedup po URL-u
    sent = _load_sent()
    new_items = []
    for it in results:
        url = (it.get("url") or "").strip()
        if url and url not in sent:
            new_items.append(it)

    # Pošalji samo nove
    sent_any = False
    for it in new_items:
        ok = _send_telegram(_fmt_msg(it))
        # mali razmak da ne udarimo rate limit
        time.sleep(0.4)
        if ok:
            sent.add((it.get("url") or "").strip())
            sent_any = True

    # Upis evidencije ako ima novih poslatih
    if sent_any:
        _save_sent(sorted(u for u in sent if u))

    # I za log/cron: ispiši rezime u stdout kao JSON
    summary = {
        "found": len(results),
        "new_sent": len(new_items),
        "criteria": DEFAULT_CRITERIA,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    os._exit(main())
