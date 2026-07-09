from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from .tools.fetch_html_tool import FetchHTMLTool
from .tools.search_tool import SearchTool


from pydantic import BaseModel, Field


class TrendingStock(BaseModel):
    """Uma empresa que está nos noticiários e chama a atenção de investidores"""

    name: str = Field(description="Nome da empresa")
    ticker: str = Field(description="Símbolo oficial da ação na bolsa de valores")
    description: str = Field(description="Descrição da atividade da empresa")
    reasons: List[str] = Field(
        description="Lista de motivos que justificam existência de tendência"
    )


class TrendingStockList(BaseModel):
    """Lista de empresas que estão se destacando nas notícias"""

    companies: List[TrendingStock] = Field(
        description="Lista de empresas que se destacam nas notícias e chamam atenção de investidores",
        min_length=2,
        max_length=3,
    )


class TrendingCompanyResearch(BaseModel):
    name: str = Field(description="Nome da empresa")
    market_position: str = Field(
        description="Posição atual no mercado e análise competitiva"
    )
    future_outlook: str = Field(description="Perspectiva de futuro e de crescimento")
    investment_potential: str = Field(
        description="Potencial e adequação de investimento"
    )


class TrendindCompanyResearchList(BaseModel):
    companies: List[TrendingCompanyResearch] = Field(
        description="Lista de análises de empresas mostrando potencial de crescimento inferido",
        min_length=2,
        max_length=3,
    )


class SelectedCompany(BaseModel):
    name: str = Field(description="Nome da empresa")
    ticker: str = Field(description="Símbolo da empresa na bolsa de valores")
    description: str = Field(description="Descrição da atividade da empresa")
    reasonns: List[str] = Field(
        description="Lista de razões pelos quais a empresa possui potencial de crescimento"
    )


@CrewBase
class StockPicker:
    """StockPicker crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_company_finder"],  # type: ignore[index]
            verbose=True,
            tools=[SearchTool(), FetchHTMLTool()],
            output_pydantic=TrendingStockList,
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],  # type: ignore[index]
            verbose=True,
            output_pydantic=TrendindCompanyResearchList,
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],
            verbose=True,
            output_pydantic=SelectedCompany,
        )

    @task
    def find_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies_task"],  # type: ignore[index]
            output_file="report/trending_companies+{current_date}.md",
        )

    @task
    def research_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies_task"],  # type: ignore[index]
            output_file="report/trending_companies_research_{current_date}.md",
        )

    @task
    def pick_best_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company_task"],  # type: ignore[index]
            output_file="report/best_company_{current_date}.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
