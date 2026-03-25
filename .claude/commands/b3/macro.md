# /b3:macro

Busca e interpreta o snapshot macroeconômico brasileiro atual.

---

## Step 0 — Coletar parâmetros via perguntas

Parse `$ARGUMENTS`. Se nenhuma data foi fornecida, pergunte:

```
AskUserQuestion(
  question: "Qual a data de referência para o snapshot macro?",
  options: [
    "Hoje ({TODAY})",
    "Outra data (eu vou digitar no formato YYYY-MM-DD)"
  ]
)
```

Se escolher "Hoje", use a data atual. Se escolher "Outra data", aguarde o input.

---

## Step 1 — Executar

```bash
bash run.sh scripts/fetch_macro.py {DATE}
```

---

## Step 2 — Produzir relatório macro em português

---

⚠️ **Aviso:** Este relatório é gerado por agentes de IA para fins exclusivamente **educacionais e de estudo pessoal**. Não constitui recomendação de investimento, consultoria financeira ou análise profissional. Renda variável envolve risco de perda do capital investido.

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
