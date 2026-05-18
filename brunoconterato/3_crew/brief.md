# CrewAI: Conceitos Fundamentais

O CrewAI é um framework para orquestrar agentes de IA autônomos que trabalham juntos de forma colaborativa. Ele é mais opinativo que o OpenAI Agents SDK, oferecendo uma estrutura robusta para definir papéis, tarefas e processos.

## 🚀 Começando um Projeto

Projetos CrewAI são, por padrão, projetos **UV** (um gerenciador de pacotes Python ultra-rápido).

- **Instalação do CLI:** `uv tool install --with crewai-tools crewai@0.121.1`
- **Criar novo projeto:** `crewai create crew meu_projeto`
- **Executar o projeto:** `crewai run`

Nota: O comando oficial `uv tool install crewai` não funcionou. Utilizei `uv tool install --with crewai-tools crewai@0.121.1` conforme [instruções](https://community.crewai.com/t/unable-to-install-crewai-no-executables-are-provided-by-crewai/6028/2)

### Cinco Passos Rápidos para Criar um Projeto

Siga estes cinco passos na ordem para criar, configurar e executar um projeto CrewAI de forma prática.

1. Criar o projeto
   - Execute: `crewai create crew meu_projeto`
   - Observação: esse comando gera a estrutura inicial do projeto (veja a seção "Estrutura de Diretórios Recomendada" abaixo).

2. Preencher os arquivos de configuração (YAML)
   - Edite `src/meu_projeto/config/agents.yaml` e `src/meu_projeto/config/tasks.yaml` para definir seus **Agents** e **Tasks**.
   - Consulte a seção **Configuração via YAML (Recomendado)** para exemplos e convenções de chave.

3. Completar o `crew.py`
   - Implemente os métodos com os decoradores `@agent`, `@task` e `@crew`, inicializando `Agent` e `Task` a partir das chaves do YAML.
   - Veja o exemplo em "Como acessar no Python" e em "Exemplo Prático de Código" abaixo.

4. Atualizar o `main.py`
   - Configure variáveis de ambiente, caminhos de config (se necessário) e inicie a execução da crew.
   - Exemplo mínimo de `main.py`:

```python
from src.meu_projeto.crew import SuaEquipe

if __name__ == "__main__":
  equipe = SuaEquipe()
  crew = equipe.equipe()
  crew.kickoff(inputs={'topico': 'IA Agentica'})
```

1. Executar

- Execute o projeto com: `crewai run`
- Alternativamente teste localmente com: `python -m src.meu_projeto.main`

### Estrutura de Diretórios Recomendada

Ao criar um projeto via CLI, o CrewAI gera automaticamente uma estrutura organizada:

```text
meu_projeto/
├── src/
│   └── meu_projeto/
│       ├── config/
│       │   ├── agents.yaml  # Definição das personas
│       │   └── tasks.yaml   # Definição das missões
│       ├── crew.py          # Lógica de orquestração (decoradores)
│       └── main.py          # Ponto de entrada do projeto
├── pyproject.toml
└── ...
```

## 🧩 Conceitos Core

### Formas de Configuração

Agentes e Tarefas podem ser definidos de duas maneiras principais:

1. **Via Código:** Diretamente no script Python (como no exemplo abaixo).
2. **Via Arquivos YAML:** Uma abordagem mais limpa e organizada, separando a lógica do código das definições de persona e instruções.

### 1. Agent (Agente)

Uma unidade autônoma que atua como um "membro da equipe".

- **Atributos:** Possui um LLM próprio, função (role), meta (goal), backstory (contexto de fundo), memória e ferramentas (tools).

### 2. Task (Tarefa)

Uma atribuição específica a ser executada.

- **Atributos:** Descrição clara, expectativa de saída (output) e um agente responsável.

### 3. Crew (Equipe)

O conjunto de **Agentes** e **Tarefas** trabalhando em conjunto. Pode operar de duas formas:

- **Sequential (Sequencial):** As tarefas são executadas na ordem em que foram definidas.
- **Hierarchical (Hierárquico):** Um Agente Gerente (Manager LLM) atribui as tarefas aos agentes mais adequados.

---

## � Configuração via YAML (Recomendado)

Para projetos maiores, é comum utilizar arquivos `.yaml` para configurar os agentes. Isso facilita o ajuste de _prompts_ sem mexer no código Python.

**Exemplo de `agents.yaml`:**

```yaml
researcher:
  role: >
    Senior Financial Researcher
  goal: >
    Research companies, news and potential
  backstory: >
    You're a seasoned financial researcher with a
    talent for finding the most relevant information.
  llm: openai/gpt-4o-mini
```

**Como acessar no Python:**
O CrewAI utiliza decoradores específicos para mapear as configurações do YAML para objetos Python de forma organizada.

- **`@agent`**: Define um método que retorna um Agente usando as configurações do YAML.
- **`@task`**: Define um método que retorna uma Tarefa, também vinculada ao YAML.
- **`@crew`**: Define o método que orquestra a equipe, unindo agentes e tarefas.

```python
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class SuaEquipe():
    # Caminhos para os arquivos de configuração
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def pesquisador_financeiro(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'] # Chave do YAML
        )

    @task
    def tarefa_de_pesquisa(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'] # Chave do YAML das tarefas
        )

    @crew
    def equipe(self) -> Crew:
        return Crew(
            agents=self.agents, # Coleta todos os métodos decorados com @agent
            tasks=self.tasks,   # Coleta todos os métodos decorados com @task
            process=Process.sequential
        )
```

---

## 💻 Exemplo Prático de Código (Via Código Direto)

Abaixo, um exemplo simplificado de como estruturar uma equipe básica no CrewAI:

```python
from crewai import Agent, Task, Crew, Process

# 1. Definindo os Agentes
pesquisador = Agent(
  role='Pesquisador de Mercado',
  goal='Encontrar as tendências mais recentes em {topico}',
  backstory='Você é um especialista em análise de dados e tendências tecnológicas.',
  verbose=True,
  allow_delegation=False
)

redator = Agent(
  role='Redator de Conteúdo',
  goal='Escrever um post de blog informativo sobre {topico}',
  backstory='Você é um escritor talentoso que transforma dados complexos em artigos simples.',
  verbose=True
)

# 2. Definindo as Tarefas
tarefa_pesquisa = Task(
  description='Analise as 3 principais tendências de {topico} em 2024.',
  expected_output='Um relatório detalhado com 3 bullet points.',
  agent=pesquisador
)

tarefa_escrita = Task(
  description='Crie um post para o LinkedIn com base no relatório de pesquisa.',
  expected_output='Um post formatado para redes sociais.',
  agent=redator
)

# 3. Orquestrando a Equipe (Crew)
equipe = Crew(
  agents=[pesquisador, redator],
  tasks=[tarefa_pesquisa, tarefa_escrita],
  process=Process.sequential # Execução sequencial: pesquisa -> escrita
)

# Executando o processo
resultado = equipe.kickoff(inputs={'topico': 'IA Agentica'})
print(resultado)
```

---

_Nota: CrewAI permite um alto nível de prescrição, permitindo que você defina fluxos de trabalho complexos e comportamentos específicos para cada componente._
