# CrewAI: Conceitos Fundamentais

O CrewAI é um framework para orquestrar agentes de IA autônomos que trabalham juntos de forma colaborativa. Ele é mais opinativo que o OpenAI Agents SDK, oferecendo uma estrutura robusta para definir papéis, tarefas e processos.

## 🚀 Começando um Projeto

Projetos CrewAI são, por padrão, projetos **UV** (um gerenciador de pacotes Python ultra-rápido).

- **Instalação do CLI:** `uv tool install --with crewai-tools crewai@latest`
- **Atualizar o CLI:** `uv tool upgrade crewai`
- **Ativar ambiente venv:** `source .venv/bin/activate`
- **Criar novo projeto:** `uv run --active crewai create crew meu_projeto --classic`
- **Executar o projeto:** `crewai run`

### CLI útil para esta sessão

Resumo curto dos comandos que mais ajudam nesta parte do curso:

- `crewai create crew <nome> --classic`: cria a estrutura inicial clássica de uma crew nova.
- `uv run --active crewai create crew <nome> --classic`: executa o criador usando o ambiente ativo do UV.
- `crewai install`: instala as dependências do projeto criado.
- `crewai run`: executa a crew com a configuração atual.
- `source .venv/bin/activate && crewai run`: ativa o venv local e roda a crew nele.
- `uv tool upgrade crewai`: atualiza a CLI instalada via `uv` para a versão mais recente disponível no índice.
- `crewai traces status`: mostra se a coleta de traces está ativa.
- `crewai traces enable` / `crewai traces disable`: liga ou desliga a coleta de traces nas execuções.
- `crewai test -n <iteracoes> [-m <modelo>]`: testa a crew algumas vezes e ajuda a comparar resultados.
- `crewai log-tasks-outputs`: mostra a saída mais recente das tasks executadas.
- `crewai replay -t <task_id>`: repete a execução a partir de uma task específica.

