"""Banco Central do Brasil (BCB) open data API integration."""

import sys
import requests
from datetime import datetime, timedelta
from typing import Optional


_BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados"

_SERIES = {
    "selic_meta": 432,       # Copom target — entries are dated through the next meeting
    "selic_diaria": 1178,    # effective Selic Over, annualized (base 252)
    "cdi": 4391,             # CDI accumulated in the month (% a.m.)
    "cdi_anual": 4389,       # CDI annualized (base 252), daily
    "selic_diaria_pct": 11,  # effective Selic, % per business day
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
    "cdi": "CDI (% a.m.)",
    "cdi_anual": "CDI (% a.a.)",
    "selic_diaria_pct": "Selic efetiva (% a.d.)",
    "ipca": "IPCA (% mensal)",
    "igpm": "IGP-M (% mensal)",
    "cambio_usd": "Câmbio BRL/USD",
    "cambio_eur": "Câmbio BRL/EUR",
    "divida_pib": "Dívida Bruta/PIB (%)",
    "resultado_primario": "Resultado Primário (R$ bi)",
    "credito_total": "Crédito Total/PIB (%)",
}


def _get_json(url: str, code: int, retries: int = 2):
    last_err = None
    for _ in range(retries + 1):
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
    print(f"[BCB] Aviso: falha ao buscar série {code}: {last_err}", file=sys.stderr)
    return None


def _fetch_series(code: int, n_last: int = 10) -> list[dict]:
    url = f"{_BCB_BASE_URL.format(code=code)}/ultimos/{n_last}?formato=json"
    data = _get_json(url, code)
    return data if isinstance(data, list) else []


def _fetch_series_range(code: int, start_date: str, end_date: str) -> list[dict]:
    start = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    end = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    url = f"{_BCB_BASE_URL.format(code=code)}/dados?formato=json&dataInicial={start}&dataFinal={end}"
    data = _get_json(url, code)
    return data if isinstance(data, list) else []


def get_cdi_reference(curr_date: str) -> tuple[Optional[float], Optional[str]]:
    """
    Returns (cdi_pct_annual, source) — the equity hurdle rate.
    Tries annualized CDI, then the daily Selic rate (annualized), then the
    Copom target − 0.10. Returns (None, None) if the BCB API is unavailable.
    Uses the latest available values (the "ultimos" endpoint is far more
    reliable than date-range queries).
    """
    def _latest(key):
        data = _fetch_series(_SERIES[key], n_last=1)
        try:
            return float(data[-1]["valor"]), data[-1]["data"]
        except (IndexError, KeyError, ValueError):
            return None, None

    val, dt = _latest("cdi_anual")
    if val is not None:
        return round(val, 2), f"BCB SGS {_SERIES['cdi_anual']} ({dt})"

    val, dt = _latest("selic_diaria_pct")
    if val is not None:
        annual = ((1 + val / 100) ** 252 - 1) * 100
        return round(annual, 2), f"BCB SGS {_SERIES['selic_diaria_pct']} anualizada ({dt})"

    val, dt = _latest("selic_meta")
    if val is not None:
        return round(val - 0.10, 2), f"BCB SGS {_SERIES['selic_meta']} meta − 0,10"

    return None, None


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

    selic = _fetch_series_range(_SERIES["selic_diaria"], start_date, curr_date)[-5:]
    if selic:
        latest = selic[-1]
        sections.append(f"### Taxa Selic Over\n")
        sections.append(f"Último valor: **{latest['valor']}% a.a.** (data: {latest['data']})\n")
        rows = " | ".join([f"{d['data']}: {d['valor']}%" for d in selic])
        sections.append(f"Histórico recente: {rows}\n")

    selic_meta = _fetch_series_range(_SERIES["selic_meta"], start_date, curr_date) or _fetch_series(
        _SERIES["selic_meta"], n_last=1
    )
    if selic_meta:
        latest = selic_meta[-1]
        sections.append(f"\n### Meta Selic (Copom)\n")
        sections.append(f"Último valor: **{latest['valor']}% a.a.** (data: {latest['data']})\n")

    cdi_ref, cdi_src = get_cdi_reference(curr_date)
    if cdi_ref is not None:
        sections.append(f"\n### CDI (referência anual)\n")
        sections.append(f"**{cdi_ref}% a.a.** — fonte: {cdi_src}\n")

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
    past = [d for d in meta_data if datetime.strptime(d["data"], "%d/%m/%Y") <= end_dt]
    if not past:
        # Range query failed and "ultimos" only returned entries dated ahead
        # (the target is published through the next Copom meeting).
        latest = meta_data[-1]
        return (
            f"## Meta Selic (Copom)\n\n"
            f"Meta vigente: **{latest['valor']}% a.a.** (série 432 já datada até {latest['data']} — "
            f"vale até a próxima reunião do Copom). Histórico indisponível no momento (API do BCB instável).\n"
        )
    meta_data = past

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
