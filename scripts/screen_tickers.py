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
    raw = get_YFin_data_online(ticker, start, date_str)

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
    Extracts PE ratio, D/EBITDA, segment and tag_along from fundamentals text.
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

    # tag_along and segment are not returned by yfinance — mark as unavailable
    # The LLM will flag these as ⚠️ dados insuficientes
    tag_along = None
    segment = None

    return {
        "pe_ratio": pe_ratio,
        "debt_ebitda": debt_ebitda,
        "tag_along": tag_along,
        "segment": segment,
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
        # Critério 3 — approximated from years of income statement data
        "listing_years_approx": years,
        # Critério 4 — not available via yfinance, LLM will flag as ⚠️
        "segment": fund["segment"],
        # Critério 5 — not available via yfinance, LLM will flag as ⚠️
        "tag_along": fund["tag_along"],
        # Critério 6
        "debt_ebitda": fund["debt_ebitda"],
        "net_cash": net_cash,
        # Critério 7
        "pe_ratio": pe_ratio,
        "earnings_yield": earnings_yield,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
