# /b3:screen

Aplica os 7 critérios do Logan a um universo de ações B3 e produz uma tier list rankeada — sem listas pré-definidas, sem curadoria manual. Os agentes chegam à seleção de forma independente com base nos dados.

**Uso:** `/b3:screen $ARGUMENTS`

Exemplos:
- `/b3:screen` — screening completo do universo padrão (~60 tickers, pode levar alguns minutos)
- `/b3:screen WEGE3 ITUB3 FLRY3 RADL3 TOTS3` — screening de tickers específicos
- `/b3:screen --setor bancos` — screening de um setor (bancos, seguros, varejo, saude, energia, industrial, agro)

---

## Step 0 — Determinar universo

Parse `$ARGUMENTS`.

**Se argumentos contêm tickers**: use esses tickers (adicione `.SA` a cada um se necessário).

**Se `--setor SETOR`**: use o subconjunto do setor correspondente (ver universo na skill `b3-analysis`):
- `bancos` → ITUB3, BBAS3, BBDC3, SANB3, BRSR3
- `seguros` → PSSA3, BBSE3, IRBR3, ODPV3
- `varejo` → LREN3, ARZZ3, VULC3, PNVL3, VIVA3, GRND3
- `saude` → FLRY3, HAPV3, RDOR3, DASA3, HYPE3
- `energia` → EQTL3, EGIE3, TAEE3, CPFE3, NEOE3
- `saneamento` → SAPR3, SBSP3, CSMG3
- `industrial` → WEGE3, ROMI3, FRAS3, LEVE3
- `agro` → SLCE3, SMTO3, AGRO3
- `petroleo` → PETR3, PRIO3, RECV3
- `logistica` → RENT3, RAIL3, EMBR3
- `celulose` → SUZB3, KLBN3, RANI3
- `alimentos` → ABEV3, JBSS3, MRFG3, MDIA3

**Se sem argumentos**: avise o usuário que o screening completo cobrirá ~60 tickers e pode levar alguns minutos. Use o universo completo da skill `b3-analysis` (seção `## Universo B3`).

Informe o usuário sobre o universo selecionado antes de iniciar.

---

## Step 1 — Ler data de referência e perfil ativo

Use a data de hoje como DATE.

```bash
cat .b3profile 2>/dev/null || echo "balanced"
```

| Profile | Agentes de dados |
|---|---|
| `quality` | `claude-opus-4-6` |
| `balanced` | `claude-sonnet-4-6` |
| `budget` | `claude-haiku-4-5` |

---

## Step 2 — Coleta de dados em paralelo (Wave 1)

Lance um agente `stock-analyst` por ticker, todos em paralelo via Task tool.

Para cada TICKER na lista:
- Use o subagente registrado `stock-analyst` com: TICKER={TICKER}.SA, DATE={DATE}
- O agente executa `fetch_stock.py` e retorna fundamentais + OHLCV + técnicos

> Para o universo completo (~60 tickers), espere todos completarem antes de prosseguir para a síntese. Erros de dados para tickers individuais são normais — registre como "dados insuficientes" e continue.

---

## Step 3 — Síntese: aplicar os 7 critérios (modelo principal)

Para cada ticker que retornou dados, avalie os 7 critérios do Logan usando os dados do `stock-analyst`. Seja rigoroso — os critérios 1, 2 e 3 são eliminatórios.

### Critério 1 — Lucros crescentes (escadinha)
Verifique o histórico de lucros no DRE retornado. Padrão esperado: escadinha consistente, sem prejuízos recorrentes. Dê ⚠️ para tropeços pontuais, ❌ para prejuízos recorrentes ou tendência de queda.

### Critério 2 — ON com liquidez (final 3, vol > R$ 10M/dia)
Verifique o ticker: deve terminar em 3. Verifique o volume médio diário. Se só tem PN ou Unit (final 4, 5, 6, 11) sem ON líquida, é eliminatório.

### Critério 3 — Sem IPO recente (5+ anos de histórico de lucros na B3)
Verifique a data de listagem e o histórico disponível. Empresas com menos de 5 anos de lucros verificáveis na B3 = eliminatório.

### Critérios 4–7 (parciais)
4. Novo Mercado (segmento de listagem)
5. Tag Along 100%
6. D/EBITDA < 2x ou caixa líquido
7. Earnings Yield > CDI (~14,75% a.a.) — use P/L TTM: EY = 1/P/L

---

## Step 4 — Output em português

Produza o relatório de screening:

---

⚠️ **Aviso:** Este relatório é gerado por agentes de IA para fins exclusivamente **educacionais e de estudo pessoal**. Não constitui recomendação de investimento, consultoria financeira ou análise profissional. Renda variável envolve risco de perda do capital investido.

---

## Screening B3 — {DATE}

**Universo analisado:** {N} tickers | **Com dados:** {N} | **Sem dados:** {N} (listar)

---

### 🏆 Elite — Score 6–7/7

Passam em todos os critérios eliminatórios + maioria dos parciais.

| Ticker | Crit.1 | Crit.2 | Crit.3 | NM | TagAlong | Dívida | Retorno | Score | Tier |
|---|---|---|---|---|---|---|---|---|---|

### ✅ Bom — Score 5/7

Passam em todos os eliminatórios, 1–2 critérios parciais com ressalvas.

| Ticker | Crit.1 | Crit.2 | Crit.3 | NM | TagAlong | Dívida | Retorno | Score | Tier |
|---|---|---|---|---|---|---|---|---|---|

### 🟡 OK — Score 4/7

Passam nos eliminatórios, mas com limitações relevantes nos parciais.

| Ticker | Crit.1 | Crit.2 | Crit.3 | NM | TagAlong | Dívida | Retorno | Score | Tier |
|---|---|---|---|---|---|---|---|---|---|

### 🔴 Evitar — Critério eliminatório falhado

| Ticker | Critério falhado | Motivo |
|---|---|---|

---

### Resumo

- **Candidatos Elite/Bom para carteira:** {lista dos aprovados com score ≥ 5}
- **Próximos passos:** Use `/b3:analyze TICKER` para análise profunda ou `/b3:swarm TICKER` para análise buy-side completa de qualquer candidato.
- **Para montar carteira:** Use `/b3:portfolio {tickers dos aprovados} {capital}`

---

Seja honesto sobre limitações dos dados. Se yfinance não retornar dados suficientes para avaliar um critério, sinalize como ⚠️ dados insuficientes — não invente.
