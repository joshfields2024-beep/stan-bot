# -*- coding: utf-8 -*-
import argparse
import json
import sys
from typing import Any, Dict

from scrapers.scraper_oglasi_rs import search_oglasi_rs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scraper za oglasi.rs – vraća JSON listu rezultata."
    )
    p.add_argument("--tip", choices=["prodaja", "izdavanje"], required=True, help="Tip oglasa")
    p.add_argument("--vrsta", choices=["stan", "kuca"], required=True, help="Vrsta nekretnine")
    p.add_argument("--grad", type=str, required=True, help="Grad/lokacija (npr. Beograd)")
    p.add_argument("--min-cena", type=int, default=None, help="Minimalna cena")
    p.add_argument("--max-cena", type=int, default=None, help="Maksimalna cena")
    p.add_argument("--limit", type=int, default=0, help="Opcioni limit rezultata (>0)")
    return p.parse_args()


def build_criteria(ns: argparse.Namespace) -> Dict[str, Any]:
    return {
        "tip": ns.tip,
        "vrsta": ns.vrsta,
        "grad": ns.grad,
        "min_cena": ns.min_cena,
        "max_cena": ns.max_cena,
    }


def main() -> int:
    try:
        ns = parse_args()
        criteria = build_criteria(ns)
        results = search_oglasi_rs(criteria)

        if ns.limit and ns.limit > 0:
            results = results[: ns.limit]

        # samo JSON na stdout – pogodno za pipe/cron
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    except Exception as e:
        print(f"[main] Error: {e}", file=sys.stderr)
        # ne rušimo pipeline – vraćamo praznu listu
        print("[]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
