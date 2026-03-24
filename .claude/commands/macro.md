# /macro

Fetch and interpret the current Brazilian macroeconomic snapshot.

**Usage:** `/macro $ARGUMENTS`

Examples:
- `/macro`
- `/macro 2026-03-24`

---

## Instructions

Parse `$ARGUMENTS`:
- `DATE` — optional, defaults to today's date in `YYYY-MM-DD` format

Run:

```bash
bash run.sh scripts/fetch_macro.py {DATE}
```

After collecting the data, produce a **macro analysis report in Portuguese** with:

---

### 1. Painel de Indicadores

| Indicador | Valor Atual | Tendência | Impacto para RV |
|---|---|---|---|
| Selic Meta | X% a.a. | ↑ / → / ↓ | Negativo / Neutro / Positivo |
| CDI (benchmark) | X% a.a. | | |
| IPCA (último) | X% | | |
| BRL/USD | X,XX | | |

### 2. Análise do Ciclo de Juros
- Selic atual e direção do Copom
- Implicações para renda variável vs renda fixa
- Comparativo retorno mínimo exigido para ações

### 3. Inflação e Câmbio
- Leitura do IPCA e perspectiva
- BRL/USD: impacto para exportadoras vs importadoras

### 4. Notícias Macro Relevantes
- Síntese dos principais eventos e seu impacto no mercado

### 5. Conclusão: Ambiente para Renda Variável
- **Favorável / Neutro / Desfavorável** — com justificativa
- Setores mais e menos beneficiados no cenário atual
- Recomendação de alocação geral (% RV vs RF)

---

Base your analysis entirely on the data returned by the script.
