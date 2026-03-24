"""Banco Central do Brasil (BCB) open data API integration."""

import requests
from datetime import datetime, timedelta
from typing import Optional


_BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

_SERIES = {
    "selic_diaria": 432,
    "selic_meta": 1178,
    "cdi": 4391,
    "ipca": 433,
    "igpm": 189,
    "cambio_usd": 1,
    "cambio_eur": 21619,
    "divida_pib": 4192,
    "resultado_primario": 5793,
    "credito_total": 20539,
}

_SERIES_LABELS = {
    "selic_diaria": "Taxa Selic Over (% a.a.)",
    "selic_meta": "Meta Selic (% a.a.)",
    "cdi": "CDI (% a.a.)",
    "ipca": "IPCA (% mensal)",
    "igpm": "IGP-M (% mensal)",
    "cambio_usd": "Câmbio BRL/USD",
    "cambio_eur": "Câmbio BRL/EUR",
    "divida_pib": "Dívida Bruta/PIB (%)",
    "resultado_primario": "Resultado Primário (R$ bi)",
    "credito_total": "Crédito Total/PIB (%)",
}


def _fetch_series(code: int, n_last: int = 10) -> list[dict]:
    url = f"{_BCB_BASE_URL.format(code=code)}/ultimos/{n_last}?formato=json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


def _fetch_series_range(code: int, start_date: str, end_date: str) -> list[dict]:
    start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    url = f"{_BCB_BASE_URL.format(code=code)}/dados?formato=json&dataInicial={start}&dataFinal={end}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_bcb_macro_indicators(
    curr_date: str,
    look_back_days: int = 30,
) -> str:
    """
    Fetches key Brazilian macroeconomic indicators from the BCB open data API.

    Returns Selic, CDI, IPCA, IGP-M, BRL/USD exchange rate, and fiscal data
    for the specified period, formatted as a report for the macro/news analyst.

    Args:
        curr_date: Reference date in yyyy-mm-dd format.
        look_back_days: Number of days to look back (default 30).

    Returns:
        Formatted macroeconomic report string.
    """
    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    sections = []
    sections.append(f"## Indicadores Macroeconômicos Brasileiros (BCB)\n")
    sections.append(f"Período: {start_date} a {curr_date}\n")

    selic = _fetch_series(_SERIES["selic_diaria"], n_last=5)
    if selic:
        latest = selic[-1]
        sections.append(f"### Taxa Selic Over\n")
        sections.append(f"Último valor: **{latest['valor']}% a.a.** (data: {latest['data']})\n")
        rows = " | ".join([f"{d['data']}: {d['valor']}%" for d in selic])
        sections.append(f"Histórico recente: {rows}\n")

    selic_meta = _fetch_series(_SERIES["selic_meta"], n_last=3)
    if selic_meta:
        latest = selic_meta[-1]
        sections.append(f"\n### Meta Selic (Copom)\n")
        sections.append(f"Último valor: **{latest['valor']}% a.a.** (data: {latest['data']})\n")

    cdi = _fetch_series(_SERIES["cdi"], n_last=5)
    if cdi:
        latest = cdi[-1]
        try:
            cdi_mensal = float(latest["valor"])
            cdi_anual = round(((1 + cdi_mensal / 100) ** 12 - 1) * 100, 2)
            sections.append(f"\n### CDI\n")
            sections.append(
                f"Último valor: **{cdi_mensal}% ao mês** (~{cdi_anual}% a.a. projetado) (data: {latest['data']})\n"
            )
        except ValueError:
            sections.append(f"\n### CDI\n")
            sections.append(f"Último valor: {latest['valor']}% (data: {latest['data']})\n")

    ipca_data = _fetch_series_range(_SERIES["ipca"], start_date, curr_date)
    if not ipca_data:
        ipca_data = _fetch_series(_SERIES["ipca"], n_last=6)
    if ipca_data:
        sections.append(f"\n### IPCA (Inflação Oficial)\n")
        acumulado = sum(float(d["valor"]) for d in ipca_data[-3:])
        for d in ipca_data[-4:]:
            sections.append(f"- {d['data']}: {d['valor']}%\n")
        sections.append(f"Acumulado últimos 3 meses: **{acumulado:.2f}%**\n")

    igpm_data = _fetch_series(_SERIES["igpm"], n_last=3)
    if igpm_data:
        sections.append(f"\n### IGP-M\n")
        for d in igpm_data:
            sections.append(f"- {d['data']}: {d['valor']}%\n")

    cambio_data = _fetch_series_range(_SERIES["cambio_usd"], start_date, curr_date)
    if not cambio_data:
        cambio_data = _fetch_series(_SERIES["cambio_usd"], n_last=10)
    if cambio_data:
        latest = cambio_data[-1]
        oldest = cambio_data[0]
        try:
            variacao = ((float(latest["valor"]) - float(oldest["valor"])) / float(oldest["valor"])) * 100
            sinal = "+" if variacao >= 0 else ""
            sections.append(f"\n### Câmbio BRL/USD\n")
            sections.append(f"Último: **R$ {latest['valor']}** (data: {latest['data']})\n")
            sections.append(f"Variação no período: **{sinal}{variacao:.2f}%**\n")
            if len(cambio_data) >= 5:
                recent = cambio_data[-5:]
                rows = " | ".join([f"{d['data']}: {d['valor']}" for d in recent])
                sections.append(f"Histórico: {rows}\n")
        except (ValueError, ZeroDivisionError):
            sections.append(f"\n### Câmbio BRL/USD\n")
            sections.append(f"Último: R$ {latest['valor']} (data: {latest['data']})\n")

    cambio_eur = _fetch_series(_SERIES["cambio_eur"], n_last=3)
    if cambio_eur:
        latest = cambio_eur[-1]
        sections.append(f"\n### Câmbio BRL/EUR\n")
        sections.append(f"Último: **R$ {latest['valor']}** (data: {latest['data']})\n")

    sections.append(f"\n---\n")
    sections.append(
        "**Contexto para análise:** A taxa Selic é o principal benchmark de renda fixa no Brasil. "
        "Ações na B3 precisam oferecer prêmio de risco sobre o CDI para justificar o investimento em renda variável. "
        "O câmbio BRL/USD impacta diretamente empresas exportadoras (positivo com BRL fraco) e "
        "empresas com dívida em dólar (negativo com BRL fraco). O IPCA influencia as decisões do Copom sobre a Selic.\n"
    )

    return "".join(sections)


