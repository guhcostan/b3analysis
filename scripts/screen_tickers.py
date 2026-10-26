#!/usr/bin/env python3
"""
Fetch and precompute screening metrics for the 7 Logan criteria.
Returns compact JSON — no OHLCV, no technical indicators.

Usage: screen_tickers.py TICKER [DATE]
"""

import sys
import re
import json
import io
import csv
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _validate_ticker(ticker):
    if not re.match(r'^[A-Z]{4}\d{1,2}(\.SA)?$', ticker):
        print(f"Erro: ticker '{ticker}' inválido. Formato: WEGE3 ou WEGE3.SA", file=sys.stderr)
        sys.exit(1)


def _validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(f"Erro: data '{date_str}' inválida. Formato: YYYY-MM-DD", file=sys.stderr)
        sys.exit(1)


from dataflows.y_finance import (
    get_fundamentals,
    get_balance_sheet,
    get_income_statement,
    get_YFin_data_online,
)
from dataflows.b3_listing import get_listing_info
from dataflows.bcb_data import get_cdi_reference


def _parse_csv(raw: str) -> dict[str, list]:
    """
    Parse CSV output from dataflows (format: metric,year1,year2,...).
    Skips comment lines starting with '#'.
    Returns dict: {metric_name: [val_year1, val_year2, ...]}
    """
    lines = [l for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    reader = csv.reader(io.StringIO("\n".join(lines)))
    result = {}
    for row in reader:
        if len(row) < 2:
            continue
        key = row[0].strip()
        values = []
        for v in row[1:]:
            v = v.strip()
            try:
                values.append(float(v) if v else None)
            except ValueError:
                values.append(None)
        result[key] = values
    return result


def _parse_kv(raw: str) -> dict[str, str]:
    """
    Parse key: value text output from get_fundamentals.
    Skips comment lines starting with '#'.
    """
    result = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _extract_earnings_history(ticker: str, date_str: str) -> tuple[list, bool, int]:
    """
    Returns (earnings_list, has_recurring_loss, years_of_data).
    earnings_list: annual net income values, newest first (as returned by yfinance).
    has_recurring_loss: True if 2+ years with negative net income.
    """
    raw = get_income_statement(ticker, "annual", date_str)
    data = _parse_csv(raw)

    net_income = None
    for key in data:
        if key.lower() == "net income":
            net_income = data[key]
            break

    if net_income is None:
        return [], False, 0

    earnings = [v for v in net_income if v is not None]
    if not earnings:
        return [], False, 0

    years = len(earnings)
    losses = sum(1 for e in earnings if e < 0)
    has_recurring_loss = losses >= 2

    return earnings, has_recurring_loss, years


def _extract_volume_and_price(ticker: str, date_str: str) -> tuple[float, float]:
    """
    Returns (avg_daily_volume_brl, last_close_price).
    OHLCV format: Date,Open,High,Low,Close,Volume,... (row per day).
    Uses 90-day window — minimum needed to compute avg volume.
    """
    end = datetime.strptime(date_str, "%Y-%m-%d")
    start = (end - timedelta(days=90)).strftime("%Y-%m-%d")
    # yfinance `end` is exclusive — add a day so the reference date is included
    raw = get_YFin_data_online(ticker, start, (end + timedelta(days=1)).strftime("%Y-%m-%d"))

    lines = [l for l in raw.splitlines() if l.strip() and not l.startswith("#")]
    if not lines:
        return 0.0, 0.0

    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    rows = list(reader)
    if not rows:
        return 0.0, 0.0

    close_key = next((k for k in rows[0] if "close" in k.lower()), None)
    volume_key = next((k for k in rows[0] if "volume" in k.lower()), None)

    if not close_key or not volume_key:
        return 0.0, 0.0

    closes = []
    volumes = []
    for row in rows:
        try:
            closes.append(float(row[close_key]))
            volumes.append(float(row[volume_key]))
        except (ValueError, TypeError):
            continue

    if not closes or not volumes:
        return 0.0, 0.0

    last_close = closes[-1]
    avg_vol_brl = (sum(volumes) / len(volumes)) * last_close
    return avg_vol_brl, last_close


def _extract_fundamentals(ticker: str, date_str: str) -> dict:
    """
    Extracts PE ratio and D/EBITDA from fundamentals text.
    """
    raw = get_fundamentals(ticker, date_str)
    kv = _parse_kv(raw)

    pe_ratio = None
    for key in kv:
        if "pe ratio" in key.lower() or "p/e" in key.lower():
            try:
                pe_ratio = float(kv[key])
            except ValueError:
                pass
            break

    debt_ebitda = None
    for key in kv:
        # Match "D/EBITDA (calculado)" — avoid "Debt to Equity (D/E — não é D/EBITDA)"
        if key.lower().startswith("d/ebitda"):
            try:
                debt_ebitda = float(kv[key])
            except ValueError:
                pass
            break

    return {
        "pe_ratio": pe_ratio,
        "debt_ebitda": debt_ebitda,
    }


def _extract_net_cash(ticker: str, date_str: str) -> bool:
    """
    Returns True if most recent quarter shows cash > total debt.
    """
    raw = get_balance_sheet(ticker, "quarterly", date_str)
    data = _parse_csv(raw)

    cash_key = next(
        (k for k in data if "cash" in k.lower() and "equivalent" in k.lower()), None
    )
    debt_key = next(
        (k for k in data if k.lower() in ("total debt", "long term debt")), None
    )

    if not cash_key or not debt_key:
        return False

    cash_vals = [v for v in data[cash_key] if v is not None]
    debt_vals = [v for v in data[debt_key] if v is not None]

    if not cash_vals or not debt_vals:
        return False

    return cash_vals[0] > debt_vals[0]


def main():
    if len(sys.argv) < 2:
        print("Usage: screen_tickers.py TICKER [DATE]")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m-%d")
    _validate_ticker(ticker)
    _validate_date(date_str)

    ticker_clean = ticker.replace(".SA", "")
    last_digit = ticker_clean[-1]
    ticker_type = "ON" if last_digit == "3" else ("PN" if last_digit == "4" else "Unit/Other")

    # Critério 1 — escadinha de lucros
    earnings, has_recurring_loss, years = _extract_earnings_history(ticker, date_str)

    # Critério 2 — ON com liquidez
    avg_volume_brl, last_close = _extract_volume_and_price(ticker, date_str)

    # Critérios 4, 5, 6 (parcial), 7
    fund = _extract_fundamentals(ticker, date_str)
    pe_ratio = fund["pe_ratio"]
    earnings_yield = round(1.0 / pe_ratio, 4) if pe_ratio and pe_ratio > 0 else None

    # Critério 6 — net cash
    net_cash = _extract_net_cash(ticker, date_str)

    # Critérios 3, 4, 5 — B3 listed-companies API
    listing = get_listing_info(ticker, date_str)

    # Critério 7 — hurdle rate
    cdi_ref, cdi_source = get_cdi_reference(date_str)

    result = {
        "ticker": ticker_clean,
        "date": date_str,
        # Critério 1
        "earnings_history": earnings,
        "has_recurring_loss": has_recurring_loss,
        "years_of_data": years,
        # Critério 2
        "ticker_type": ticker_type,
        "avg_daily_volume_brl": round(avg_volume_brl),
        "last_close": last_close,
        # Critério 3 — years since B3 listing date (yfinance only has ~4 annual periods)
        "listing_date": listing["listing_date"],
        "listing_years_approx": listing["listing_years"],
        # Critério 4
        "segment": listing["segment"],
        # Critério 5 — derived from segment (NM/N2 = 100; else 80 = legal minimum)
        "tag_along": listing["tag_along_on"],
        "tag_along_source": listing["tag_along_source"],
        "b3_found": listing["b3_found"],
        # Critério 6
        "debt_ebitda": fund["debt_ebitda"],
        "net_cash": net_cash,
        # Critério 7
        "pe_ratio": pe_ratio,
        "earnings_yield": earnings_yield,
        "cdi_ref": round(cdi_ref / 100, 4) if cdi_ref is not None else None,
        "cdi_source": cdi_source,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
