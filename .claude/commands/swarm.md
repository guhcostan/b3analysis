# /swarm

Ultra-análise de uma ação B3 com 9 agentes em paralelo — 3 de dados + 6 analíticos especializados.

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

| Profile | Data agents model | Analysis agents model |
|---|---|---|
| `quality` | `claude-opus-4-6` | `claude-opus-4-6` |
| `balanced` | `claude-sonnet-4-6` | `claude-sonnet-4-6` |
| `budget` | `claude-haiku-4-5` | `claude-haiku-4-5` |

---

## Step 2 — Spawnar agentes de dados em paralelo (3 agentes)

Lance simultaneamente usando a Task tool:

**Agente 1: `stock-analyst`**
Invoke with: TICKER={TICKER}, DATE={DATE}

**Agente 2: `macro-analyst`**
Invoke with: DATE={DATE}

**Agente 3: `news-analyst`**
Invoke with: TICKER={TICKER}, DATE={DATE}, LOOKBACK_DAYS=30

Aguarde todos completarem. Capture os outputs como RAW_STOCK, RAW_MACRO, RAW_NEWS.

---

## Step 3 — Spawnar swarm analítico em paralelo (6 agentes)

Com RAW_STOCK, RAW_MACRO e RAW_NEWS disponíveis, lance todos simultaneamente usando a Task tool.

Cada agente recebe no prompt:
- TICKER={TICKER}
- RAW_STOCK={raw stock data}
- RAW_MACRO={raw macro data}
- RAW_NEWS={raw news data}

**Agente 4: `fundamental-analyst`**
**Agente 5: `technical-analyst`**
**Agente 6: `macro-correlation-analyst`**
**Agente 7: `news-sentiment-analyst`**
**Agente 8: `governance-analyst`**
**Agente 9: `peer-comparison-analyst`**

---

## Step 4 — Síntese final (modelo principal)

Think step by step. Re-read all 6 agent outputs carefully. Challenge any conclusion without numerical backing.

Produce the final swarm report in **Portuguese**:

### Painel do Swarm — {TICKER}

| Agente | Sinal | Score | Principais Achados |
|---|---|---|---|
| Fundamental | COMPRAR/MANTER/EVITAR | X/10 | ... |
| Técnico | COMPRAR/MANTER/EVITAR | X/10 | ... |
| Macro-Correlação | FAVORÁVEL/NEUTRO/DESFAVORÁVEL | X/10 | ... |
| Sentimento de Notícias | POSITIVO/NEUTRO/NEGATIVO | X/10 | ... |
| Governança | APROVADO/ALERTA/REPROVADO | X/10 | ... |
| Pares | PRÊMIO JUSTIFICADO/NEUTRO/DESCONTO | X/10 | ... |

### Critérios Eliminatórios

| Critério | Status | Agente que Verificou | Evidência |
|---|---|---|---|
| 1. Escadinha de lucros | ✅/⚠️/❌ | fundamental-analyst | ... |
| 2. ON com liquidez (final 3, vol >R$10M/dia) | ✅/⚠️/❌ | governance-analyst | ... |
| 3. Sem IPO recente (5+ anos) | ✅/⚠️/❌ | fundamental-analyst | ... |

**Se qualquer critério eliminatório falhar → EVITAR imediatamente.**

### Veredicto do Swarm

**COMPRAR / MANTER / EVITAR** — Conviction: **ALTA / MÉDIA / BAIXA**

Justificativa em 3-4 frases citando dados concretos dos agentes.

### Preço-Alvo 12 meses

- Metodologia: múltiplos históricos / earnings yield / DCF simplificado
- Preço-alvo: R$ XXX
- Retorno esperado: XX% vs CDI (~14,75% a.a.)
- Vale o risco? Sim / Não / Condicionalmente

### Divergências entre Agentes

Casos onde agentes chegaram a conclusões opostas — qual prevalece e por quê.

### Próximos Catalisadores

Top 3 eventos a monitorar nos próximos 6 meses com datas se disponíveis.
