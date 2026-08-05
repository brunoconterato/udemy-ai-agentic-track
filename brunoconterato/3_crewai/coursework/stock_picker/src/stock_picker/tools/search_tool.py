import json
from typing import Type

from crewai.tools import BaseTool
from ddgs import DDGS
from pydantic import BaseModel, Field


class SearchToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    query: str = Field(description="The query for a search")
    limit: int = Field(description="The max number of search items returned", default=5)


class SearchTool(BaseTool):
    name: str = "SearchTool"
    description: str = "This tool is used to search for a query in the web."
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str, limit: int) -> str:
        results = list(
            DDGS().text(query, safesearch="on", max_results=limit, backend="auto")
        )
        compact_results = [
            {
                "title": item.get("title"),
                "href": item.get("href"),
                "body": item.get("body"),
            }
            for item in results[:limit]
        ]
        return json.dumps(compact_results, ensure_ascii=False, indent=2)
