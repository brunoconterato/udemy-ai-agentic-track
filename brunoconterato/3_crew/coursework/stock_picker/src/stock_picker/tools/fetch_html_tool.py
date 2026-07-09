import re
from typing import Type
from urllib.parse import parse_qs, unquote, urlparse

import requests
from crewai.tools import BaseTool
from ddgs import DDGS
from pydantic import BaseModel, Field
from trafilatura import extract


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def _normalize_website_url(website: str) -> str:
    parsed = urlparse(website)
    if parsed.scheme:
        return website
    return f"https://{website.lstrip('/')}"


def _website_candidates(website: str) -> list[str]:
    normalized = _normalize_website_url(website)
    parsed = urlparse(normalized)
    candidates = [normalized]

    if parsed.netloc.startswith("www."):
        candidates.append(parsed._replace(netloc=parsed.netloc[4:]).geturl())
    elif parsed.netloc:
        candidates.append(parsed._replace(netloc=f"www.{parsed.netloc}").geturl())

    if parsed.scheme == "https":
        candidates.append(parsed._replace(scheme="http").geturl())
    elif parsed.scheme == "http":
        candidates.append(parsed._replace(scheme="https").geturl())

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(candidates))


def _unwrap_search_url(website: str) -> str:
    parsed = urlparse(website)
    if "duckduckgo.com" not in parsed.netloc:
        return website

    query = parse_qs(parsed.query)
    target = query.get("uddg", [None])[0]
    if target:
        return unquote(target)

    return website


def _query_from_url(website: str) -> str:
    parsed = urlparse(_normalize_website_url(website))
    tokens: list[str] = []

    host = parsed.netloc.removeprefix("www.")
    if host:
        tokens.extend(host.split("."))

    path = re.split(r"[/._?&=\-]+", f"{parsed.path} {parsed.query}")
    tokens.extend(part for part in path if part and not part.isdigit())

    return " ".join(dict.fromkeys(token for token in tokens if len(token) > 2))


def _search_result_candidates(query: str, limit: int = 5) -> list[str]:
    candidates: list[str] = []
    try:
        for item in DDGS().text(query, safesearch="on", max_results=limit, backend="auto"):
            href = item.get("href") or item.get("url")
            if href:
                candidates.append(_unwrap_search_url(href))
    except Exception as e:
        print("Exception while searching for fallback url: ", query, " --> ", e)

    return list(dict.fromkeys(candidates))


def _fetch_markdown(candidate: str) -> str | None:
    try:
        response = requests.get(candidate, headers=REQUEST_HEADERS, timeout=20)
        if response.status_code >= 400:
            return None

        result = extract(
            response.text,
            favor_recall=True,
            favor_precision=False,
            include_comments=False,
            include_tables=True,
            output_format="markdown",
        )
        return result or None
    except requests.RequestException:
        return None


class FetchHTMLInput(BaseModel):
    """Input schema for MyCustomTool."""

    url: str = Field(..., description="Url for fetching data")


class FetchHTMLTool(BaseTool):
    name: str = "Fetch HTML tool"
    description: str = (
        "Tool used for extract html content from a given url for fetching data porposes"
    )
    args_schema: Type[BaseModel] = FetchHTMLInput

    def _run(self, url: str) -> str | None:
        url_candidates = _website_candidates(_unwrap_search_url(url))
        for candidate in url_candidates:
            result = _fetch_markdown(candidate)
            if result:
                return result

        fallback_query = _query_from_url(url)
        if fallback_query:
            for search_candidate in _search_result_candidates(fallback_query):
                for candidate in _website_candidates(search_candidate):
                    result = _fetch_markdown(candidate)
                    if result:
                        return result

        return None
