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
| `/b3:swarm` | `/b3:swarm WEGE3.SA` | Ultra-análise com 12 agentes em 3 ondas (buy-side process) |
| `/b3:analyze` | `/b3:analyze WEGE3.SA [2026-03-24]` | Full single-stock analysis (3 agents) |
| `/b3:screen` | `/b3:screen` or `/b3:screen --setor bancos` | Agent-driven B3 screening — applies 7 criteria to full universe |
| `/b3:portfolio` | `/b3:portfolio WEGE3,ITUB3 10000` | Diversified portfolio builder |
| `/b3:macro` | `/b3:macro` | BR macroeconomic snapshot |
| `/b3:profile` | `/b3:profile quality` | Switch analysis model profile |

## Architecture

```
.claude/
    commands/        ← slash command orchestration
    agents/          ← 12 registered agents in 3 tiers (see below)
    hooks/           ← PreToolUse (validate args) + PostToolUse (detect errors)
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

### Agent tiers (buy-side process model)

**Tier 1 — Data agents** (Wave 1, parallel): collect raw data, no analysis
- `stock-analyst` → OHLCV + technicals + fundamentals + financial statements
- `macro-analyst` → BCB: Selic, CDI, IPCA, BRL/USD, fiscal
- `news-analyst` → Google News PT-BR by ticker + sector

**Tier 2 — Research analysts** (Wave 2, parallel): specialized analysis across 7 dimensions
- `business-analyst` → moat, management, industry dynamics, competitive positioning
- `financial-analyst` → escadinha (criterion 1+3), margins, ROE, FCF quality
- `credit-analyst` → D/EBITDA, liquidity, Selic stress test, debt quality A/B/C/D
- `valuation-analyst` → 3-method valuation (earnings yield, multiples, FCF/DDM), price target range
- `technical-analyst` → SMA/RSI/MACD/Bollinger/ADX, entry zone, stop level
- `macro-correlation-analyst` → Selic/BRL/IPCA impact specific to this sector/company
- `governance-analyst` → criterion 2 (ON + liquidity), Novo Mercado, tag along, state risk

**Tier 3 — Devil's advocate** (Wave 3, sequential): adversarial review
- `bear-analyst` → reads all Tier 2 outputs, attacks 3 weakest assumptions, stress-tests bull case, proposes bear scenario + fragility score

**Synthesis**: main session acts as portfolio manager — weighs bull case vs bear analyst, checks eliminatory criteria, produces final verdict + position sizing guidance.

### Orchestration pattern: Command → Agent → Skill

`/b3:analyze` and `/b3:portfolio` spawn data agents (`stock-analyst`, `macro-analyst`, `news-analyst`) in parallel via the Task tool. `/b3:swarm` runs all 3 tiers sequentially (data → analysis → challenge). The main session synthesizes using the `b3-analysis` skill for methodology.

### Profile state

Two files must stay in sync when changing profiles:
- `.b3profile` — profile name (`quality` / `balanced` / `budget`)
- `.claude/settings.json` — `{ "model": "..." }` for the synthesis model

The `/b3:profile` command updates both atomically.

## Analysis profiles

| Profile | Synthesis (main) | Ticker agents | Macro agent |
|---|---|---|---|
| `quality` | claude-opus-4-6 | claude-opus-4-6 | claude-sonnet-4-6 |
| `balanced` | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 |
| `budget` | claude-sonnet-4-6 | claude-haiku-4-5 | claude-haiku-4-5 |

Default is `balanced`. For real investment decisions use `quality` + `/effort high`.

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

Every report must begin with: `⚠️ **Aviso:** Este relatório é gerado por agentes de IA para fins exclusivamente **educacionais e de estudo pessoal**. Não constitui recomendação de investimento, consultoria financeira ou análise profissional. Renda variável envolve risco de perda do capital investido.`
