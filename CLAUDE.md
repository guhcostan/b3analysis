# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

`run.sh` is a venv-aware Python runner, not a setup script. It bootstraps `.venv` on first use and then executes any Python script inside it:

```bash
bash run.sh scripts/fetch_stock.py WEGE3.SA 2026-03-24
bash run.sh scripts/fetch_macro.py 2026-03-24
bash run.sh scripts/fetch_news.py WEGE3.SA 2026-03-24 14
```

Always invoke scripts via `run.sh` from the workspace root — never activate the venv manually.

## Commands

| Command | Usage | Description |
|---|---|---|
| `/analyze` | `/analyze WEGE3.SA [2026-03-24]` | Full single-stock analysis |
| `/portfolio` | `/portfolio elite 10000` | Diversified portfolio builder |
| `/macro` | `/macro` | BR macroeconomic snapshot |
| `/b3profile` | `/b3profile quality` | Switch analysis model profile |

## Architecture

### Data flow

```
.claude/commands/        ← slash command definitions (multi-agent orchestration)
    analyze.md           → spawns 3 parallel Task agents (stock + macro + news)
    portfolio.md         → spawns N+1 parallel Task agents (1 per ticker + macro)
    macro.md             → runs fetch_macro.py, produces report
scripts/
    fetch_stock.py       → calls dataflows/y_finance.py + stockstats_utils.py
    fetch_macro.py       → calls dataflows/bcb_data.py + google_news_br.py
    fetch_news.py        → calls dataflows/google_news_br.py
dataflows/
    y_finance.py         → OHLCV, fundamentals, technicals via yfinance
    bcb_data.py          → Selic/CDI/IPCA/BRL-USD from BCB API (no key needed)
    google_news_br.py    → PT-BR news via Google News RSS (no key needed)
    stockstats_utils.py  → RSI, MACD, Bollinger, SMA, ADX, ATR via stockstats
    config.py            → cache path config (dataflows/data_cache/)
```

### Multi-agent execution

`/analyze` and `/portfolio` use Claude's Task tool to spawn parallel subagents. Each data agent runs a script and returns raw output. The main session synthesizes all results into a Portuguese report. Model assignment per agent type is controlled by the active profile.

### Profile state

Two files must stay in sync when changing profiles:

- `.b3profile` — stores the profile name (`quality` / `balanced` / `budget`)
- `.claude/settings.json` — stores `{ "model": "..." }` for the synthesis (main) model

The `/b3profile` command updates both atomically.

## Analysis profiles

| Profile | Synthesis (main) | Ticker agents | Macro agent |
|---|---|---|---|
| `quality` | claude-opus-4-6 | claude-opus-4-6 | claude-sonnet-4-6 |
| `balanced` | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 |
| `budget` | claude-sonnet-4-6 | claude-haiku-4-5 | claude-haiku-4-5 |

Default is `balanced`. For real investment decisions use `quality` + `/effort high`.

## Preset tickers

| Preset | Tickers |
|---|---|
| `elite` | WEGE3, ITUB3, BBAS3, RADL3, LREN3, EQTL3, RENT3, PSSA3, FLRY3, TOTS3 |
| `elite-plus` | Elite + BBSE3, SAPR3 |
| `blue-chips` | PETR4, VALE3, ITUB4, BBDC4, ABEV3, WEGE3, RENT3, SUZB3, EQTL3, BBAS3 |

## B3 Quality Checklist

Criteria 1, 2, and 3 are **eliminatory** — fail any = automatic AVOID.

| # | Criterion | Eliminatory |
|---|---|---|
| 1 | Consistent growing profits (escadinha, no recurring losses) | ✅ Yes |
| 2 | Liquid ON shares (ticker ending in 3, vol > R$10M/day) | ✅ Yes |
| 3 | No recent IPO (5+ years of profit history on B3) | ✅ Yes |
| 4 | Novo Mercado listing | Partial |
| 5 | Tag Along 100% | Partial |
| 6 | Controlled debt (net cash or D/EBITDA < 2x) | Partial |
| 7 | Expected return > CDI (~14.75% a.a.) | Partial |

Score 6–7 = Strong Buy / Elite. Score ≤ 2 = Exclude from portfolio.

### Red flags
- Ticker ending in 4/11 with no ON liquidity
- Controlling shareholder holds only ON, forces investors into PN
- Tag Along < 100%
- Heavy state interference (pricing / dividend policy risk)
- D/EBITDA > 3x

## Macro context

- **Selic meta**: ~14,75% a.a. (tightening cycle, 2025–2026)
- **CDI** ≈ Selic − 0.10% a.a. — minimum return benchmark for equities
- High Selic: favors insurance (float income), exporters (USD revenue); hurts retail, utilities, high-growth tech
- BRL/USD: strong USD = positive for exporters, negative for importers

## Report language

All analysis reports must be written in **Portuguese (Brazil)**. Only code, scripts, and this file are in English.
