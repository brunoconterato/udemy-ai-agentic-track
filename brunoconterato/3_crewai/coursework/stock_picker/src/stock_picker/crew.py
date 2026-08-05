from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from stock_picker.tools.fetch_html_tool import FetchHTMLTool
from stock_picker.tools.search_tool import SearchTool

from stock_picker.model import (
    TrendingStocksList,
    TrendingCompaniesResearchList,
    SelectedCompany,
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
            max_iter=6,
            max_retry_limit=2,
            # memory=True,
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],  # type: ignore[index]
            verbose=True,
            # memory=True,
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],
            verbose=True,
            memory=True,
        )

    @task
    def find_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies_task"],  # type: ignore[index]
            output_file="report/trending_companies+{current_date}.md",
            output_pydantic=TrendingStocksList,
        )

    @task
    def research_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies_task"],  # type: ignore[index]
            output_file="report/trending_companies_research_{current_date}.md",
            output_pydantic=TrendingCompaniesResearchList,
        )

    @task
    def pick_best_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company_task"],  # type: ignore[index]
            output_file="report/best_company_{current_date}.md",
            output_pydantic=SelectedCompany,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        stock_picker_manager = Agent(
            role="Workflow Manager",
            goal="Orchestrate entire task execution across agents and handle complex decision-making.",
            backstory="""You are the chief manager of a stock analysis crew. You have full control to delegate, oversee progress, reassign tasks when needed based on each agent's strengths, coordinate between financial research teams like 'trending_company_finder' and 'financial_researcher', review final recommendations from the 'stock_picker', resolve conflicts in findings or strategy shifts during market trends changes.""",
            allow_delegation=True,  # Enabled to delegate subtasks across other agents when needed dynamically. You have ultimate authority over workflow control.
            max_iter=6,  # Keep manager iterations reasonable for orchestration loops without excessive retries.
            embedder={
                "provider": "ollama",
                "config": {
                    "model_name": "nomic-embed-text:latest",
                    "url": "http://localhost:11434/api/embeddings",
                },
            },
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=stock_picker_manager,
            verbose=True,
            memory=True,
            embedder={
                "provider": "ollama",
                "config": {
                    "model_name": "nomic-embed-text:latest",
                    "url": "http://localhost:11434/api/embeddings",
                },
            },
        )
