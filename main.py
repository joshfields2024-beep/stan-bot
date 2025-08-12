# -*- coding: utf-8 -*-
import json, os, time, html, pathlib, argparse
from typing import Any, Dict, List
from dotenv import load_dotenv
import requests

from scrapers import aggregate
from utils.filters import should_skip

load_dotenv()

SENT_DB_PATH = pathlib.Path("data/sent_oglasi.json")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))

def _load_cfg() -> Dict[str, str]:
    token = os.getenv("8203967152:AAF6d3JldWam3TphxHYrofxquzUQsf3FI2M")
    chat_id = os.getenv("586131374")
    if token and chat_id:
        return {"token": token, "chat_id": chat_id}
    with open("settings.json", "r", encoding="utf-8") as f:
        s = json.load(f)
        return {"token": s["telegram_bot_token"], "chat_id": s["telegram_chat_id"]}

DEFAULT_CRITERIA: Dict[str, Any] = {
    # koristi postojeće parametre za oglasi.rs
    "tip": "prodaja",
    "vrsta": "stan",
    "grad": "Novi Sad",
    "min_cena": None,
    "max_cena": 180000,
    "valuta": "EUR",
    "lokacije": ["Grbavica","Železnička stanica","Sajam","Rotkvarija","Nova Detelinara","Novo naselje"],
    "sobnost": ["Trosoban","Četvorosoban i više","Troiposoban"],
    "kvadratura": [60,70,80,90,100,110,120],
    "terasa": True, "lift": True, "parking": True,

    # direktno zadate pretrage za nova 2 sajta
    "url_4zida": "https://www.4zida.rs/prodaja-stanova/nova-detelinara-detelinara-gradske-lokacije-novi-sad/trosoban/do-180000-evra?mesto=novo-naselje-gradske-lokacije-novi-sad&mesto=sajam-savski-venac-beograd&mesto=sajmiste-gradske-lokacije-novi-sad&mesto=banatic-gradske-lokacije-novi-sad&mesto=zeleznicka-stanica-banatic-gradske-lokacije-novi-sad&mesto=grbavica-gradske-lokacije-novi-sad&mesto=rotkvarija-gradske-lokacije-novi-sad&mesto=socijalno-rotkvarija-gradske-lokacije-novi-sad&struktura=troiposoban&struktura=cetvorosoban&struktura=cetvoroiposoban-i-vise&tip=stan-u-zgradi&lift=da&vece_od=60m2&prizemlje=ne&sa_parkingom=da&uknjizeno=da&terasa=da",
    "url_nekretnine": "https://www.nekretnine.rs/stambeni-objekti/stanovi/izdavanje-prodaja/prodaja/deo-grada/adamovicevo-naselje_banatic_detelinara-nova_grbavica_novo-naselje_rotkvarija_sajam_socijalno_zeleznicka-stanica/grad/novi-sad/prateci-objekti-povrsine/terasa_spoljno-parking-mesto_lift/kvadratura/60_1000000/cena/1_180000/lista/po-stranici/10/",
}

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
    if meta: parts.append(meta)
    if url: parts.append(url)
    return "\n".join(parts)[:4096]

def _send_telegram(cfg: Dict[str, str], text: str) -> bool:
    api = f"https://api.telegram.org/bot{cfg['token']}/sendMessage"
    try:
        r = requests.post(api, timeout=15, data={
            "chat_id": cfg["chat_id"],
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
        return r.ok
    except Exception:
        return False

def _send_ads(cfg: Dict[str, str], ads: List[Dict[str, Any]], sent_urls: set) -> int:
    sent = 0
    for it in ads:
        msg = _fmt_msg(it)
        ok = _send_telegram(cfg, msg)
        print(f"  -> Slanje '{it.get('title')}' : {'OK' if ok else 'FAIL'}")
        if ok:
            sent_urls.add((it.get("url") or "").strip())
            sent += 1
        time.sleep(0.5)
    return sent

def _run_once(cfg: Dict[str, str], initial: bool):
    results = aggregate(DEFAULT_CRITERIA)
    # filter jednosoban/dvosoban
    results = [it for it in results if not should_skip(it)]
    print(f"[RUN] Posle agregacije i filtera: {len(results)}")

    sent_urls = _load_sent()
    if initial:
        new_items = [it for it in results if (it.get("url") or "").strip() not in sent_urls]
    else:
        new_items = [it for it in results if (it.get("url") or "").strip() not in sent_urls]
    if not new_items:
        print("[RUN] Nema novih.")
        return
    sent = _send_ads(cfg, new_items, sent_urls)
    _save_sent(sorted(u for u in sent_urls if u))
    print(f"[RUN] Poslato: {sent}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Jedna iteracija i izlaz")
    parser.add_argument("--no-initial", action="store_true", help="Ne šalji sve odmah")
    args = parser.parse_args()

    cfg = _load_cfg()

    if not args.no_initial:
        print("[INIT] Start sa punim slanjem.")
        _run_once(cfg, initial=True)

    if args.once:
        return

    print(f"[LOOP] Provera na {CHECK_INTERVAL_MINUTES} min.")
    while True:
        try:
            _run_once(cfg, initial=False)
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
