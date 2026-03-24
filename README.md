# B3Analysis

![B3Analysis](docs/banner.png)

Agente de análise de ações brasileiras (B3) usando Claude Code. Sem API keys — todos os dados vêm de fontes públicas (yfinance, BCB, Google News RSS).

---

## Início rápido

```bash
git clone https://github.com/guhcostan/b3analysis.git
cd b3analysis

# Análise de uma ação
/analyze WEGE3.SA

# Carteira diversificada
/portfolio elite 10000

# Snapshot macro
/macro
```

O ambiente Python (`.venv`) é criado automaticamente na primeira execução. Nenhum setup manual necessário.

---

## Comandos

| Comando | Exemplo | Descrição |
|---|---|---|
| `/analyze` | `/analyze WEGE3.SA 2026-03-24` | Análise completa com técnica, fundamentos e macro |
| `/portfolio` | `/portfolio elite 10000` | Carteira com alocação otimizada por conviction |
| `/macro` | `/macro` | Painel de indicadores BCB + notícias macro |
| `/b3profile` | `/b3profile quality` | Troca o perfil de qualidade/custo dos agentes |

### Presets de carteiras

| Preset | Tickers |
|---|---|
| `elite` | WEGE3, ITUB3, BBAS3, RADL3, LREN3, EQTL3, RENT3, PSSA3, FLRY3, TOTS3 |
| `elite-plus` | Elite + BBSE3, SAPR3 |
| `blue-chips` | PETR4, VALE3, ITUB4, BBDC4, ABEV3, WEGE3, RENT3, SUZB3, EQTL3, BBAS3 |

---

## Perfis de análise

Controla qual modelo Claude usa por tipo de agente. Troque com `/b3profile`.

| Perfil | Síntese | Agentes ticker | Agente macro | Quando usar |
|---|---|---|---|---|
| `quality` | claude-opus-4-6 | claude-opus-4-6 | claude-sonnet-4-6 | Decisão real de investimento |
| `balanced` | claude-sonnet-4-6 | claude-sonnet-4-6 | claude-haiku-4-5 | Padrão — bom equilíbrio |
| `budget` | claude-sonnet-4-6 | claude-haiku-4-5 | claude-haiku-4-5 | Screening rápido |

Para máxima qualidade na síntese, combine `quality` com `/effort high`.

---

## Metodologia

Baseada na tier list B3 do Logan. Os critérios 1, 2 e 3 são **eliminatórios** — a empresa falha em qualquer um e vai direto para EVITAR.

| # | Critério | Eliminatório |
|---|---|---|
| 1 | **Lucros crescentes (escadinha)** — padrão consistente, sem prejuízos recorrentes | ✅ Sim |
| 2 | **ON com liquidez (final 3)** — vol > R$ 10M/dia; só PN/Unit = descartado | ✅ Sim |
| 3 | **Sem IPO recente** — mínimo 5+ anos de histórico de lucros na B3 | ✅ Sim |
| 4 | Novo Mercado (maior governança da B3) | Parcial |
| 5 | Tag Along 100% (proteção ao minoritário) | Parcial |
| 6 | Dívida controlada (caixa líquido ou D/EBITDA < 2x) | Parcial |
| 7 | Retorno esperado > CDI (~14,75% a.a.) | Parcial |

### Sinais de alerta

- Ticker final 4/11 sem ON com liquidez — empresa quer capital sem perder controle
- Controlador com só ON, força investidor a entrar por PN — desalinhamento
- Tag Along < 100%
- Interferência estatal forte (risco de dividendos e precificação)
- D/EBITDA > 3x
- Setor cíclico de commodity sem histórico multi-décadas consistente

---

## Arquitetura

```
.claude/commands/        ← Definições dos slash commands (orquestração multi-agente)
    analyze.md           → Spawna 3 agentes em paralelo (ação + macro + notícias)
    portfolio.md         → Spawna N+1 agentes (1 por ticker + macro)
    macro.md             → Executa fetch_macro.py e produz relatório

scripts/
    fetch_stock.py       → OHLCV + técnicos + fundamentos (365 dias)
    fetch_macro.py       → Indicadores BCB + histórico Selic + notícias macro
    fetch_news.py        → Notícias PT-BR por ticker + setor (Google News RSS)

dataflows/
    y_finance.py         → OHLCV, fundamentos, DRE, balanço, fluxo de caixa
    bcb_data.py          → Selic, CDI, IPCA, IGP-M, câmbio via API pública BCB
    google_news_br.py    → Notícias financeiras PT-BR via Google News RSS
    stockstats_utils.py  → RSI, MACD, Bollinger, SMA, ADX, ATR via stockstats
    config.py            → Cache local em dataflows/data_cache/
```

### Fluxo de execução `/analyze`

```
/analyze WEGE3.SA
    │
    ├─▶ [Agente 1] fetch_stock.py WEGE3.SA      ─┐
    ├─▶ [Agente 2] fetch_macro.py               ─┼─▶ Síntese (modelo principal)
    └─▶ [Agente 3] fetch_news.py WEGE3.SA 21d   ─┘         │
                                                             ▼
                                              Relatório completo em PT-BR
```

### Fluxo de execução `/portfolio`

```
/portfolio elite 10000
    │
    ├─▶ [Agente macro]   fetch_macro.py          ─┐
    ├─▶ [Agente WEGE3]   fetch_stock + fetch_news ┤
    ├─▶ [Agente ITUB3]   fetch_stock + fetch_news ┤
    ├─▶ [...]            ...                      ┼─▶ Síntese → Alocação final
    └─▶ [Agente TOTS3]   fetch_stock + fetch_news ─┘
```

---

## Fontes de dados

| Fonte | O que fornece | Autenticação |
|---|---|---|
| [Yahoo Finance](https://finance.yahoo.com) via `yfinance` | OHLCV, fundamentos, DRE, balanço, fluxo de caixa | Nenhuma |
| [BCB API aberta](https://dadosabertos.bcb.gov.br) | Selic, CDI, IPCA, IGP-M, câmbio, dívida/PIB | Nenhuma |
| [Google News RSS](https://news.google.com) | Notícias financeiras PT-BR | Nenhuma |

---

## Dependências

```
yfinance==1.2.0
stockstats==0.6.8
pandas==3.0.1
requests==2.32.5
python-dateutil==2.9.0.post0
```

Python 3.10+. Gerenciado automaticamente pelo `run.sh`.

---

## Contexto macro (atualizar periodicamente)

- **Selic meta**: ~14,75% a.a. (ciclo de alta, 2025–2026)
- **CDI** é o benchmark mínimo de retorno para renda variável
- **IPCA elevado** comprime margens de empresas com custo fixo alto
- **BRL/USD**: moeda fraca favorece exportadoras; importadoras e endividadas em dólar sofrem
