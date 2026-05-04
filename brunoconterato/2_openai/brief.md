# OpenAI Agents SDK

## Terminologia Minimalista do OpenAI Agents SDK

O OpenAI Agents SDK utiliza uma terminologia simples e direta para explicar como os agentes funcionam. Essa abordagem reduz a complexidade e facilita a compreensão dos conceitos centrais.

---

### 1. Agents (Agentes)

- **O que são**: agentes representam modelos de linguagem (LLMs).
- **Papel**: são a “mente” que processa texto, gera respostas e toma decisões com base em prompts e contexto.
- **Por que importa**: quando falamos de um agente, estamos nos referindo a uma instância de IA que executa tarefas conversacionais ou de raciocínio.

---

### 2. Handoffs (Transferências)

- **O que são**: handoffs representam interações.
- **Papel**: descrevem como a conversa ou o trabalho é passado entre agentes, entre o usuário e o agente, ou entre diferentes componentes de um fluxo.
- **Por que importa**: em sistemas com múltiplos agentes, o handoff define a transição de controle e de informação de uma parte para outra.

---

### 3. Guardrails (Trilhos de proteção)

- **O que são**: guardrails representam controles.
- **Papel**: servem para limitar comportamentos, impor regras de segurança e garantir que o agente opere dentro de parâmetros aceitáveis.
- **Por que importa**: garantem respostas mais seguras, apropriadas e alinhadas com as intenções desejadas.

---

## Resumo

A terminologia minimalista do SDK foca em três conceitos essenciais:

- **Agents = LLMs**
- **Handoffs = Interações**
- **Guardrails = Controles**

Essa simplicidade ajuda a entender rapidamente como estruturar agentes no OpenAI Agents SDK, especialmente ao começar a trabalhar com orquestração de IA e fluxos de conversação.

---

## Três passos para usar um agente

O fluxo básico no SDK segue três passos simples, conforme a imagem:

1. Criar uma instância de `Agent`
2. Usar `with trace()` para acompanhar o agente
3. Chamar `runner.run()` para executar o agente

### Exemplo simplificado

```python
from openai_agents import Agent, runner

agent = Agent(model="gpt-4.1")

with trace(agent) as trace_data:
    result = runner.run(agent, "Explique a terminologia minimalista do SDK.")

print(result)
print(trace_data)
```

Nesse exemplo:

- `Agent(...)` cria o agente que usa o modelo de linguagem.
- `with trace(agent)` habilita o rastreamento da execução do agente.
- `runner.run(agent, prompt)` dispara a execução do agente com o prompt dado.

Essa sequência demonstra de forma didática como inicializar, monitorar e rodar um agente no OpenAI Agents SDK.

---

## Executando com Ollama

O notebook usa uma conexão local ao Ollama via `AsyncOpenAI` e `OpenAIChatCompletionsModel`.
O código de configuração é similar a este:

```python
from agents import OpenAIChatCompletionsModel, AsyncOpenAI, ModelSettings

external_client = AsyncOpenAI(base_url="http://localhost:11434/v1")
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
2. Use `AsyncOpenAI(base_url="http://localhost:11434/v1")` para apontar o cliente para o Ollama.
3. Defina o modelo com `OpenAIChatCompletionsModel(model="qwen2.5", openai_client=external_client)` para corresponder ao modelo carregado no Ollama.
4. Execute o agente com `Runner.run(agent, prompt)` como no exemplo acima.

Se o Ollama estiver rodando em outra porta ou host, ajuste `base_url` para o endpoint correto do servidor Ollama.
