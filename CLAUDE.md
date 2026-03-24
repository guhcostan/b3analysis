# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

`run.sh` is a venv-aware Python runner. It bootstraps `.venv` on first use, then executes any Python script inside it:

```bash
bash run.sh scripts/fetch_stock.py WEGE3.SA 2026-03-24
bash run.sh scripts/fetch_macro.py 2026-03-24
bash run.sh scripts/fetch_news.py WEGE3.SA 2026-03-24 14
```

Always invoke scripts via `run.sh` from the workspace root.

## Commands

| Command | Usage | Description |
|---|---|---|
| `/analyze` | `/analyze WEGE3.SA [2026-03-24]` | Full single-stock analysis |
| `/portfolio` | `/portfolio elite 10000` | Diversified portfolio builder |
| `/macro` | `/macro` | BR macroeconomic snapshot |
| `/b3profile` | `/b3profile quality` | Switch analysis model profile |

## Architecture

```
.claude/
    commands/        ← slash command orchestration (/analyze, /portfolio, /macro, /b3profile)
    agents/          ← registered subagents (stock-analyst, macro-analyst, news-analyst)
    skills/          ← domain knowledge (b3-analysis: checklist, technicals, sector impacts)
scripts/
    fetch_stock.py   → OHLCV + technicals + fundamentals (365 days)
    fetch_macro.py   → BCB indicators + Selic history + macro news
    fetch_news.py    → Google News RSS PT-BR by ticker + sector
dataflows/
    y_finance.py     → OHLCV, fundamentals, DRE, balance sheet, cash flow
    bcb_data.py      → Selic, CDI, IPCA, IGP-M, BRL/USD via BCB public API
    google_news_br.py → PT-BR financial news via Google News RSS
    stockstats_utils.py → RSI, MACD, Bollinger, SMA, ADX, ATR
    config.py        → cache dir (dataflows/data_cache/)
```

### Orchestration pattern: Command → Agent → Skill

`/analyze` and `/portfolio` spawn the registered subagents (`stock-analyst`, `macro-analyst`, `news-analyst`) in parallel via the Task tool. Each agent runs a script and returns raw output. The main session synthesizes all results into a Portuguese report using the `b3-analysis` skill for methodology.

### Profile state

Two files must stay in sync when changing profiles:
- `.b3profile` — profile name (`quality` / `balanced` / `budget`)
- `.claude/settings.json` — `{ "model": "..." }` for the synthesis model

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

<important if="analyzing any B3 stock or building a portfolio">
Criteria 1, 2, and 3 are **eliminatory** — fail any one = automatic AVOID, no exceptions.

| # | Criterion | Eliminatory |
|---|---|---|
| 1 | Consistent growing profits (escadinha, no recurring losses) | 🔴 YES |
| 2 | Liquid ON shares (ticker ending in 3, vol > R$10M/day) | 🔴 YES |
| 3 | No recent IPO (5+ years of profit history on B3) | 🔴 YES |
| 4 | Novo Mercado listing | Partial |
| 5 | Tag Along 100% | Partial |
| 6 | Controlled debt (net cash or D/EBITDA < 2x) | Partial |
| 7 | Expected return > CDI (~14.75% a.a.) | Partial |

Score 6–7 = Strong Buy. Score ≤ 2 = Exclude from portfolio entirely.
</important>

Red flags: ticker 4/11 with no ON liquidity · controlling shareholder only in ON · Tag Along < 100% · state interference · D/EBITDA > 3x

## Macro context

- **Selic meta**: ~14,75% a.a. (tightening cycle, 2025–2026)
- **CDI** ≈ Selic − 0.10% a.a. — minimum return benchmark for equities
- High Selic: favors insurance and exporters; hurts retail, utilities, high-growth tech

## Report language

All analysis reports must be written in **Portuguese (Brazil)**. Code, scripts, and this file are in English.
