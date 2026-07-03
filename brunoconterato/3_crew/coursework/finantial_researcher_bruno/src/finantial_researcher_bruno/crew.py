import os
from urllib.parse import urlparse
from typing import List

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import WebsiteSearchTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class FinantialResearcherBruno:
    """FinantialResearcherBruno crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @staticmethod
    def _ollama_model() -> str:
        return os.getenv("MODEL", "ollama/gemma4:e2b")

    @staticmethod
    def _ollama_base_url() -> str:
        return os.getenv("OLLAMA_API_BASE", os.getenv("API_BASE", "http://localhost:11434"))

    @staticmethod
    def _ollama_embedding_model() -> str:
        return os.getenv("EMBEDDINGS_OLLAMA_MODEL_NAME", "nomic-embed-text")

    @staticmethod
    def _ollama_embedding_url() -> str:
        return os.getenv(
            "EMBEDDINGS_OLLAMA_URL",
            f"{FinantialResearcherBruno._ollama_base_url().rstrip('/')}/api/embeddings",
        )

    def _ollama_llm(self) -> LLM:
        return LLM(
            model=self._ollama_model(),
            base_url=self._ollama_base_url(),
        )

    @staticmethod
    def _normalize_website_url(website: str) -> str:
        parsed = urlparse(website)
        if parsed.scheme:
            return website
        return f"https://{website.lstrip('/')}"

    def _website_search_tool(self) -> WebsiteSearchTool:
        class NormalizedWebsiteSearchTool(WebsiteSearchTool):
            def _run(
                self,
                search_query: str,
                website: str | None = None,
                similarity_threshold: float | None = None,
                limit: int | None = None,
            ) -> str:
                normalized_website = (
                    FinantialResearcherBruno._normalize_website_url(website)
                    if website is not None
                    else None
                )
                return super()._run(
                    search_query=search_query,
                    website=normalized_website,
                    similarity_threshold=similarity_threshold,
                    limit=limit,
                )

        return NormalizedWebsiteSearchTool(
            config={
                "embedding_model": {
                    "provider": "ollama",
                    "config": {
                        "url": self._ollama_embedding_url(),
                        "model_name": self._ollama_embedding_model(),
                    },
                }
            },
        )

    @agent
    def pesquisador_financeiro(self) -> Agent:
        return Agent(
            config=self.agents_config["pesquisador_financeiro"],
            llm=self._ollama_llm(),
            tools=[
                self._website_search_tool(),
            ],
            verbose=True,
        )

    @agent
    def analista_financeiro(self):
        return Agent(
            config=self.agents_config["analista_financeiro"],
            llm=self._ollama_llm(),
            verbose=True,
        )

    @task
    def pesquisa(self):
        return Task(config=self.tasks_config["pesquisa"], verbose=True)

    @task
    def analise(self):
        return Task(config=self.tasks_config["analise"], verbose=True)

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
        )
