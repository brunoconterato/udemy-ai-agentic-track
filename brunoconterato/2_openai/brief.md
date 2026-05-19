# OpenAI Agents SDK

## Terminologia minimalista para agentes de IA

O OpenAI Agents SDK foca em uma visão simples e prática para criar fluxos com agentes.

### 1. Agents

- Agentes são instâncias de LLMs com instruções e contexto.
- Eles executam tarefas, respondem a prompts e tomam decisões.
- Pense neles como a “mente” do sistema.

### 2. Guardrails

- Guardrails são regras e limites que controlam o comportamento do agente.
- Eles evitam respostas indesejadas ou fora do escopo.
- Funcionam como segurança e alinhamento.

### 3. Tools

- Tools são capacidades auxiliares que o agente pode chamar.
- Elas funcionam como funções ou serviços externos.
- O agente chama a tool, recebe o resultado e continua sua execução.

### 4. Handoffs

- Handoffs são delegações de controle entre agentes.
- Um agente passa a tarefa para outro agente especializado.
- O segundo agente assume a execução e pode continuar o fluxo.

---

## Diferença direta: tools vs handoffs

- `tools` ampliam um agente com ações auxiliares e retornam ao agente original.
- `handoffs` transferem o trabalho para outro agente, deslocando o controle.

Ou seja:

- com ferramentas, o agente mantém o controle e usa capacidades externas;
- com handoffs, o agente entrega a tarefa e deixa outro agente conduzir.

Essa distinção é central para construir pipelines de agentes eficientes.

---

## Antes de começar

Importe os elementos principais e carregue variáveis de ambiente:

```python
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
import asyncio

load_dotenv(override=True)
```

Use `trace()` para acompanhar a execução, entender dependências e depurar o fluxo.

---

## Fluxo básico de um agente

1. Criar o agente com `Agent(...)`.
2. Executar com `Runner.run(...)`.
3. Inspecionar com `trace(...)`.

```python
agent = Agent(
    name="ResumoAgent",
    instructions="Resuma o texto de forma clara",
    model="gpt-4o-mini"
)

with trace("Resumo"):
    result = Runner.run(agent, "Explique o papel dos agentes de IA")

print(result.final_output)
```

---

## Executando com Ollama

O notebook usa uma conexão local ao Ollama via `AsyncOpenAI` e `OpenAIChatCompletionsModel`.
O código de configuração é similar a este:

```python
from agents import OpenAIChatCompletionsModel, AsyncOpenAI, ModelSettings

external_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
model = OpenAIChatCompletionsModel(model="qwen2.5", openai_client=external_client)

agent = Agent(
    name="Jokester",
    instructions="You are a joke teller",
    model=model,
    model_settings=ModelSettings(temperature=0.9),
)
```

O fluxo é:

1. Inicie o Ollama localmente e exponha o endpoint HTTP no `localhost:11434`.
2. Use `AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")` para apontar o cliente para o Ollama.
3. Defina o modelo com `OpenAIChatCompletionsModel(model="qwen2.5", openai_client=external_client)` para corresponder ao modelo carregado no Ollama.
4. Execute o agente com `Runner.run(agent, prompt)` como no exemplo acima.

Se o Ollama estiver rodando em outra porta ou host, ajuste `base_url` para o endpoint correto do servidor Ollama.

## Vibe Coding

A imagem destaca uma abordagem prática e ágil para trabalhar com LLMs, chamada `vibe coding`.

- **Prompt curto e direto**: mantenha prompts curtos e peça respostas diretas, preferindo APIs e datas atualizadas.
- **Confirme com outro modelo**: consulte dois LLMs para a mesma pergunta e compare respostas.
- **Quebre em etapas**: divida o pedido em etapas menores e independentes para testar cada parte.
- **Revise com uma segunda checagem**: peça uma resposta e depois use outro modelo para checar ou revisar.
- **Compare múltiplas alternativas**: solicite três soluções para o mesmo problema e escolha a melhor.

Essa mentalidade ajuda a trabalhar com IA de forma mais segura e eficaz, mantendo rapidez, comparação e validação em cada interação.

---

## Criação de agentes colaborativos

É comum criar vários agentes com diferentes estilos ou funções:

```python
agent1 = Agent(name="Formal", instructions="Escreva formalmente", model="gpt-4o-mini")
agent2 = Agent(name="Criativo", instructions="Escreva de forma criativa", model="gpt-4o-mini")

results = await asyncio.gather(
    Runner.run(agent1, "Gere um parágrafo"),
    Runner.run(agent2, "Gere um parágrafo")
)

outputs = [r.final_output for r in results]
```

Um agente avaliador pode comparar as saídas e escolher a melhor opção.

---

## Ferramentas em agentes

Declare ferramentas genéricas com `@function_tool`:

```python
@function_tool
def format_text(text: str) -> dict:
    return {"formatted": text.strip()}
```

Também é possível converter um agente em tool:

```python
writer_agent = Agent(name="Writer", instructions="Gere texto curto", model="gpt-4o-mini")
writer_tool = writer_agent.as_tool(
    tool_name="writer_tool",
    tool_description="Gera texto curto"
)
```

Use as tools dentro de outro agente:

```python
planner = Agent(
    name="Planner",
    instructions="Use as ferramentas para criar a melhor resposta",
    tools=[writer_tool, format_text],
    model="gpt-4o-mini"
)
```

---

## Handoffs entre agentes

Handoffs são úteis quando você quer delegar o trabalho a outro agente especializado.

```python
formatter = Agent(name="Formatter", instructions="Formate o texto em HTML", model="gpt-4o-mini")
manager = Agent(
    name="Manager",
    instructions="Escolha a melhor resposta e passe para o Formatter",
    tools=[writer_tool],
    handoffs=[formatter],
    model="gpt-4o-mini"
)
```

Nesse caso, o `manager` gera o conteúdo e entrega para o `formatter`, que assume a continuação.

---

## Boas práticas rápidas

- Use instruções claras e específicas.
- Divida o fluxo em agentes com responsabilidades distintas.
- Compare saídas de agentes diferentes.
- Use `trace()` para entender cada etapa.
- Seja explícito ao definir tools e handoffs.

---

## Resumo rápido

- **Agents**: instâncias de LLMs com instruções.
- **Tools**: ações auxiliares que retornam resultados ao agente original.
- **Handoffs**: delegação de tarefa para outro agente.
- **Guardrails**: regras que limitam comportamento.
- **Trace**: rastreamento e depuração do fluxo.
