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
CHECK_INTERVAL_MINUTES = 10  # koliko minuta između provera novih

# Kriterijumi (identični tvom linku)
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

SENT_DB_PATH = pathlib.Path("data/sent_oglasi.json")


# --- FUNKCIJE ---

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
    parts = [f"<b>{title}</b>"]
    meta = " — ".join(x for x in [price, location] if x)
    if meta:
        parts.append(meta)
    if url:
        parts.append(url)
    return "\n".join(parts)[:4096]


def _send_telegram(text: str) -> bool:
    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(api, timeout=15, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
        return r.ok
    except Exception:
        return False


def _send_ads(ads: List[Dict[str, Any]], sent_urls: set) -> int:
    """Šalje oglase na Telegram i vraća broj uspešno poslatih."""
    sent_count = 0
    for it in ads:
        msg = _fmt_msg(it)
        ok = _send_telegram(msg)
        print(f"  -> Slanje oglasa '{it.get('title')}' : {'OK' if ok else 'FAIL'}")
        if ok:
            sent_urls.add((it.get("url") or "").strip())
            sent_count += 1
        time.sleep(0.5)  # sprečava rate limit
    return sent_count


def _full_initial_run():
    """Prva pretraga – šalje sve oglase koji ispunjavaju kriterijume."""
    print("[INIT] Pokrećem početnu pretragu svih oglasa...")
    results = search_oglasi_rs(DEFAULT_CRITERIA)
    print(f"[INIT] Pronađeno {len(results)} oglasa.")

    sent_urls = set()
    sent_count = _send_ads(results, sent_urls)

    _save_sent(sorted(u for u in sent_urls if u))
    print(f"[INIT] Poslato {sent_count} oglasa. Evidencija zapisana.\n")


def _check_new():
    """Proverava samo nove oglase i šalje ih."""
    results = search_oglasi_rs(DEFAULT_CRITERIA)
    print(f"[CHECK] Pronađeno ukupno oglasa: {len(results)}")

    sent_urls = _load_sent()
    new_items = [it for it in results if (it.get("url") or "").strip() not in sent_urls]
    print(f"[CHECK] Novi oglasi: {len(new_items)}")

    if new_items:
        sent_count = _send_ads(new_items, sent_urls)
        _save_sent(sorted(u for u in sent_urls if u))
        print(f"[CHECK] Poslato {sent_count} novih oglasa.\n")
    else:
        print("[CHECK] Nema novih oglasa.\n")


# --- MAIN LOOP ---

def main():
    # Prvo punjenje – šalje sve oglase
    _full_initial_run()

    # Loop za proveru novih oglasa
    print(f"[LOOP] Ulazim u režim provere svakih {CHECK_INTERVAL_MINUTES} minuta.\n")
    while True:
        try:
            _check_new()
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
