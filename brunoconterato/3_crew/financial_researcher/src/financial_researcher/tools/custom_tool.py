from crewai.tools import tool
import httpx
from trafilatura import fetch_url, extract


def extract_html_txt(body: str) -> str:
    return (
        extract(
            fetch_url(body),
            no_fallback=True,
            include_comments=False,
            include_links=False,
            include_formatting=False,
            include_images=False,
            include_tables=True,
            fast=True,
            favor_precision=True,
        )
        or ""
    )


@tool("search_web_async")
async def search_web_async(query: str) -> str:
    """Asyncronously search the web based on the query."""

    async with httpx.AsyncClient() as client:
        try:
            print(f"\n\nSearching query: {query}\n\n")
            response = await client.get(
                "http://localhost:4479/search/text",
                params={"query": query, "max_results": 5},
            )
            response.raise_for_status()
            print(f"\n\nResponse from search tool: {response.json()}\n\n")
            results_arr = [
                f"Title: {r['title']}\nBody: {extract_html_txt(r['href'])}"
                for r in response.json()["results"]
            ]
            print(f"\n\nResults arr [0]: {results_arr[0]}\n\n")
            return "\n\n".join(results_arr)
        except Exception as e:
            return f"Search failed: {str(e)}"
