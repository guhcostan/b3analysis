# B3Analysis

![B3Analysis](docs/banner.png)

![Agent Swarm](https://img.shields.io/badge/Agent%20Swarm-9%20agentes-blueviolet?style=flat-square)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Teams-blue?style=flat-square)
![B3 Brasil](https://img.shields.io/badge/B3-%F0%9F%87%A7%F0%9F%87%B7-009c3b?style=flat-square)
![No API Key](https://img.shields.io/badge/Dados-Sem%20API%20Key-success?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude%20Code-claude--sonnet--4--6-orange?style=flat-square)

Análise de ações brasileiras (B3) com **agent swarm** — equipes de agentes especializados em paralelo usando Claude Code. Sem API keys: todos os dados vêm de fontes públicas (yfinance, BCB, Google News RSS).

---

## Início rápido

```bash
git clone https://github.com/guhcostan/b3analysis.git
cd b3analysis

# Ultra-análise com swarm de 9 agentes
/swarm WEGE3.SA

# Análise completa (3 agentes)
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
| `/swarm` | `/swarm WEGE3.SA` | Ultra-análise com 9 agentes especializados em paralelo |
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

## Agent Teams & Swarm Architecture

O B3Analysis é construído em 3 camadas de **parallel agent dispatch**:

### Camada 1 — Agentes de dados (coleta paralela)

Cada agente busca uma fonte de dados independente e retorna output bruto:

```
stock-analyst    → yfinance: OHLCV + técnicos + fundamentos
macro-analyst    → BCB API: Selic, CDI, IPCA, câmbio, fiscal
news-analyst     → Google News RSS: notícias PT-BR por ticker/setor
```

### Camada 2 — Swarm analítico (6 micro-especialistas em paralelo)

O `/swarm` passa os dados brutos para 6 agentes analíticos simultaneamente. Cada um tem um mandato restrito e produz um sinal independente:

```
/swarm WEGE3.SA
       │
       ├─▶ [stock-analyst]    fetch_stock.py ──────────────┐
       ├─▶ [macro-analyst]    fetch_macro.py ──────────────┤ RAW DATA
       └─▶ [news-analyst]     fetch_news.py 30d ───────────┘
                                                            │
           ┌────────────────────────────────────────────────▼───────────────────┐
           │                  AGENT SWARM (6 em paralelo)                       │
           ├──────────────────────────┬─────────────────────────────────────────┤
           │  fundamental-analyst     │  technical-analyst                      │
           │  ↳ escadinha, D/EBITDA   │  ↳ SMA/RSI/MACD/Bollinger/ADX          │
           ├──────────────────────────┼─────────────────────────────────────────┤
           │  macro-correlation       │  news-sentiment-analyst                 │
           │  ↳ Selic/BRL/IPCA impact │  ↳ score -5..+5, catalisadores          │
           ├──────────────────────────┼─────────────────────────────────────────┤
           │  governance-analyst      │  peer-comparison-analyst                │
           │  ↳ ON/tag along/NM/estado│  ↳ prêmio/desconto vs pares B3          │
           └──────────────────────────┴─────────────────────────────────────────┘
                                                            │
                                           Síntese: painel 6 agentes
                                           + critérios eliminatórios
                                           + veredicto + preço-alvo vs CDI
```

### Camada 3 — Síntese (modelo principal)

O modelo da sessão principal integra os outputs do swarm, verifica os critérios eliminatórios, resolve divergências entre agentes e produz o relatório final em PT-BR.

---

## Arquitetura

```
.claude/
    commands/            ← Slash commands (orquestração de agent teams)
        swarm.md         → Despacha 9 agentes em paralelo (flagship)
        analyze.md       → 3 agentes em paralelo (ação + macro + notícias)
        portfolio.md     → N+1 agentes (1 por ticker + macro)
        macro.md         → Snapshot macroeconômico BCB
    agents/              ← Agentes registrados com mandatos específicos
        stock-analyst    → Coleta: OHLCV + técnicos + fundamentos
        macro-analyst    → Coleta: indicadores BCB
        news-analyst     → Coleta: notícias PT-BR RSS
        fundamental-analyst     → Análise: lucros, margens, D/EBITDA, FCF
        technical-analyst       → Análise: SMA, RSI, MACD, Bollinger, ADX
        macro-correlation       → Análise: impacto Selic/BRL/IPCA no setor
        news-sentiment-analyst  → Análise: sentimento, catalisadores, riscos
        governance-analyst      → Análise: ON/liquidez, tag along, Novo Mercado
        peer-comparison-analyst → Análise: posicionamento vs pares
    hooks/               ← Hooks Claude Code (validação + detecção de erros)
    skills/b3-analysis/  ← Conhecimento de domínio (checklist, técnicos, setores)

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

---

## Referências e inspirações

- **[TradingAgents](https://github.com/TauricResearch/TradingAgents)** — arquitetura multi-agente para análise financeira que inspirou o design deste projeto
- **[Investimentos em Evidência](https://www.youtube.com/@investimentosemevidencia)** — canal do Logan, fonte da metodologia de qualidade B3 (tier list, critérios eliminatórios, escadinha de lucros)
