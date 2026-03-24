"""Google News RSS integration for Brazilian financial news in Portuguese."""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional


_GOOGLE_NEWS_RSS_URL = (
    "https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
)

_BR_MACRO_QUERIES = [
    "mercado financeiro B3 bolsa Brasil",
    "Copom Selic Banco Central Brasil",
    "IPCA inflação economia brasileira",
    "dólar real câmbio Brasil",
    "resultado fiscal governo federal Brasil",
]

_BR_SECTOR_QUERIES = {
    "energia": "petróleo gás Petrobras energia elétrica B3 ações",
    "financeiro": "bancos Itaú Bradesco financeiras crédito Brasil investimento",
    "commodities": "Vale minério ferro soja agronegócio exportação commodity Brasil",
    "varejo": "Magazine Luiza Renner varejo consumo e-commerce Brasil B3",
    "imobiliario": "FII fundo imobiliário CSHG construção civil Brasil B3",
    "saude": "Hapvida Rede D'Or saúde hospitais farmácias Brasil B3",
    "tecnologia": "TOTVS LWSA tecnologia TI startups Brasil B3",
    "saneamento": "Sanepar Sabesp saneamento básico água esgoto Brasil B3",
}


def _fetch_rss(query: str, max_items: int = 20) -> list[dict]:
    encoded = urllib.parse.quote(query)
    url = _GOOGLE_NEWS_RSS_URL.format(query=encoded)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        root = ET.fromstring(resp.read())
        items = []
        for item in root.findall(".//item")[:max_items]:
            title_el = item.find("title")
            link_el = item.find("link")
            pub_el = item.find("pubDate")
            source_el = item.find("source")
            desc_el = item.find("description")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            pub_date_str = pub_el.text if pub_el is not None else ""
            source = source_el.text if source_el is not None else "Google News"
            description = desc_el.text if desc_el is not None else ""

            pub_dt = None
            if pub_date_str:
                try:
                    pub_dt = parsedate_to_datetime(pub_date_str).replace(tzinfo=None)
                except Exception:
                    pass

            if title:
                items.append({
                    "title": title,
                    "link": link,
                    "pub_date": pub_dt,
                    "source": source,
                    "description": description,
                })
        return items
    except Exception:
        return []


def _filter_by_date(
    items: list[dict], start_dt: datetime, end_dt: datetime
) -> list[dict]:
    filtered = []
    for item in items:
        if item["pub_date"] is None:
            filtered.append(item)
        elif start_dt <= item["pub_date"] <= end_dt + timedelta(days=1):
            filtered.append(item)
    return filtered


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _format_articles(articles: list[dict], limit: int) -> str:
    output = ""
    for article in articles[:limit]:
        pub_str = (
            article["pub_date"].strftime("%d/%m/%Y %H:%M")
            if article["pub_date"]
            else "Data não disponível"
        )
        output += f"### {article['title']}\n"
        output += f"**Fonte:** {article['source']} | **Data:** {pub_str}\n"
        if article["description"]:
            clean_desc = _strip_html(article["description"])
            title_clean = _strip_html(article["title"])
            if clean_desc.startswith(title_clean):
                clean_desc = clean_desc[len(title_clean):].strip()
            if len(clean_desc) > 300:
                clean_desc = clean_desc[:300] + "..."
            if clean_desc and len(clean_desc) > 10:
                output += f"{clean_desc}\n"
        if article["link"]:
            output += f"[Leia mais]({article['link']})\n"
        output += "\n"
    return output


