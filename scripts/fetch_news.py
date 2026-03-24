#!/usr/bin/env python3
"""Fetch Brazilian financial news for a given ticker (Google News PT-BR RSS)."""

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

from dataflows.google_news_br import get_news_google_br, get_sector_news_br


SECTOR_MAP = {
    "WEGE3": "industrial",
    "RENT3": "varejo",
    "RADL3": "saude",
    "FLRY3": "saude",
    "TOTS3": "tecnologia",
    "PSSA3": "financeiro",
    "ITUB3": "financeiro", "ITUB4": "financeiro",
    "BBAS3": "financeiro", "BBDC4": "financeiro",
    "BBSE3": "financeiro",
    "EQTL3": "energia", "EGIE3": "energia",
    "SAPR3": "saneamento",
    "LREN3": "varejo",
    "ABEV3": "consumo",
    "PETR4": "energia", "PETR3": "energia",
    "VALE3": "commodities",
    "SUZB3": "commodities",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_news.py TICKER [DATE] [LOOKBACK_DAYS]")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.today().strftime("%Y-%m-%d")
    _validate_ticker(ticker)
    _validate_date(date_str)
    lookback = int(sys.argv[3]) if len(sys.argv) > 3 else 14

    base_ticker = ticker.replace(".SA", "")
    sector = SECTOR_MAP.get(base_ticker)

    end_dt = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = (end_dt - timedelta(days=lookback)).strftime("%Y-%m-%d")

    separator = "\n" + "=" * 60 + "\n"

    output = [f"# News Report: {ticker} — {date_str}"]

    output.append(separator + "## Notícias da Empresa (PT-BR)\n")
    output.append(get_news_google_br(base_ticker, start_date, date_str))

    if sector:
        output.append(separator + f"## Notícias do Setor: {sector}\n")
        output.append(get_sector_news_br(sector, date_str, look_back_days=lookback))

    print("\n".join(output))


if __name__ == "__main__":
    main()
