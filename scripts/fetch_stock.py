#!/usr/bin/env python3
"""Fetch stock data (OHLCV + technicals + fundamentals) for a B3 ticker."""

import sys
import re
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
    get_YFin_data_online,
    get_stock_stats_indicators_window,
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
)


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_stock.py TICKER [DATE]")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m-%d")
    _validate_ticker(ticker)
    _validate_date(date_str)
    curr_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = (curr_date - timedelta(days=365)).strftime("%Y-%m-%d")

    separator = "\n" + "=" * 60 + "\n"

    output = [f"# Stock Report: {ticker} — {date_str}"]

    output.append(separator + "## OHLCV (last 365 days)\n")
    output.append(get_YFin_data_online(ticker, start_date, date_str))

    indicators = [
        "close_50_sma", "close_200_sma", "close_10_ema",
        "macd", "macd_signal", "macd_hist",
        "rsi_14", "boll", "boll_ub", "boll_lb",
        "atr", "adx",
    ]
    output.append(separator + "## Technical Indicators\n")
    for ind in indicators:
        try:
            result = get_stock_stats_indicators_window(ticker, ind, date_str, 90)
            output.append(f"### {ind.upper()}\n{result}\n")
        except Exception as e:
            output.append(f"### {ind.upper()}\nError: {e}\n")

    output.append(separator + "## Fundamentals\n")
    output.append(get_fundamentals(ticker, date_str))

    output.append(separator + "## Income Statement (quarterly)\n")
    output.append(get_income_statement(ticker, "quarterly", date_str))

    output.append(separator + "## Balance Sheet (quarterly)\n")
    output.append(get_balance_sheet(ticker, "quarterly", date_str))

    output.append(separator + "## Cash Flow (quarterly)\n")
    output.append(get_cashflow(ticker, "quarterly", date_str))

    print("\n".join(output))


if __name__ == "__main__":
    main()