Nota: O comando oficial `uv tool install crewai` não funcionou. Utilizei `uv tool install --with crewai-tools crewai@latest` conforme [instruções](https://community.crewai.com/t/unable-to-install-crewai-no-executables-are-provided-by-crewai/6028/2)

### Cinco Passos Rápidos para Criar um Projeto

Siga estes cinco passos na 
ordem para criar, configurar e executar um projeto CrewAI de forma prática.

1. Criar o projeto
   - Execute: `uv run --active crewai create crew meu_projeto --classic`
   - Observação: esse comando gera a estrutura inicial clássica do projeto e usa o ambiente ativo do UV (veja a seção "Estrutura de Diretórios Recomendada" abaixo).

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

5. Executar

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

- **Atributos:** Possui um LLM próprio, função (role), meta (goal), contexto de fundo (backstory), memória e ferramentas (tools).

Nota: podemos pensar em um `Agent` como o `system prompt` dado ao LLM.

### 2. Task (Tarefa)

Uma atribuição específica a ser executada.

- **Atributos:** Descrição clara, expectativa de saída (output) e um agente responsável.

Nota: podemos pensar em uma `Task` como o `user prompt` dado ao `Agent`.

### 3. Crew (Equipe)

O conjunto de **Agentes** e **Tarefas** trabalhando em conjunto. Pode operar de duas formas:

- **Sequential (Sequencial):** As tarefas são executadas na ordem em que foram definidas.
- **Hierarchical (Hierárquico):** Um Agente Gerente (Manager LLM) atribui as tarefas aos agentes mais adequados.

---

## � Configuração via YAML (Recomendado)

Para projetos maiores, é comum utilizar arquivos `.yaml` para configurar os agentes. Isso facilita o ajuste de _prompts_ sem mexer no código Python.

Nota: em YAML, o `>` junta várias linhas em um único texto, trocando as quebras de linha por espaços.
Exemplo: `linha 1` > `linha 2` vira `linha 1 linha 2`.

**Arquivo: `src/meu_projeto/config/agents.yaml`**

```yaml
pesquisador_conteudo:
  role: >
    Pesquisador de Conteúdo
  goal: >
    Levantar informações confiáveis sobre o tema antes da escrita
  backstory: >
    Você é um analista cuidadoso, ótimo em encontrar fontes relevantes
    e identificar os pontos mais importantes de um assunto.

editor_seo:
  role: >
    Editor SEO
  goal: >
    Transformar a pesquisa em um texto claro, útil e otimizado para leitura online
  backstory: >
    Você escreve conteúdo objetivo, bem estruturado e pensado para quem quer
    aprender rápido sem perder profundidade.
```

**Arquivo: `src/meu_projeto/config/tasks.yaml`**

```yaml
mapear_tendencias:
  description: >
    Pesquise as principais tendências sobre {topico} e organize os achados em tópicos.
  expected_output: >
    Um resumo com 3 a 5 pontos principais, incluindo contexto e exemplos.
  agent: pesquisador_conteudo

escrever_artigo:
  description: >
    Escreva um artigo curto para blog usando a pesquisa como base, com título,
    introdução, subtítulos e conclusão.
  expected_output: >
    Um artigo pronto para publicação, com tom didático e leitura fluida.
  agent: editor_seo
```

**Arquivo: `src/meu_projeto/crew.py`**

**No arquivo `src/meu_projeto/crew.py`, o acesso fica assim:**
O CrewAI utiliza decoradores específicos para mapear as configurações do YAML para objetos Python de forma organizada.

- **`@agent`**: Define um método que retorna um Agente usando as configurações do YAML.
- **`@task`**: Define um método que retorna uma Tarefa, também vinculada ao YAML.
- **`@crew`**: Define o método que orquestra a equipe, unindo agentes e tarefas.

```python
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class SuaEquipe():
    # Arquivos de configuração usados por esta classe
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def pesquisador_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisador_conteudo'] # Chave do YAML
        )

    @agent
    def editor_seo(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_seo'] # Chave do YAML
        )

    @task
    def mapear_tendencias(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_tendencias'] # Chave do YAML das tarefas
        )

    @task
    def escrever_artigo(self) -> Task:
        return Task(
            config=self.tasks_config['escrever_artigo'] # Chave do YAML das tarefas
        )

    @crew
    def equipe(self) -> Crew:
        return Crew(
            agents=self.agents, # Vem de config/agents.yaml
            tasks=self.tasks,   # Vem de config/tasks.yaml
            process=Process.sequential
        )
```

---

## 💻 Exemplo Prático de Código (Via Código Direto)

Abaixo, um exemplo simplificado de como estruturar uma equipe básica no CrewAI:

**Arquivo: `src/meu_projeto/crew.py`**

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

### 4. Tools (Ferramentas)

`Tools` são recursos extras que um `Agent` pode usar para fazer algo além de gerar texto.

- **Ideia central:** o agente continua pensando e decidindo, mas agora pode consultar fontes, ler arquivos ou interagir com dados reais.
- **Quando usar:** quando o trabalho pede informação atualizada, leitura de conteúdo externo ou alguma ação fora do LLM.
- **Regra prática:** a `Tool` ajuda a executar a tarefa; ela não substitui a `Task`.

Exemplos de tools prontas do ecossistema CrewAI:

- `SerperDevTool`: busca na web.
- `ScrapeWebsiteTool`: lê o conteúdo de uma página.
- `FileReadTool`: lê arquivos locais.
- `DirectoryReadTool`: lê diretórios e lista arquivos.
- `CSVSearchTool`: consulta dados em arquivos CSV.
- `WebsiteSearchTool`: pesquisa conteúdo em sites.

Exemplo incremental, mudando só o `Agent`:

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

pesquisador = Agent(
    ...
    tools=[SerperDevTool(), ScrapeWebsiteTool()],
)
```

Aqui a ideia é simples: o agente pesquisa e abre páginas antes de responder. Se a `Task` não precisar de fonte externa, você pode deixar `tools=[]` ou nem declarar ferramentas.

### 5. Context (Contexto)

`Context` é a informação que uma tarefa ou agente recebe para trabalhar com continuidade.

- **Pode vir de:** saídas de tarefas anteriores, inputs passados na execução, memória do agente ou instruções explícitas.
- **Em uma crew sequencial:** o resultado de uma tarefa pode virar o contexto da próxima. É exatamente a ideia da aula: uma etapa depende da anterior e herda o que já foi produzido.
- **Ideia prática:** use `Context` quando uma tarefa depende do que já foi produzido antes, em vez de começar do zero.

Exemplo típico de `Task` com contexto de outra tarefa:

```python
from crewai import Task

mapear_tendencias = Task(
    description="Pesquise as principais tendências sobre IA aplicada a negócios.",
    expected_output="Um resumo com os 3 principais pontos encontrados.",
)

escrever_artigo = Task(
    description="Escreva um artigo curto com base na pesquisa anterior.",
    expected_output="Um artigo pronto para publicação.",
    context=[mapear_tendencias],
)
```

Aqui, `escrever_artigo` recebe como contexto o que foi produzido em `mapear_tendencias`, então ela não precisa repetir a pesquisa do zero.

### 6. Recursos avançados do CrewAI

Além dos conceitos base, o CrewAI também destaca alguns recursos que ajudam a organizar fluxos mais robustos. A ideia aqui não é decorar a API inteira, mas entender como cada recurso resolve um problema prático.

#### 6.1 Structured outputs

Use `structured outputs` quando você quer que a saída venha em um formato previsível, fácil de validar e consumir por código.

Exemplo simples com um modelo estruturado:

```python
from pydantic import BaseModel, Field
from crewai import Agent, Task


class ResumoTendencias(BaseModel):
    topico: str = Field(..., description="Tema analisado")
    pontos_chave: list[str] = Field(..., description="Lista com os achados principais")
    conclusao: str = Field(..., description="Resumo final curto")


pesquisador = Agent(
    role="Pesquisador de Mercado",
    goal="Encontrar tendências sobre IA aplicada a negócios",
    backstory="Você organiza informações de forma clara e objetiva.",
)

tarefa = Task(
    description="Analise o tema e devolva um resumo estruturado.",
    expected_output="Um objeto com topico, pontos_chave e conclusao.",
    agent=pesquisador,
    output_pydantic=ResumoTendencias,
)
```

Na prática, isso é útil quando a próxima etapa precisa ler os dados sem fazer parsing de texto livre.

#### 6.2 Custom tool

Use uma `custom tool` quando o agente precisa acessar uma fonte ou executar uma ação específica de forma controlada.

Exemplo de tool simples para consultar uma lista local:

```python
from crewai_tools import BaseTool


class BuscarGlossarioTool(BaseTool):
    name: str = "buscar_glossario"
    description: str = "Procura um termo em um glossário local e retorna a definição."

    def _run(self, termo: str) -> str:
        glossario = {
            "agent": "Entidade que toma decisões com base em um objetivo.",
            "task": "Trabalho específico atribuído a um agente.",
        }
        return glossario.get(termo.lower(), "Termo não encontrado.")


pesquisador = Agent(
    role="Pesquisador",
    goal="Explicar conceitos do curso de forma simples",
    tools=[BuscarGlossarioTool()],
)
```

Aqui o agente continua decidindo, mas agora consulta uma fonte confiável e limitada por nós.

#### 6.3 Hierarchical process

Use `hierarchical process` quando você quer que um agente gerente distribua o trabalho e acompanhe a execução dos demais.

Exemplo conceitual:

```python
from crewai import Agent, Task, Crew, Process

gerente = Agent(
    role="Manager",
    goal="Organizar as tarefas e decidir a melhor ordem de execução",
)

pesquisador = Agent(role="Pesquisador", goal="Levantar dados relevantes")
redator = Agent(role="Redator", goal="Transformar a pesquisa em texto final")

tarefa1 = Task(description="Pesquisar o tema", agent=pesquisador)
tarefa2 = Task(description="Escrever o relatório", agent=redator)

equipe = Crew(
    agents=[gerente, pesquisador, redator],
    tasks=[tarefa1, tarefa2],
    process=Process.hierarchical,
    manager_agent=gerente,
)
```

Esse modelo faz mais sentido quando existem várias etapas e você quer mais coordenação do que uma simples sequência fixa.

#### 6.4 Unified memory

Use `unified memory` quando a crew precisa lembrar preferências, contexto ou decisões anteriores ao longo da conversa.

Exemplo simplificado:

```python
from crewai import Agent, Task, Crew, Process

atendente = Agent(
    role="Assistente",
    goal="Responder sempre considerando o histórico do usuário",
    memory=True,
)

tarefa = Task(
    description="Responder à dúvida atual com base no histórico disponível.",
    agent=atendente,
)

equipe = Crew(
    agents=[atendente],
    tasks=[tarefa],
    process=Process.sequential,
    memory=True,
)
```

Isso ajuda a evitar repetições e deixa a experiência mais consistente quando a interação acontece em várias etapas.

Em resumo, esses recursos são extensões naturais dos conceitos de `Agent`, `Task`, `Tools` e `Context`:

- `Structured outputs` deixam a saída previsível.
- `Custom tool` conecta o agente a ações ou fontes específicas.
- `Hierarchical process` adiciona coordenação entre agentes.
- `Unified memory` mantém continuidade entre interações.

### Tracing

`Tracing` ajuda a acompanhar a execução do crew com mais clareza, principalmente quando você quer entender decisões, uso de tools e sequência das tasks.

Fluxo que funciona neste projeto:

1. Crie conta em `https://app.crewai.com` e faça login manualmente no navegador.
2. No terminal do subprojeto, rode `uv run crewai login` para conectar a conta local.
3. O CLI deve abrir uma página no navegador com um código de confirmação.
4. Confira se o código mostrado no navegador bate com o código exibido no terminal.
5. Autorize o acesso.
6. Ative o tracing com `tracing=True` no `Crew` ou com `CREWAI_TRACING_ENABLED=true` no ambiente.

Exemplo de configuração mínima:

```python
from crewai import Crew

equipe = Crew(
  agents=[pesquisador, redator],
  tasks=[tarefa_pesquisa, tarefa_escrita],
  process=Process.sequential,
  tracing=True,
)
```

E, no `.env`:

```text
CREWAI_TRACING_ENABLED=true
```

Quando tudo estiver certo, o terminal deve terminar com algo parecido com:

```text
You are now authenticated to the tool repository for organization '...'
Welcome to CrewAI AMP
```

Com isso, os traces passam a aparecer no dashboard do CrewAI AMP e você consegue inspecionar decisões do agente, timeline das tasks, uso de tools e chamadas ao LLM.

---

_Nota: CrewAI permite um alto nível de prescrição, permitindo que você defina fluxos de trabalho complexos e comportamentos específicos para cada componente._

### 7. 
