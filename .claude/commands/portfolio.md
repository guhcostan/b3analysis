# /portfolio

Build a diversified B3 investment portfolio using parallel subagents — one per ticker.

**Usage:** `/portfolio $ARGUMENTS`

Examples:
- `/portfolio`
- `/portfolio elite`
- `/portfolio elite 10000`
- `/portfolio blue-chips 50000`
- `/portfolio WEGE3.SA,ITUB3.SA,VALE3.SA 25000`

---

## Preset definitions

| Preset | Tickers |
|---|---|
| `elite` | WEGE3.SA, ITUB3.SA, BBAS3.SA, RADL3.SA, LREN3.SA, EQTL3.SA, RENT3.SA, PSSA3.SA, FLRY3.SA, TOTS3.SA |
| `elite-plus` | All `elite` + BBSE3.SA, SAPR3.SA |
| `blue-chips` | PETR4.SA, VALE3.SA, ITUB4.SA, BBDC4.SA, ABEV3.SA, WEGE3.SA, RENT3.SA, SUZB3.SA, EQTL3.SA, BBAS3.SA |

If no preset or tickers are provided, use `elite` as default.

---

## Step 0 — Read active profile

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

Based on the profile, assign models:

| Profile | Ticker agents model | Macro agent model |
|---|---|---|
| `quality` | `claude-opus-4-6` | `claude-sonnet-4-6` |
| `balanced` | `claude-sonnet-4-6` | `claude-haiku-4-5` |
| `budget` | `claude-haiku-4-5` | `claude-haiku-4-5` |

The synthesis step (Step 2) always uses the main session model (set by `/b3profile`).

---

## Step 1 — Spawn all agents in parallel using the Task tool

Parse `$ARGUMENTS` to extract PRESET/TICKERS and CAPITAL (default R$ 10.000). Then launch all agents simultaneously.

---

### Macro agent
Model: per profile table above (use `claude --model {MACRO_MODEL} -p "..."` as bash if model differs from session)

Prompt:
```
Think carefully before answering.

Run from workspace root:
bash run.sh scripts/fetch_macro.py {DATE}

Analyze the output and write a macro summary covering:
- Selic: current level, last Copom decision, cycle direction (hiking/cutting/pausing)
- CDI as the minimum return benchmark for equities
- BRL/USD: trend and sector impact (exporters vs importers)
- IPCA: current reading, 3-month accumulation, trajectory
- Fiscal risk: any primary deficit or debt/GDP data
- Equity environment verdict: Favorable / Neutral / Unfavorable — with justification
- Recommended cash/Tesouro Selic reserve: 0%, 10%, or 20%
```

---

### One ticker agent per ticker
Model: per profile table above (use `claude --model {TICKER_MODEL} -p "..."` as bash if model differs from session)

Prompt per TICKER:
```
Think step by step. You are doing institutional-quality B3 analysis.

Run from workspace root:
bash run.sh scripts/fetch_stock.py {TICKER} {DATE}
bash run.sh scripts/fetch_news.py {TICKER} {DATE} 14

Read ALL data before drawing conclusions. Produce:

TICKER: {TICKER}
SCORE: X/6
SIGNAL: STRONG BUY | BUY | HOLD | AVOID

CHECKLIST (cite specific data evidence for each — criteria 1/2/3 are ELIMINATORY: fail = AVOID):
1. [ELIMINATORY] Growing profits stair-step (no recurring losses, consistent long-term growth): ✅/⚠️/❌ — evidence: ...
2. [ELIMINATORY] Liquid ON shares (ticker ending in 3, volume > R$10M/day; PN/Unit only = disqualified): ✅/⚠️/❌ — evidence: ...
3. [ELIMINATORY] No recent IPO (5+ years of profit history on B3; recent IPO = disqualified): ✅/⚠️/❌ — evidence: ...
4. Novo Mercado listing: ✅/⚠️/❌ — evidence: ...
5. Tag Along 100%: ✅/⚠️/❌ — evidence: ...
6. Controlled debt (D/EBITDA < 2x or net cash preferred): ✅/⚠️/❌ — evidence: ...
7. Expected return > CDI (~14.75% a.a.) via earnings yield / DCF / DY: ✅/⚠️/❌ — evidence: ...

KEY METRICS (exact values from data):
- Price: R$ X | P/L TTM: X | Forward P/L: X
- P/VP: X | DY: X% | ROE: X% | ROA: X%
- Margins (gross/EBITDA/net): X% / X% / X%
- Revenue YoY: X% | Net income YoY: X%
- Net Debt/EBITDA: X (or net cash R$ X) | FCF yield: X%

TECHNICAL (from indicators data):
- Trend: price vs SMA50/SMA200 — above/below, golden/death cross
- RSI14: X — oversold / neutral / overbought
- MACD: bullish / bearish signal

THESIS (specific, cite numbers): ...
MAIN RISKS (specific, not generic): ...
RED FLAGS (anything disqualifying): ...
PRICE TARGET 12m (with method): R$ X via [P/L reversion / earnings yield / DCF]
EXPECTED RETURN vs CDI (14.75%): X% — worthwhile: yes / marginal / no
```

---

## Step 2 — Deep synthesis (main model)

Think step by step. Re-read every individual analysis and the macro summary before writing. Challenge any conclusion that lacks numerical backing. Be specific.

Produce the final portfolio report in **Portuguese**:

### Resumo Macro
(macro agent summary, 150 words max)

### Scoring Individual

| Ticker | Score | Signal | P/L | ROE | D/EBITDA | DY | Preço |
|---|---|---|---|---|---|---|---|

### Alocação da Carteira

Rules:
- **AVOID (score ≤ 2):** exclude entirely
- **Max 30% per sector**
- **Conviction sizing:** STRONG BUY → larger weight, BUY → standard, HOLD → underweight
- **Minimum position:** R$ 500 (skip if below)
- **Cash reserve:** if macro is Unfavorable → 10-20% Tesouro Selic

| Ticker | Score | Signal | Setor | Alocação % | Valor R$ | Justificativa |
|---|---|---|---|---|---|---|
| **Total** | | | | **100%** | **R$ {CAPITAL}** | |

### Top 3 Convicções
2-3 sentences each, citing specific numbers from the data.

### Ativos Monitorados
Score 3-4 tickers underweighted — what catalyst to watch.

### Excluídos
Score ≤ 2 tickers with specific reason from the data.

### Riscos da Carteira
- Sector concentration
- Macro risks
- Key upcoming events (earnings, Copom, dividends, regulatory)
