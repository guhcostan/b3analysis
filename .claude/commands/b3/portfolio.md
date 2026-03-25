# /b3:portfolio

Monta uma carteira diversificada na B3 usando subagentes em paralelo — um por ticker.

---

## Step 0 — Coletar parâmetros via perguntas

Parse `$ARGUMENTS`. Para cada parâmetro ausente, use `AskUserQuestion` para perguntar ao usuário.

### 0a — Tickers da carteira

Se `$ARGUMENTS` não contém uma lista de tickers, pergunte:

```
AskUserQuestion(
  question: "Quais tickers você quer incluir na carteira?",
  options: [
    "Eu vou digitar os tickers manualmente",
    "Rode /b3:screen para descobrir candidatos primeiro (recomendado se não tem lista)"
  ]
)
```

Se o usuário escolher "Eu vou digitar", pergunte em seguida:

```
AskUserQuestion(
  question: "Digite os tickers separados por vírgula (ex: WEGE3, VALE3, ITUB3). Dica: use /b3:screen para descobrir quais ações passam nos critérios do Logan antes de montar a carteira."
)
```

Se o usuário escolher rodar o screen, execute o `/b3:screen` completo primeiro e use os tickers classificados como Elite ou Bom como input para a carteira.

### 0b — Capital disponível

Se `$ARGUMENTS` não contém um valor numérico, pergunte:

```
AskUserQuestion(
  question: "Qual o valor total disponível para investir? (ex: 10000, 50000, 100000)"
)
```

Interprete a resposta como BRL. Se não informado, use R$ 10.000.

### 0c — Data de referência (opcional)

Se `$ARGUMENTS` não contém uma data (`YYYY-MM-DD`), use a data de hoje. Não pergunte — só pergunte se o usuário explicitamente quiser analisar uma data específica no passado.

---

## Step 1 — Ler perfil ativo

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

| Profile | Ticker agents model | Macro agent model |
|---|---|---|
| `quality` | `claude-opus-4-6` | `claude-sonnet-4-6` |
| `balanced` | `claude-sonnet-4-6` | `claude-haiku-4-5` |
| `budget` | `claude-haiku-4-5` | `claude-haiku-4-5` |

A síntese (Step 2) sempre usa o modelo da sessão principal (definido pelo `/b3:profile`).

---

## Step 2 — Spawnar todos os agentes em paralelo com a Task tool

Com os parâmetros coletados (TICKERS, CAPITAL, DATE), lance todos os agentes simultaneamente.

---

### Agente macro

Use o subagente registrado `macro-analyst` com: DATE={DATE}

O agente deve produzir uma macro summary cobrindo:
- Selic: current level, last Copom decision, cycle direction (hiking/cutting/pausing)
- CDI as the minimum return benchmark for equities
- BRL/USD: trend and sector impact (exporters vs importers)
- IPCA: current reading, 3-month accumulation, trajectory
- Fiscal risk: any primary deficit or debt/GDP data
- Equity environment verdict: Favorable / Neutral / Unfavorable — with justification
- Recommended cash/Tesouro Selic reserve: 0%, 10%, or 20%

---

### Um agente por ticker

Use o subagente registrado `stock-analyst` com: TICKER={TICKER}, DATE={DATE}
Use o subagente registrado `news-analyst` com: TICKER={TICKER}, DATE={DATE}, LOOKBACK_DAYS=14

O agente deve produzir para cada ticker:

```
TICKER: {TICKER}
SCORE: X/6
SIGNAL: STRONG BUY | BUY | HOLD | AVOID

CHECKLIST (cite specific data evidence — criteria 1/2/3 are ELIMINATORY: fail = AVOID):
1. [ELIMINATORY] Growing profits stair-step: ✅/⚠️/❌ — evidence: ...
2. [ELIMINATORY] Liquid ON shares (ticker ending in 3, vol > R$10M/day): ✅/⚠️/❌ — evidence: ...
3. [ELIMINATORY] No recent IPO (5+ years of profit history): ✅/⚠️/❌ — evidence: ...
4. Novo Mercado listing: ✅/⚠️/❌ — evidence: ...
5. Tag Along 100%: ✅/⚠️/❌ — evidence: ...
6. Controlled debt (D/EBITDA < 2x or net cash): ✅/⚠️/❌ — evidence: ...
7. Expected return > CDI (~14.75% a.a.): ✅/⚠️/❌ — evidence: ...

KEY METRICS: Price | P/L TTM | P/VP | DY | ROE | ROA | Margins | Revenue YoY | D/EBITDA | FCF yield
TECHNICAL: Trend (SMA50/200) | RSI14 | MACD signal
THESIS | MAIN RISKS | RED FLAGS | PRICE TARGET 12m | EXPECTED RETURN vs CDI
```

---

## Step 3 — Síntese profunda (modelo principal)

Think step by step. Re-read every individual analysis and the macro summary before writing. Challenge any conclusion that lacks numerical backing. Be specific.

Produce the final portfolio report in **Portuguese**:

---

⚠️ **Aviso:** Este relatório é gerado por agentes de IA para fins exclusivamente **educacionais e de estudo pessoal**. Não constitui recomendação de investimento, consultoria financeira ou análise profissional. Renda variável envolve risco de perda do capital investido.

---

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
