---
name: b3-analysis
description: Load this skill when analyzing Brazilian stocks listed on B3, building investment portfolios with Brazilian equities, or interpreting data from yfinance, BCB API, and Google News PT-BR. Provides the quality methodology, technical indicator reference, and sector impact framework used in /analyze and /portfolio.
---

## B3 Quality Checklist

Methodology from Logan's tier list (YouTube: @investimentosemevidencia). Criteria 1, 2, 3 are **ELIMINATORY** — fail any = automatic AVOID regardless of other factors.

| # | Criterion | Eliminatory | How to evaluate |
|---|---|---|---|
| 1 | **Consistent growing profits (escadinha)** | 🔴 YES | Stair-step pattern in income statement, no recurring losses. #1 criterion. |
| 2 | **Liquid ON shares (ticker ending in 3)** | 🔴 YES | PN-only or Unit-only with no ON liquidity = disqualified. Verify volume in OHLCV data. |
| 3 | **No recent IPO** | 🔴 YES | Minimum 5+ years of profit history on B3. |
| 4 | **Novo Mercado listing** | No | Highest B3 governance level |
| 5 | **Tag Along 100%** | No | Minority protection — < 100% = penalize |
| 6 | **Controlled debt** | No | Prefer net cash or D/EBITDA < 2x |
| 7 | **Expected return > CDI** | No | Selic ~14,75% a.a. — justify via earnings yield, DCF, or DY |

### Score interpretation (after passing eliminatory filters)
- 6–7: Strong Buy / Elite
- 5: Buy
- 4: Hold / Monitor
- 0–3: Avoid

### Tier classification
- **Elite**: All 7 ✅, proven stair-step growth, large/growing TAM
- **Bom**: Passes eliminatory, 5–6/7, minor flags
- **OK**: Passes eliminatory, 4/7, one notable weakness
- **Mé**: Passes eliminatory barely, erratic profits or structural limits
- **Você é Louco**: Fails an eliminatory criterion
- **Oi**: Persistent losses, cotação trending to zero

## Technical Indicator Reference

When interpreting `fetch_stock.py` output:

| Indicator | Bullish Signal | Bearish Signal |
|---|---|---|
| Close > SMA 200 | Uptrend confirmed | Below = downtrend |
| SMA 50 crosses SMA 200 up | Golden cross | Death cross |
| RSI 14 < 30 | Oversold — possible entry | RSI > 70 = overbought |
| MACD hist positive & rising | Momentum building | Negative & falling |
| Price near Bollinger Lower | Potential bounce | |
| ADX > 25 | Strong trend — confirm direction | ADX < 20 = ranging market |

## Macro Impact by Sector

| Sector | High Selic Impact |
|---|---|
| Banking (ITUB, BBAS) | Mixed — spread benefits, but higher default risk |
| Utilities (EQTL, SAPR) | Negative — regulated returns compressed vs risk-free |
| Healthcare (RADL, FLRY) | Neutral-negative — capex financing more expensive |
| Retail (LREN, RENT) | Negative — consumer credit more expensive |
| Exporters (VALE, SUZB) | Positive — stronger USD boosts BRL revenue |
| Technology (TOTS) | Negative — high growth DCF heavily discounted |
| Insurance (PSSA, BBSE) | Positive — float income rises with higher rates |

## Red Flags

- Ticker final 4/11 only, no ON liquidity — bad faith (wants capital without losing control)
- Controlling shareholder holds only ON, forces investors into PN — misalignment
- Tag Along < 100%
- Heavy state interference (pricing, dividend policy risk)
- D/EBITDA > 3x
- Highly cyclical commodity sector without multi-decade consistent track record

## Output Rules

- Always respond in **Portuguese (Brazil)**
- **Every report must begin with the disclaimer:** `⚠️ **Aviso:** Este relatório é gerado por agentes de IA para fins exclusivamente **educacionais e de estudo pessoal**. Não constitui recomendação de investimento, consultoria financeira ou análise profissional. Renda variável envolve risco de perda do capital investido.`
- Always compare expected equity return vs CDI explicitly
- State clearly when data is unavailable or scripts return errors
- Never recommend leverage or derivatives — long-only equity analysis only
- Minimum position size for portfolio allocation: R$ 500

## Universo B3 (Screening)

Usado pelo `/b3:screen` como universo padrão de triagem. Apenas ações ON (final 3) ou com ON líquida conhecida. Atualizar conforme necessário.

```
Bancos:         ITUB3, BBAS3, BBDC3, SANB3, BRSR3
Seguros:        PSSA3, BBSE3, IRBR3, ODPV3
Varejo:         LREN3, ARZZ3, VULC3, PNVL3, VIVA3, GRND3
Saúde:          FLRY3, HAPV3, RDOR3, DASA3, HYPE3
Tech/Software:  TOTS3, INTB3
Energia:        EQTL3, EGIE3, TAEE3, CPFE3, NEOE3
Saneamento:     SAPR3, SBSP3, CSMG3
Industrial:     WEGE3, ROMI3, FRAS3, LEVE3
Farmácias:      RADL3
Petróleo:       PETR3, PRIO3, RECV3
Mineração:      VALE3, GOAU3, GGBR3
Agro:           SLCE3, SMTO3, AGRO3
Logística:      RENT3, RAIL3, EMBR3
Construção:     DIRR3, CYRE3
Celulose:       SUZB3, KLBN3, RANI3
Alimentos:      ABEV3, JBSS3, MRFG3, MDIA3
Educação:       YDUQ3
```

> Este universo pode ser substituído por qualquer lista de tickers via `/b3:screen TICKER1 TICKER2 ...`

## Gotchas

- **Criterion 2 is often misread**: check the actual ticker suffix AND verify daily volume > R$ 10M. A ticker ending in 3 with low liquidity still fails criterion 2.
- **yfinance P/L can be misleading for Brazilian stocks**: cross-check against the income statement returned by `fetch_stock.py`. Trailing PE from `info` uses US GAAP adjustments.
- **CDI is monthly in BCB data**: `fetch_macro.py` converts it to annualized, but always double-check the annualization logic when citing CDI % a.a.
- **Google News RSS has no pagination**: if the lookback window is long and articles are sparse, `fetch_news.py` may return fewer results than expected. This is a data gap, not an error.
- **D/EBITDA from yfinance uses `debtToEquity`** (debt/equity ratio), not debt/EBITDA. To get D/EBITDA, divide `totalDebt` by `ebitda` from the fundamentals output.
- **Score ≤ 2 = exclude from portfolio regardless of macro environment**. No macro tailwind overrides a failed eliminatory criterion.
