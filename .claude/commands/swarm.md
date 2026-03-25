# /swarm

Ultra-análise de uma ação B3 com 12 agentes em 3 ondas sequenciais — espelhando o processo de uma gestora buy-side profissional: coleta → análise especializada → revisão adversarial → decisão.

---

## Step 0 — Coletar parâmetros

Parse `$ARGUMENTS`. Para cada parâmetro ausente, use `AskUserQuestion`.

### 0a — Ticker

Se `$ARGUMENTS` não contém um ticker, pergunte:

```
AskUserQuestion(
  question: "Qual ação você quer analisar com o swarm? Digite o ticker da B3 (ex: WEGE3, ITUB3, VALE3):"
)
```

Normalize: adicione `.SA` se não tiver (ex: `WEGE3` → `WEGE3.SA`).

### 0b — Data de referência

Se `$ARGUMENTS` não contém uma data (`YYYY-MM-DD`), use a data de hoje. Não pergunte.

---

## Step 1 — Ler perfil ativo

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

| Profile | Modelo dos agentes |
|---|---|
| `quality` | `claude-opus-4-6` |
| `balanced` | `claude-sonnet-4-6` |
| `budget` | `claude-haiku-4-5` |

---

## Step 2 — ONDA 1: Coleta de dados (3 agentes, paralelo)

Lance simultaneamente usando a Task tool:

**Agente 1: `stock-analyst`** → TICKER={TICKER}, DATE={DATE}
**Agente 2: `macro-analyst`** → DATE={DATE}
**Agente 3: `news-analyst`** → TICKER={TICKER}, DATE={DATE}, LOOKBACK_DAYS=30

Aguarde todos completarem. Capture: RAW_STOCK, RAW_MACRO, RAW_NEWS.

---

## Step 3 — ONDA 2: Análise especializada (7 agentes, paralelo)

Com os dados brutos disponíveis, lance todos simultaneamente usando a Task tool.

Cada agente recebe: TICKER={TICKER}, RAW_STOCK, RAW_MACRO, RAW_NEWS.

**Agente 4: `business-analyst`** → moat, gestão, dinâmicas do setor
**Agente 5: `financial-analyst`** → escadinha (critério 1 e 3), margens, ROE, FCF
**Agente 6: `credit-analyst`** → dívida, liquidez, stress test (critério 6)
**Agente 7: `valuation-analyst`** → 3 métodos, preço-alvo range, CDI hurdle (critério 7)
**Agente 8: `technical-analyst`** → SMA/RSI/MACD/Bollinger/ADX, entrada/stop
**Agente 9: `macro-correlation-analyst`** → impacto Selic/BRL/IPCA neste setor
**Agente 10: `governance-analyst`** → ON/liquidez (critério 2), Novo Mercado, tag along

Aguarde todos completarem.

---

## Step 4 — ONDA 3: Revisão adversarial (1 agente, sequencial)

Lance o agente `bear-analyst` com todos os outputs da Onda 2 no contexto:

**Agente 11: `bear-analyst`** → recebe TICKER, RAW_STOCK, RAW_MACRO, RAW_NEWS, e os outputs completos dos 7 agentes da Onda 2.

O bear-analyst identifica os 3 pontos mais fracos da tese, stress-testa o bull case, e propõe bear scenario com preço-alvo alternativo.

Aguarde a conclusão antes de sintetizar.

---

## Step 5 — Síntese final (modelo principal como portfolio manager)

Think step by step. Re-read todos os 7 outputs de análise + o output do bear-analyst antes de escrever qualquer conclusão. Não aceite nenhuma afirmação sem respaldo numérico.

Produce the final swarm report in **Portuguese**:

---

### Painel do Swarm — {TICKER}

| Agente | Papel | Sinal | Score | Principais Achados |
|---|---|---|---|---|
| business-analyst | Estrategista de Setor | COMPRAR/MANTER/EVITAR | X/10 | ... |
| financial-analyst | Analista Financeiro | COMPRAR/MANTER/EVITAR | X/10 | ... |
| credit-analyst | Analista de Crédito | A/B/C/D | X/10 | ... |
| valuation-analyst | Especialista em Valuation | COMPRAR/MANTER/EVITAR | X/10 | ... |
| technical-analyst | Analista Técnico | COMPRAR/MANTER/EVITAR | X/10 | ... |
| macro-correlation | Estrategista Macro | FAVORÁVEL/NEUTRO/DESFAVORÁVEL | X/10 | ... |
| governance-analyst | Analista de Governança | APROVADO/ALERTA/REPROVADO | X/10 | ... |
| **bear-analyst** | **Devil's Advocate** | **Fragility: Baixa/Média/Alta** | X/10 | ... |

---

### Critérios Eliminatórios B3

| # | Critério | Status | Agente | Evidência |
|---|---|---|---|---|
| 1 🔴 | Escadinha de lucros | ✅/⚠️/❌ | financial-analyst | ... |
| 2 🔴 | ON com liquidez (final 3, vol >R$10M/dia) | ✅/⚠️/❌ | governance-analyst | ... |
| 3 🔴 | Sem IPO recente (5+ anos) | ✅/⚠️/❌ | financial-analyst | ... |

**Se qualquer critério eliminatório falhar → EVITAR imediatamente, sem exceção.**

---

### Resumo do Bear Case (devil's advocate)

- Top 3 pontos fracos da tese: {lista}
- Cenários que quebram a tese: {3 cenários com probabilidade e downside}
- Bear case preço-alvo: R$ {value} ({%} vs atual)
- Fragilidade da tese: **Baixa / Média / Alta**

---

### Valuation — Preço-Alvo Range

| Cenário | Metodologia | Preço-Alvo | vs Atual | vs CDI |
|---|---|---|---|---|
| Bear | {método} | R$ X | {%} | {acima/abaixo} |
| Base | {método} | R$ X | {%} | {acima/abaixo} |
| Bull | {método} | R$ X | {%} | {acima/abaixo} |

CDI hurdle: ~14,75% a.a.

---

### Veredicto do Swarm

**COMPRAR / MANTER / EVITAR** — Conviction: **ALTA / MÉDIA / BAIXA**

Justificativa em 3-4 frases citando dados concretos dos agentes e endereçando o bear case.

---

### Gestão de Risco

- Moat defensivo: {Forte/Moderado/Fraco}
- Risco de balanço: {A/B/C/D}
- Fragilidade da tese: {Baixa/Média/Alta}
- **Tamanho de posição sugerido:** {Concentrada >5% / Padrão 2-4% / Reduzida <2%} — baseado em conviction + fragilidade
- Stop sugerido: R$ {nível técnico do technical-analyst}
- Catalisadores a monitorar: {top 3 eventos com datas se disponíveis}
