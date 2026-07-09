from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from trafilatura import fetch_url, extract


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
        url_candidates = _website_candidates(url)
        for candidate in url_candidates:
            try:
                downloaded = fetch_url(candidate)
                if downloaded:
                    result = extract(
                        downloaded,
                        favor_recall=True,
                        favor_precision=False,
                        include_comments=False,
                        include_tables=True,
                        output_format="markdown",
                    )
                    if result:
                        return result
            except Exception as e:
                print("Exception for url: ", candidate, " --> ", e)
                continue

        return None
