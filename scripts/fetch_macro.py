#!/usr/bin/env python3
"""Fetch Brazilian macroeconomic indicators and macro news."""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dataflows.bcb_data import get_bcb_macro_indicators, get_bcb_selic_history
from dataflows.google_news_br import get_macro_news_br


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.today().strftime("%Y-%m-%d")

    separator = "\n" + "=" * 60 + "\n"

    output = [f"# Macro Snapshot Brasil — {date_str}"]

    output.append(separator + "## Indicadores BCB (Banco Central do Brasil)\n")
    output.append(get_bcb_macro_indicators(date_str))

    output.append(separator + "## Histórico Meta Selic (Copom)\n")
    output.append(get_bcb_selic_history(date_str))

    output.append(separator + "## Notícias Macro Brasil (PT-BR)\n")
    output.append(get_macro_news_br(date_str, look_back_days=14))

    print("\n".join(output))


if __name__ == "__main__":
    main()