def get_bcb_selic_history(
    curr_date: str,
    look_back_days: int = 90,
) -> str:
    """
    Returns the recent Selic rate history to contextualize the monetary policy cycle.

    Args:
        curr_date: Reference date in yyyy-mm-dd format.
        look_back_days: Number of days to look back.

    Returns:
        Formatted Selic history report.
    """
    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    meta_data = _fetch_series_range(_SERIES["selic_meta"], start_date, curr_date)
    if not meta_data:
        meta_data = _fetch_series(_SERIES["selic_meta"], n_last=6)

    if not meta_data:
        return "Dados da Selic indisponíveis no momento."

    lines = [f"## Histórico da Meta Selic (Copom) — últimos {look_back_days} dias\n\n"]
    for d in meta_data:
        lines.append(f"- {d['data']}: {d['valor']}% a.a.\n")

    if len(meta_data) >= 2:
        first = float(meta_data[0]["valor"])
        last = float(meta_data[-1]["valor"])
        diff = last - first
        trend = "em alta" if diff > 0 else ("em queda" if diff < 0 else "estável")
        lines.append(f"\n**Tendência no período:** Selic {trend} ({first}% → {last}%)\n")

    lines.append(
        "\n**Impacto no mercado:** Em ciclos de alta da Selic, o custo de capital aumenta e "
        "múltiplos de ações (P/L) tendem a se comprimir. Em ciclos de queda, o inverso ocorre, "
        "favorecendo especialmente ações de crescimento e setores sensíveis a juros "
        "(imobiliário, varejo, utilities).\n"
    )

    return "".join(lines)
