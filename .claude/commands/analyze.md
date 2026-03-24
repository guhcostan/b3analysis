# /analyze

Perform a complete investment analysis for a B3 stock using parallel subagents.

**Usage:** `/analyze $ARGUMENTS`

Examples:
- `/analyze WEGE3.SA`
- `/analyze WEGE3.SA 2026-03-24`

> **Maximum quality mode:** Before running, set `/effort high` in Claude Code to enable extended thinking on the synthesis step.

---

## Execution — Multi-Agent Architecture

Parse `$ARGUMENTS`:
- `TICKER` — required (add `.SA` if missing for B3 tickers)
- `DATE` — optional, defaults to today (`YYYY-MM-DD`)

### Step 0 — Read active profile

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

| Profile | Data agents model | Synthesis model (main session) |
|---|---|---|
| `quality` | `claude-opus-4-6` | `claude-opus-4-6` |
| `balanced` | `claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `budget` | `claude-haiku-4-5` | `claude-sonnet-4-6` |

Use `claude --model {MODEL} -p "..."` as bash for data agents when model differs from session.

### Step 1 — Spawn 3 agents in parallel using the Task tool

**Agent 1: Stock Data**
```
Run from workspace root and return the complete raw output without summarizing:
bash run.sh scripts/fetch_stock.py {TICKER} {DATE}
```

**Agent 2: Macro Context**
```
Run from workspace root and return the complete raw output without summarizing:
bash run.sh scripts/fetch_macro.py {DATE}
```

**Agent 3: News**
```
Run from workspace root and return the complete raw output without summarizing:
bash run.sh scripts/fetch_news.py {TICKER} {DATE} 21
```

### Step 2 — Deep synthesis

Think step by step. Re-read all data carefully before writing any conclusion. Challenge your own assumptions — if a metric looks unusually good or bad, verify it against other data points. Be specific: cite actual numbers, dates, and comparisons. Avoid generic statements.

After all three agents complete, write the following report in **Portuguese**:

---

### 1. Resumo Executivo
- Ticker, nome, setor, segmento (Novo Mercado?)
- Recomendação: **COMPRAR / MANTER / EVITAR** com conviction (Alta / Média / Baixa)
- Preço atual e faixa de preço justa estimada

### 2. Checklist de Qualidade B3
Critérios 1, 2 e 3 são **eliminatórios** — falha em qualquer um = AVOID automaticamente.

| # | Critério | Status | Evidência |
|---|---|---|---|
| 1 🔴 | Lucros crescentes (escadinha, sem prejuízos recorrentes) | ✅/⚠️/❌ | ... |
| 2 🔴 | ON com liquidez (final 3, vol > R$10M/dia; só PN/Unit = eliminado) | ✅/⚠️/❌ | ... |
| 3 🔴 | Sem IPO recente (5+ anos de histórico de lucros na bolsa) | ✅/⚠️/❌ | ... |
| 4 | Novo Mercado | ✅/⚠️/❌ | ... |
| 5 | Tag Along 100% | ✅/⚠️/❌ | ... |
| 6 | Dívida controlada (caixa líquido ou D/EBITDA < 2x) | ✅/⚠️/❌ | ... |
| 7 | Retorno esperado > CDI (~14,75% a.a.) | ✅/⚠️/❌ | ... |

**Score: X/7 — SIGNAL**

### 3. Análise Técnica
- Tendência (SMA 50 vs 200, golden/death cross)
- Momentum (RSI 14, MACD)
- Suportes e resistências (Bollinger Bands)
- Volatilidade (ATR) e força da tendência (ADX)

### 4. Análise Fundamentalista
- Crescimento de receita e lucro (YoY)
- Margens: bruta, EBITDA, líquida
- ROE, ROA
- Dívida: D/EBITDA, caixa líquido vs dívida bruta
- Valuation: P/L, P/VP, Dividend Yield, FCF Yield

### 5. Contexto Macroeconômico
- Como a Selic ~14,75% a.a. afeta este negócio?
- Impacto do câmbio (exportadora / importadora / neutro)?
- Exposição ao IPCA?
- Riscos regulatórios/fiscais do setor?

### 6. Notícias e Catalisadores
- Síntese das notícias recentes mais relevantes
- Catalisadores para os próximos 6-12 meses
- Riscos identificados nas notícias

### 7. Conclusão e Preço-Alvo
- Tese de investimento em 2-3 frases
- Preço-alvo 12 meses com metodologia (múltiplos / earnings yield)
- Retorno esperado vs CDI: vale o risco?

---

Always ground every claim in the actual data returned by the agents. State clearly when data is unavailable.
