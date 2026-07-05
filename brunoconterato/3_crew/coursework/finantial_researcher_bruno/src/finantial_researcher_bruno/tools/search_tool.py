from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from ddgs import DDGS


class SearchToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    query: str = Field(description="The query for a search")
    limit: int = Field(description="The max number of search items returned", default=5)


class SearchTool(BaseTool):
    name: str = "SearchTool"
    description: str = "This tool is used to search for a query in the web."
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str, limit: int) -> str:
        print("argument", query)
        results = DDGS().text(query, safesearch="on", page=1, backend="auto")
        print(results)
        return results
