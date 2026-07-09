from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from .tools.fetch_html_tool import FetchHTMLTool
from .tools.search_tool import SearchTool


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
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config["stock_picker"], verbose=True)

    @task
    def find_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies_task"],  # type: ignore[index]
            output_file="trending_companies+{current_date}.md",
        )

    @task
    def research_trending_companies_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies_task"],  # type: ignore[index]
            output_file="trending_companies_research_{current_date}.md",
        )

    @task
    def pick_best_company_task(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company_task"],  # type: ignore[index]
            output_file="best_company_{current_date}.md",
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
