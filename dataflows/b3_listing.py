"""B3 listed-companies API: listing segment, listing date and derived tag along."""

import base64
import json
import os
import sys
import time
from datetime import datetime
from typing import Optional

import requests

from .config import get_config


_B3_URL = (
    "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/"
    "CompanyCall/GetInitialCompanies/{payload}"
)
_CACHE_TTL_HOURS = 24 * 7

SEGMENT_NAMES = {
    "NM": "Novo Mercado",
    "N2": "Nível 2",
    "N1": "Nível 1",
    "MA": "Bovespa Mais",
    "M2": "Bovespa Mais Nível 2",
    "MB": "Balcão Organizado",
    "": "Tradicional",
}

# Minimum tag along for ON shares implied by the listing segment.
# NM / N2 / Bovespa Mais rules require 100%; otherwise Lei 6.404 art. 254-A
# guarantees 80% to ON holders. A company's bylaws may grant more than the
# minimum — callers should treat non-100 values as "legal minimum".
_TAG_ALONG_ON = {"NM": 100, "N2": 100, "MA": 100, "M2": 100}
_TAG_ALONG_LEGAL_MIN = 80


def _cache_path(issuer: str) -> str:
    cache_dir = os.path.join(get_config()["data_cache_dir"], "b3_listing")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{issuer}.json")


def _fetch_issuer(issuer: str) -> Optional[dict]:
    path = _cache_path(issuer)
    if os.path.exists(path) and (time.time() - os.path.getmtime(path)) / 3600 < _CACHE_TTL_HOURS:
        with open(path) as f:
            return json.load(f)

    payload = base64.b64encode(json.dumps({
        "language": "pt-br", "pageNumber": 1, "pageSize": 20, "company": issuer,
    }).encode()).decode()
    try:
        resp = requests.get(_B3_URL.format(payload=payload), timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print(f"[B3] Aviso: falha ao buscar dados de listagem de {issuer}: {e}", file=sys.stderr)
        return None

    match = next((r for r in results if r.get("issuingCompany") == issuer), None)
    if match is not None:
        with open(path, "w") as f:
            json.dump(match, f, ensure_ascii=False)
    return match


def get_listing_info(ticker: str, ref_date: Optional[str] = None) -> dict:
    """
    Returns listing info for a B3 ticker (e.g. WEGE3 or WEGE3.SA):
    segment code/name, listing date, years listed, and tag along for ON shares.
    Fields are None when the B3 API has no record (delisted, renamed, BDR...).
    """
    issuer = ticker.upper().replace(".SA", "")[:4]
    info = {
        "segment_code": None,
        "segment": None,
        "listing_date": None,
        "listing_years": None,
        "tag_along_on": None,
        "tag_along_source": None,
        "b3_found": False,
    }

    data = _fetch_issuer(issuer)
    if not data:
        return info

    code = (data.get("market") or "").strip()
    info["b3_found"] = True
    info["segment_code"] = code
    info["segment"] = SEGMENT_NAMES.get(code, code)

    listing = data.get("dateListing")
    if listing and not listing.startswith("31/12/9999"):
        listed = datetime.strptime(listing, "%d/%m/%Y")
        ref = datetime.strptime(ref_date, "%Y-%m-%d") if ref_date else datetime.today()
        info["listing_date"] = listed.strftime("%Y-%m-%d")
        info["listing_years"] = round((ref - listed).days / 365.25, 1)

    if code.startswith("DR"):
        return info  # BDR — tag along rules don't apply

    if code in _TAG_ALONG_ON:
        info["tag_along_on"] = _TAG_ALONG_ON[code]
        info["tag_along_source"] = "segment_rule"
    else:
        info["tag_along_on"] = _TAG_ALONG_LEGAL_MIN
        info["tag_along_source"] = "legal_minimum"

    return info