def get_news_google_br(
    ticker: str,
    start_date: str,
    end_date: str,
) -> str:
    """
    Fetches Brazilian financial news for a specific stock ticker via Google News RSS (PT-BR).

    Args:
        ticker: Stock ticker symbol (e.g., "PETR4.SA" or "VALE3.SA").
        start_date: Start date in yyyy-mm-dd format.
        end_date: End date in yyyy-mm-dd format.

    Returns:
        Formatted string with relevant Brazilian news articles in Portuguese.
    """
    clean_ticker = ticker.upper().replace(".SA", "")

    company_map = {
        "PETR3": "Petrobras", "PETR4": "Petrobras",
        "VALE3": "Vale",
        "ITUB3": "Itaú Unibanco", "ITUB4": "Itaú Unibanco",
        "BBDC3": "Bradesco", "BBDC4": "Bradesco",
        "ABEV3": "Ambev",
        "MGLU3": "Magazine Luiza",
        "WEGE3": "WEG",
        "RENT3": "Localiza",
        "BBAS3": "Banco do Brasil",
        "SUZB3": "Suzano",
        "RDOR3": "Rede D'Or",
        "EQTL3": "Equatorial",
        "PRIO3": "PRIO",
        "GGBR4": "Gerdau",
        "CSNA3": "CSN",
        "LREN3": "Lojas Renner",
        "HAPV3": "Hapvida",
        "RADL3": "Raia Drogasil",
        "TOTS3": "TOTVS",
        "PSSA3": "Porto Seguro",
        "FLRY3": "Fleury",
        "BBSE3": "BB Seguridade",
        "SAPR3": "Sanepar",
    }

    company_name = company_map.get(clean_ticker, clean_ticker)
    queries = [
        f"{clean_ticker} {company_name} B3 ações",
        f"{company_name} resultados dividendos investidores",
        f"{company_name} notícias mercado",
    ]

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    all_articles = []
    seen_titles: set[str] = set()

    for query in queries:
        items = _fetch_rss(query, max_items=15)
        for item in _filter_by_date(items, start_dt, end_dt):
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_articles.append(item)

    all_articles.sort(key=lambda x: x["pub_date"] or datetime.min, reverse=True)

    if not all_articles:
        return (
            f"Nenhuma notícia encontrada para {ticker} ({company_name}) "
            f"entre {start_date} e {end_date} nas fontes brasileiras."
        )

    header = (
        f"## Notícias Brasileiras — {ticker} ({company_name})\n"
        f"Período: {start_date} a {end_date} | {len(all_articles)} artigos encontrados\n\n"
    )
    return header + _format_articles(all_articles, limit=15)


def get_macro_news_br(
    curr_date: str,
    look_back_days: int = 7,
    limit: int = 10,
) -> str:
    """
    Fetches broad Brazilian macroeconomic and financial market news via Google News RSS (PT-BR).

    Covers: Copom/Selic decisions, IPCA, BRL/USD exchange rate, government fiscal policy,
    B3 market overview, and commodity prices affecting Brazilian exports.

    Args:
        curr_date: Reference date in yyyy-mm-dd format.
        look_back_days: Number of days to look back (default 7).
        limit: Maximum number of articles per topic (default 10).

    Returns:
        Formatted macroeconomic news report in Portuguese.
    """
    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    all_articles: list[dict] = []
    seen_titles: set[str] = set()

    for query in _BR_MACRO_QUERIES:
        items = _fetch_rss(query, max_items=10)
        for item in _filter_by_date(items, start_dt, end_dt):
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_articles.append(item)

    all_articles.sort(key=lambda x: x["pub_date"] or datetime.min, reverse=True)

    if not all_articles:
        return (
            f"Nenhuma notícia macroeconômica brasileira encontrada "
            f"entre {start_date} e {curr_date}."
        )

    header = (
        f"## Notícias Macroeconômicas Brasileiras (Google News PT-BR)\n"
        f"Período: {start_date} a {curr_date} | {len(all_articles)} artigos encontrados\n\n"
        "Fontes: InfoMoney, Valor Econômico, Exame, Estadão, Folha, G1 Economia, Bora Investir\n\n"
    )
    return header + _format_articles(all_articles, limit=limit)


def get_sector_news_br(
    sector: str,
    curr_date: str,
    look_back_days: int = 7,
    limit: int = 8,
) -> str:
    """
    Fetches Brazilian sector-specific news via Google News RSS.

    Args:
        sector: One of: energia, financeiro, commodities, varejo, imobiliario, saude, tecnologia.
        curr_date: Reference date in yyyy-mm-dd format.
        look_back_days: Number of days to look back.
        limit: Maximum number of articles to return.

    Returns:
        Formatted sector news report in Portuguese.
    """
    sector = sector.lower().strip()
    query = _BR_SECTOR_QUERIES.get(sector, f"{sector} mercado Brasil B3")

    end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    start_dt = end_dt - timedelta(days=look_back_days)
    start_date = start_dt.strftime("%Y-%m-%d")

    items = _fetch_rss(query, max_items=20)
    filtered = _filter_by_date(items, start_dt, end_dt)
    filtered.sort(key=lambda x: x["pub_date"] or datetime.min, reverse=True)

    if not filtered:
        all_items = _fetch_rss(query, max_items=20)
        all_items.sort(key=lambda x: x["pub_date"] or datetime.min, reverse=True)
        if not all_items:
            return f"Nenhuma notícia encontrada para o setor '{sector}'."
        header = (
            f"## Notícias do Setor: {sector.capitalize()} (Brasil) — artigos mais recentes disponíveis\n"
            f"(Nenhum artigo encontrado nos últimos {look_back_days} dias; exibindo os mais recentes)\n\n"
        )
        return header + _format_articles(all_items, limit=limit)

    header = (
        f"## Notícias do Setor: {sector.capitalize()} (Brasil)\n"
        f"Período: {start_date} a {curr_date} | {len(filtered)} artigos encontrados\n\n"
    )
    return header + _format_articles(filtered, limit=limit)
