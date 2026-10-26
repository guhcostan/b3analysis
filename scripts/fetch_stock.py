#!/usr/bin/env python3
"""Fetch stock data (OHLCV + technicals + fundamentals) for a B3 ticker."""

import sys
import re
import json
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
from dataflows.b3_listing import get_listing_info
from dataflows.bcb_data import get_cdi_reference


def _key_metrics(ticker: str, curr_date: datetime) -> dict:
    """Price, liquidity and dividend metrics computed from raw yfinance history."""
    import yfinance as yf

    tk = yf.Ticker(ticker)
    # yfinance `end` is exclusive — add a day so the reference date is included
    end = (curr_date + timedelta(days=1)).strftime("%Y-%m-%d")
    start = (curr_date - timedelta(days=380)).strftime("%Y-%m-%d")
    hist = tk.history(start=start, end=end, auto_adjust=False)
    if hist.empty:
        return {}

    close = hist["Close"]
    last_date = hist.index[-1].date()
    divs = tk.dividends
    if len(divs):
        divs.index = divs.index.tz_localize(None)
        divs_12m = float(divs[(divs.index > curr_date - timedelta(days=365)) & (divs.index <= curr_date + timedelta(days=1))].sum())
    else:
        divs_12m = 0.0
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) > 1 else None

    return {
        "last_close": round(last, 2),
        "last_bar_date": last_date.isoformat(),
        "last_bar_may_be_intraday": last_date == datetime.today().date(),
        "prev_close": round(prev, 2) if prev else None,
        "change_pct": round((last / prev - 1) * 100, 2) if prev else None,
        "avg_daily_volume_brl_60d": round(float((hist["Close"] * hist["Volume"]).tail(60).mean())),
        "high_52w": round(float(close.tail(252).max()), 2),
        "low_52w": round(float(close.tail(252).min()), 2),
        "dividends_12m_per_share": round(divs_12m, 4),
        "dividend_yield_12m_pct": round(divs_12m / last * 100, 2) if last else None,
        "dividends_note": "trailing 12m — may include extraordinary payouts",
    }


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

    end_date = (curr_date + timedelta(days=1)).strftime("%Y-%m-%d")

    output.append(separator + "## Key Metrics\n")
    try:
        metrics = _key_metrics(ticker, curr_date)
    except Exception as e:
        metrics = {"error": str(e)}
    cdi, cdi_src = get_cdi_reference(date_str)
    metrics["cdi_ref_pct"] = cdi
    metrics["cdi_ref_source"] = cdi_src
    output.append(json.dumps(metrics, ensure_ascii=False, indent=2))

    output.append(separator + "## B3 Listing (segment / listing date / tag along)\n")
    listing = get_listing_info(ticker, date_str)
    listing["note"] = (
        "tag_along_on derived from segment: NM/N2 = 100% by rule; otherwise 80% is the "
        "legal minimum (Lei 6.404 art. 254-A) and bylaws may grant more."
    )
    output.append(json.dumps(listing, ensure_ascii=False, indent=2))

    output.append(separator + "## OHLCV (last 365 days)\n")
    output.append(get_YFin_data_online(ticker, start_date, end_date))

    # Indicator names follow stockstats (rsi = RSI 14, macds/macdh = MACD signal/histogram)
    indicators = [
        "close_50_sma", "close_200_sma", "close_10_ema",
        "macd", "macds", "macdh",
        "rsi", "boll", "boll_ub", "boll_lb",
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

    output.append(separator + "## Income Statement (annual)\n")
    output.append(get_income_statement(ticker, "annual", date_str))

    output.append(separator + "## Income Statement (quarterly)\n")
    output.append(get_income_statement(ticker, "quarterly", date_str))

    output.append(separator + "## Balance Sheet (quarterly)\n")
    output.append(get_balance_sheet(ticker, "quarterly", date_str))

    output.append(separator + "## Cash Flow (quarterly)\n")
    output.append(get_cashflow(ticker, "quarterly", date_str))

    print("\n".join(output))


if __name__ == "__main__":
    main()
