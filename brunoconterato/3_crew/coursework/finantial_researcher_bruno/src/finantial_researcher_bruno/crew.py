from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FinantialResearcherBruno():
    """FinantialResearcherBruno crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def pesquisador_financeiro(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisador_financeiro'], # type: ignore[index]
            verbose=True
        )
        
    @agent
    def analista_financeiro(self):
        return Agent(
            config=self.agents_config['analista_financeiro'],
            verbose=True
        )

    @task
    def pesquisa(self):
        return Task(
            config=self.tasks_config['pesquisa'],
            verbose=True
        )
        
    @task
    def analise(self):
        return Task(
            config=self.tasks_config['analise'],
            verbose=True
        )
        
    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
        )
