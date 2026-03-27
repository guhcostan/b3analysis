#!/usr/bin/env python3
"""Fetch and pre-process key financial metrics for a B3 ticker."""

import sys
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yfinance as yf

from dataflows.y_finance import (
    get_fundamentals,
    get_income_statement,
)

def _validate_ticker(ticker):
    if not re.match(r'^[A-Z]{4}\d{1,2}(\.SA)?$', ticker):
        sys.exit(1)

def _validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        sys.exit(1)

def parse_income_statement(raw):
    """Extrai valores de Net Income do CSV retornado por get_income_statement."""
    earnings = []
    for line in raw.split("\n"):
        if line.startswith("Net Income,"):
            try:
                values = [float(v) for v in line.split(",")[1:] if v.strip()]
                earnings.extend(values)
            except:
                pass
    return earnings[-5:]  # últimos anos

def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    ticker = sys.argv[1].upper()
    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m-%d")

    _validate_ticker(ticker)
    _validate_date(date_str)

    fundamentals = get_fundamentals(ticker, date_str)
    income = get_income_statement(ticker, "yearly", date_str)

    # ===== EXTRAÇÃO (ajustar conforme formato real) =====
    earnings = parse_income_statement(income)

    # Flags simples (ajuste parsing conforme retorno real)
    is_on = ticker.replace(".SA", "").endswith("3")

    # extrair campos estruturados direto do yfinance info
    info = yf.Ticker(ticker).info or {}
    avg_volume = info.get("averageVolume", 0)
    segment = info.get("exchange", "")
    tag_along = 0  # não disponível via yfinance
    total_debt = info.get("totalDebt") or 0
    ebitda = info.get("ebitda") or 0
    debt_ebitda = round(total_debt / ebitda, 2) if ebitda != 0 else None
    net_cash = (info.get("totalCash") or 0) > total_debt
    pe = info.get("trailingPE")

    earnings_yield = (1 / pe) if pe and pe != 0 else None

    has_loss = any(e < 0 for e in earnings)

    result = {
        "ticker": ticker.replace(".SA", ""),
        "years_of_data": len(earnings),
        "earnings": earnings,
        "has_loss": has_loss,
        "is_on": is_on,
        "avg_volume": avg_volume,
        "segment": segment,
        "tag_along": tag_along,
        "debt_ebitda": debt_ebitda,
        "net_cash": net_cash,
        "pe_ttm": pe,
        "earnings_yield": earnings_yield,
    }

    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
