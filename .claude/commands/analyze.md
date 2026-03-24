# /analyze

Análise completa de uma ação da B3 usando subagentes em paralelo.

---

## Step 0 — Coletar parâmetros via perguntas

Parse `$ARGUMENTS`. Para cada parâmetro ausente, use `AskUserQuestion`.

### 0a — Ticker

Se `$ARGUMENTS` não contém um ticker, pergunte:

```
AskUserQuestion(
  question: "Qual ação você quer analisar? Digite o ticker da B3 (ex: WEGE3, ITUB3, VALE3):"
)
```

Normalize a resposta: adicione `.SA` se não tiver (ex: `WEGE3` → `WEGE3.SA`).

### 0b — Data de referência

Se `$ARGUMENTS` não contém uma data (`YYYY-MM-DD`), pergunte:

```
AskUserQuestion(
  question: "Qual a data de referência para a análise?",
  options: [
    "Hoje ({TODAY})",
    "Outra data (eu vou digitar no formato YYYY-MM-DD)"
  ]
)
```

Se escolher "Hoje", use a data atual. Se escolher "Outra data", aguarde o input.

---

## Step 1 — Ler perfil ativo

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

| Profile | Data agents model | Synthesis model (main session) |
|---|---|---|
| `quality` | `claude-opus-4-6` | `claude-opus-4-6` |
| `balanced` | `claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `budget` | `claude-haiku-4-5` | `claude-sonnet-4-6` |

Use `claude --model {MODEL} -p "..."` as bash for data agents when model differs from session.

---

## Step 2 — Spawnar 3 agentes em paralelo com a Task tool

Use os subagentes registrados em `.claude/agents/`:

**Agente 1: `stock-analyst`**
Invoke with: TICKER={TICKER}, DATE={DATE}

**Agente 2: `macro-analyst`**
Invoke with: DATE={DATE}

**Agente 3: `news-analyst`**
Invoke with: TICKER={TICKER}, DATE={DATE}, LOOKBACK_DAYS=21

---

## Step 3 — Síntese profunda

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
