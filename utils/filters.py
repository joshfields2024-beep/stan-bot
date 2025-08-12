# -*- coding: utf-8 -*-
import re
from typing import Dict

_SKIP_PATTERNS = [
    r"\bgarsonjer(a|u)?\b",
    r"\bstud(io|ijo)\b",
    r"\bjednosobn\w*\b",
    r"\bjednoiposobn\w*\b",
    r"\bdvosobn\w*\b",
    r"\bdvoiposobn\w*\b",
    r"\b1\.0\b", r"\b1\.5\b", r"\b2\.0\b", r"\b2\.5\b",
]
_SKIP_RE = re.compile("|".join(_SKIP_PATTERNS), flags=re.IGNORECASE | re.UNICODE)

def should_skip(item: Dict) -> bool:
    title = (item.get("title") or "").strip()
    return bool(_SKIP_RE.search(title))
