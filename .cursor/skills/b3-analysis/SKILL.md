# B3 Stock Analysis Skill

Provides specialized methodology for analyzing Brazilian stocks listed on B3, interpreting financial data from yfinance, Banco Central do Brasil API, and Google News PT-BR RSS.

Use this skill when the user asks to analyze a B3 stock, build a Brazilian investment portfolio, or interpret Brazilian financial market data.

## Data Sources

Fetch data using the project scripts (run from workspace root with venv active):

```bash
# Activate venv first (only needed once per session):
source .venv/bin/activate

python scripts/fetch_stock.py WEGE3.SA 2026-03-24
python scripts/fetch_macro.py 2026-03-24
python scripts/fetch_news.py WEGE3.SA 2026-03-24 14
```

## B3 Quality Checklist

Methodology from Logan's B3 tier list (YouTube). Criteria 1, 2, 3 are **ELIMINATORY** — fail any = automatic AVOID regardless of other factors.

| # | Criterion | Eliminatory | How to evaluate |
|---|---|---|---|
| 1 | **Consistent growing profits (escadinha)** | 🔴 YES | Stair-step pattern in income statement, no recurring losses. This is the #1 criterion. |
| 2 | **Liquid ON shares (ticker ending in 3)** | 🔴 YES | PN-only or Unit-only with no ON liquidity = disqualified. Verify volume in OHLCV data. |
| 3 | **No recent IPO** | 🔴 YES | Minimum 5+ years of profit history on B3. Recent IPO = disqualified. |
| 4 | **Novo Mercado listing** | No | Highest B3 governance level — check `longName` and sector info |
| 5 | **Tag Along 100%** | No | Minority protection — < 100% = penalize, move down tier |
| 6 | **Controlled debt** | No | Prefer net cash or D/EBITDA < 2x |
| 7 | **Expected return > CDI** | No | With Selic ~14,75% a.a., CDI ≈ 14,65%. Justify via DCF, earnings yield, or DY |

### Score interpretation (after passing eliminatory filters)
- 6-7: Strong Buy / Elite
- 5: Buy
- 4: Hold / Monitor
- 0-3: Avoid

### Tier classification (mirrors Logan's tier list)
- **Elite**: All 7 ✅, proven stair-step growth, large/growing TAM
- **Bom** (Good): Passes elimatory, 5-6/7, some minor flags
- **OK**: Passes eliminatory, 4/7, one notable weakness
- **Mé** (Meh): Passes eliminatory barely, erratic profits or structural limits
- **Você é Louco** (Avoid): Fails an eliminatory criterion
- **Oi** (Worst): Persistent losses, cotação trending to zero

## Signals to Avoid (Red Flags)

- Final 4/11 only, no ON liquidity — company showing bad faith (wants capital without losing control)
- Controlling shareholder holds only ON but forces investors into PN — misalignment
- Tag Along < 100%
- Recurring losses or erratic profit pattern
- Heavy government control/interference (pricing, dividend policy risk)
- Highly cyclical commodity sectors without multi-decade consistent track record
- D/EBITDA > 3x

## Macro Context Interpretation

Current reference rates (update from BCB data):
- **Selic meta**: ~14,75% a.a. (tightening cycle as of 2025-2026)
- **CDI**: ≈ Selic − 0,10% a.a.
- **Minimum return bar for equities**: CDI + risk premium (typically CDI + 3-5%)

### Selic impact by sector

| Sector | Impact of High Selic |
|---|---|
| Banking (ITUB, BBAS) | Mixed — benefits from spread, but higher defaults |
| Utilities (EQTL, SAPR) | Negative — regulated returns compressed vs risk-free |
| Healthcare (RADL, FLRY) | Neutral-negative — capex financing more expensive |
| Retail (LREN, RENT) | Negative — consumer credit more expensive |
| Exporters (VALE, SUZB) | Positive — stronger USD boosts BRL revenue |
| Technology (TOTS) | Negative — high growth DCF heavily discounted |
| Insurance (PSSA, BBSE) | Positive — float income rises with higher rates |

## Technical Analysis Reference

When interpreting `fetch_stock.py` technical indicators:

| Indicator | Bullish Signal | Bearish Signal |
|---|---|---|
| Close > SMA 200 | Uptrend confirmed | Below = downtrend |
| SMA 50 crosses SMA 200 up | Golden cross | Death cross |
| RSI 14 | < 30 oversold (possible entry) | > 70 overbought |
| MACD hist | Positive & rising | Negative & falling |
| Price near Bollinger Lower | Potential bounce | |
| ADX > 25 | Strong trend (confirm direction) | < 20 = ranging market |

## Report Structure

For `/analyze`:
1. Executive Summary (recommendation + conviction)
2. Technical Analysis
3. Fundamental Analysis
4. B3 Quality Checklist (✅ / ⚠️ / ❌)
5. Macro Context
6. Catalysts & Risks
7. Conclusion & Price Target (vs CDI)

For `/portfolio`:
1. Individual scoring per ticker
2. Sector diversification (max 30% per sector)
3. Allocation table with BRL values
4. Top 3 conviction picks with thesis
5. Excluded tickers and reasons

## Important Rules

- Always respond in **Portuguese (Brazil)**
- State clearly when data is unavailable or scripts return errors
- Never recommend leverage or derivatives — focus on long-only equity analysis
- Always compare expected equity return vs CDI explicitly
- Respect the minimum position size (R$ 500) for portfolio allocation
