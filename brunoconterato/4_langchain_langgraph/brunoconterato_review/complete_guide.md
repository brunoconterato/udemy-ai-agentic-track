# Guia completo — LangChain `create_agent`, Tools, Middleware, Memória, HITL e Gradio

Guia de estudo e implementação · APIs atuais do LangChain 1.x, LangGraph e Gradio · Revisado em novembro de 2026

O foco é entender onde cada componente é definido, como é conectado ao agente e como seu resultado chega ao próximo componente.

## 1. O que você vai aprender

O guia apresenta tools, memória, middleware e aprovação humana (HITL), até a integração do agente com uma interface Gradio.

## 2. Mapa completo da arquitetura

```text
Usuário
   │ mensagem / decisão
   ▼
Gradio (interface, callbacks e gr.State)
   │ agent.invoke(...) / Command(resume=...)
   ▼
create_agent — grafo executado pelo LangGraph
   │
   ├── Modelo ◄──── mensagens e resultados das tools
   │     │ tool calls
   │     ▼
   ├── Middleware ── HITL ── interrupt ──► Gradio
   │     │                ◄── decisão humana
   │     ▼
   ├── Tools ── ToolRuntime ──► State, Context, Store e Config
   │
   ├── AgentState ◄── Checkpointer (estado por thread)
   └── Store (dados compartilhados entre threads)
```

### As quatro operações fundamentais

Para compreender qualquer componente, pergunte:

| Etapa       | Pergunta                    | Exemplo                     |
| ----------- | --------------------------- | --------------------------- |
| Definição   | Onde ele é criado?          | `@tool def somar(...)`      |
| Registro    | Onde é conectado ao agente? | `tools=[somar]`             |
| Acionamento | Quem o chama?               | O runtime, após `tool_call` |
| Resultado   | Para onde volta?            | `ToolMessage` → modelo      |

Esse mesmo raciocínio será aplicado ao middleware, à memória e ao Gradio.

## 3. Pré-requisitos e instalação

Usando `uv`:

```bash
uv init agente-estudo
cd agente-estudo

uv add "langchain>=1.4.6" langgraph langchain-openai gradio
```

Configure sua chave de API:

```bash
export OPENAI_API_KEY="sua-chave"
```

Nos exemplos, utilizaremos:

```python
MODEL = "openai:gpt-5.5"
```

O modelo deve suportar tool calling. A escolha de modelo é independente da implementação de memória, middleware ou Gradio.

## 4. Conceito central: `create_agent`

O `create_agent` constrói um agente sobre LangGraph.

```python
from langchain.agents import create_agent
agent = create_agent(
    model=MODEL,
    tools=[],
)
```

Para executar:

```python
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Olá"}
    ]})
print(result["messages"][-1].content)
```

### Quem executa o quê?

```text
Seu código
    │
    └── agent.invoke(...)
             │
             ├── LangGraph executa os nós do agente
             │
             ├── LangChain chama o LLM
             │
             ├── LLM pode gerar tool_calls
             │
             ├── LangChain executa tools
             │
             ├── Resultados viram ToolMessages
             │
             └── LLM continua até concluir
```

Não precisa escrever um loop `while` para executar tool calls.

## 5. Tools: funções que o modelo pode solicitar

### 5.1. Definição

```python
from langchain.tools import tool

@tool
def somar(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b
```

### 5.2. Registro

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
)
```

### 5.3. Acionamento

```python
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Some 20 e 30."}
    ]})
```

Se o modelo solicitar:

```python
{
    "name": "somar",
    "args": {"a": 20, "b": 30},
}
```

o runtime executa `somar(a=20, b=30)`, cria o `ToolMessage` com o resultado e devolve a informação ao modelo.

Não é necessário:

```python
somar.invoke(...)
```

após a resposta do modelo.

### 5.4. Estrutura das mensagens

```text
HumanMessage
    "Some 20 e 30"

AIMessage
    tool_calls=[somar(a=20, b=30)]

ToolMessage
    content="50"

AIMessage
    content="O resultado é 50."
```

Essas mensagens também podem compor a memória de curto prazo.

## 6. `AgentState`, `Context`, `Checkpointer`, `Store` e `ToolRuntime`

Esses conceitos devem ser separados.

| Objeto         | Finalidade                           | Quem fornece       |
| -------------- | ------------------------------------ | ------------------ |
| `AgentState`   | Estado mutável da conversa           | Agente/LangGraph   |
| `Context`      | Dados de uma invocação               | Sua aplicação      |
| `Checkpointer` | Salvar e recuperar o estado          | Sua configuração   |
| `Store`        | Dados persistentes entre threads     | Sua configuração   |
| `ToolRuntime`  | Acesso aos recursos dentro das tools | Injeção automática |

### 6.1. Memória curta com `Checkpointer`

Definição:

```python
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    checkpointer=checkpointer,
)
```

Identificação da conversa:

```python
config = {
    "configurable": {
        "thread_id": "conversa-123"
    }}
```

Execução:

```python
agent.invoke(
    {"messages": [
        {"role": "user", "content": "Meu nome é Bruno."}
    ]},
    config=config,
)
result = agent.invoke(
    {"messages": [
        {"role": "user", "content": "Qual é meu nome?"}
    ]},
    config=config,
)
```

A segunda chamada recupera o histórico da mesma thread. O estado é atualizado durante o fluxo, inclusive quando tools são executadas.

### 6.2. `Context`: informações da execução

Definição:

```python
from dataclasses import dataclass

@dataclass
class Context:
    user_id: str
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    context_schema=Context,
)
```

Fornecimento:

```python
agent.invoke(
    {"messages": [
        {"role": "user", "content": "Olá"}
    ]},
    context=Context(user_id="usuario-123"),
)
```

O `Context` é particularmente útil para dados como identificadores de usuários, permissões e configurações da invocação.

### 6.3. Memória longa com `Store`

Definição:

```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    store=store,
    context_schema=Context,
)
```

O `Store` armazena informações entre threads. Ao contrário do `Checkpointer`, ele não representa necessariamente o histórico completo de uma conversa.

### 6.4. `ToolRuntime`: a conexão interna

O `ToolRuntime` é um objeto que o LangChain injeta na função.

```python
from langchain.tools import tool, ToolRuntime

@tool
def contar_mensagens(runtime: ToolRuntime) -> int:
    """Conta mensagens da conversa."""
    return len(runtime.state["messages"])
```

O modelo não precisa preencher `runtime`.

Além de `runtime.state`, uma tool pode utilizar `runtime.context`, `runtime.store`, `runtime.config` e `runtime.tool_call_id`.

### 6.5. Tools acessando memória longa

```python
@tool
def salvar_preferencia(
    chave: str,
    valor: str,
    runtime: ToolRuntime[Context],) -> str:
    """Salva uma preferência do usuário."""
    user_id = runtime.context.user_id
    runtime.store.put(
        ("usuarios", user_id),
        chave,
        {"valor": valor},
    )
    return "Preferência salva."@tool
def consultar_preferencia(
    chave: str,
    runtime: ToolRuntime[Context],) -> str:
    """Consulta uma preferência do usuário."""
    user_id = runtime.context.user_id
    item = runtime.store.get(
        ("usuarios", user_id),
        chave,
    )
    return item.value["valor"] if item else "Não encontrada."
```

Conexão no agente:

```python
agent = create_agent(
    model=MODEL,
    tools=[
        salvar_preferencia,
        consultar_preferencia,
    ],
    store=store,
    context_schema=Context,
)
```

Acionamento:

```python
agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "Guarde que prefiro respostas curtas."
    }]},
    context=Context(user_id="usuario-123"),
)
```

O modelo precisa decidir chamar a tool. A mera presença de `store=store` não produz memória longa automaticamente.

## 7. Middleware: lógica conectada aos estágios da execução

Os hooks principais são:

| Hook              | Momento                 | Exemplo de uso     |
| ----------------- | ----------------------- | ------------------ |
| `before_agent`    | Entrada no agente       | Preparação         |
| `before_model`    | Antes da chamada ao LLM | Logging de estado  |
| `wrap_model_call` | Ao redor do LLM         | Fallback/retry     |
| `after_model`     | Após a resposta do LLM  | Inspeção           |
| `wrap_tool_call`  | Ao redor da tool        | Logging/retry/HITL |
| `after_agent`     | Finalização             | Pós-processamento  |

Os hooks de nó e os hooks de wrapper possuem comportamentos diferentes. Os primeiros executam em pontos específicos; os segundos envolvem a execução e recebem um `handler`.

### 7.1. Middleware que observa o estado

```python
from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime

@before_model
def log_model(state: AgentState, runtime: Runtime):
    print("Mensagens:", len(state["messages"]))
    return None
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    middleware=[log_model],
)
```

### 7.2. Middleware que envolve tools

```python
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def log_tool(request, handler):
    print("Início:", request.tool_call["name"])
    result = handler(request)
    print("Fim da tool")
    return result
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    middleware=[log_model, log_tool],
)
```

O `handler(request)` continua a cadeia de execução. Ele pode passar por outros middlewares antes de chegar à tool.

### 7.3. Middleware que envolve o modelo

```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def log_model_call(request, handler):
    print("Chamando o LLM")
    response = handler(request)
    print("LLM respondeu")
    return response
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    middleware=[
        log_model,
        log_model_call,
        log_tool,
    ],
)
```

### 7.4. Middlewares predefinidos

Por exemplo, resumir histórico para controlar o tamanho do contexto:

```python
from langchain.agents.middleware import SummarizationMiddleware
summary = SummarizationMiddleware(
    model="openai:gpt-5.4-mini",
    trigger=("tokens", 4000),
    keep=("messages", 20),
)
```

Registro:

```python
agent = create_agent(
    model=MODEL,
    tools=[somar],
    middleware=[summary, log_tool],
    checkpointer=checkpointer,
)
```

Existem também middlewares de retry, tratamento de erros, proteção de dados e limites de execução.

## 8. Human-in-the-Loop: o que realmente acontece

### 8.1. Definição da ferramenta sensível

```python
@tool
def transferir(destino: str, valor: float) -> str:
    """Simula uma transferência financeira."""
    return f"Transferidos R$ {valor:.2f} para {destino}"
```

### 8.2. Definição da política

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware
hitl = HumanInTheLoopMiddleware(
    interrupt_on={
        "transferir": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
        "somar": False,
    },
    interrupt_mode="per_call",
)
```

### 8.3. Registro

```python
agent = create_agent(
    model=MODEL,
    tools=[somar, transferir],
    middleware=[hitl],
    checkpointer=InMemorySaver(),
)
```

### 8.4. Invocação que pode produzir interrupção

```python
config = {
    "configurable": {
        "thread_id": "conversa-123"
    }}
result = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "Transfira R$ 500 para João."
    }]},
    config=config,
    version="v2",
)
```

Ponto importante: `result.interrupts` só existirá com uma interrupção pendente se o modelo realmente propuser uma tool protegida.

```python
if result.interrupts:
    interrupt = result.interrupts[0]
    print(interrupt.id)
    print(interrupt.value)
```

O interrupt fornece a identificação e os argumentos da chamada proposta. Ele não executa a tool.

### 8.5. Decisões possíveis

No modo `per_call`, cada interrupção representa uma chamada de tool. A política de `transferir` definida na seção 8.2 permite três decisões:

- `approve`: executa a tool com os argumentos originais.
- `edit`: executa a tool com os argumentos alterados.
- `reject`: não executa a chamada e devolve o motivo ao modelo.

Copie **apenas uma** das atribuições abaixo para a interrupção obtida na seção 8.4. Se executar o bloco inteiro, a última atribuição (`edit`) será a escolhida:

```python
# Aprovar como foi solicitado
decision = {"type": "approve"}

# OU rejeitar (a mensagem é opcional)
decision = {
    "type": "reject",
    "message": "Operação não autorizada.",
}

# OU alterar os argumentos e aprovar
decision = {
    "type": "edit",
    "edited_action": {
        "name": "transferir",
        "args": {
            "destino": "João",
            "valor": 200,
        },
    },
}
```

Ao usar `edit`, mantenha o nome da tool e forneça argumentos compatíveis com sua definição. Para experimentar outra decisão, inicie uma nova execução e use a nova interrupção: uma decisão já enviada não pode ser substituída na mesma interrupção.

Há também `respond`: o humano fornece o resultado da tool sem executá-la. É apropriado para uma tool como `ask_user`; a mensagem é tratada como resultado bem-sucedido. Para negar uma operação, use `reject`. **`respond` não está permitido para `transferir` na política da seção 8.2**; veja um exemplo executável ao final da próxima seção.

### 8.6. Retomada

Depois de escolher `decision`, retome a interrupção com seu ID e o mesmo `thread_id`. O exemplo abaixo usa `result` e `config` da seção 8.4:

```python
from langgraph.types import Command

if not result.interrupts:
    print("Não há interrupção pendente para revisar.")
else:
    interrupt = result.interrupts[0]
    print("Chamada em revisão:", interrupt.value)

    result = agent.invoke(
        Command(resume={interrupt.id: decision}),
        config=config,  # Mesmo thread_id da invocação inicial
        version="v2",
    )

    if result.interrupts:
        print("Ainda há interrupções pendentes:", result.interrupts)
    else:
        print("Resposta do agente:", result.value["messages"][-1].content)
```

`version="v2"` retorna um `GraphOutput`: use `result.interrupts` para consultar as pendências e `result.value` para acessar o estado retornado. Sem esse parâmetro, o retorno padrão é um dicionário; uma interrupção pendente fica na chave `__interrupt__`.

Se houver várias interrupções, o exemplo responde apenas à primeira; as demais continuam pendentes. Uma retomada também pode gerar novas interrupções. A seção 11.1 mostra como lidar com várias decisões.

**Exemplo separado de `respond`:** crie outra tool e outro agente com essa decisão habilitada. Execute este bloco após os imports e a definição de `MODEL` usados no guia:

```python
@tool
def ask_user(pergunta: str) -> str:
    """Pergunta algo ao usuário quando uma informação estiver faltando."""
    return "Resposta não fornecida."

agent_ask = create_agent(
    model=MODEL,
    tools=[ask_user],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"ask_user": {"allowed_decisions": ["respond"]}},
        interrupt_mode="per_call",
    )],
    checkpointer=InMemorySaver(),
)
config_ask = {"configurable": {"thread_id": "exemplo-ask-user"}}
result_ask = agent_ask.invoke(
    {"messages": [{"role": "user", "content": "Use ask_user para perguntar minha cor favorita."}]},
    config=config_ask,
    version="v2",
)

if result_ask.interrupts:
    interrupt_ask = result_ask.interrupts[0]
    print("Pergunta proposta:", interrupt_ask.value["args"])
    result_ask = agent_ask.invoke(
        Command(resume={interrupt_ask.id: {
            "type": "respond",
            "message": "Minha cor favorita é azul.",
        }}),
        config=config_ask,
        version="v2",
    )
    if result_ask.interrupts:
        print("Ainda há interrupções pendentes:", result_ask.interrupts)
    else:
        print("Resposta do agente:", result_ask.value["messages"][-1].content)
else:
    print("O modelo não solicitou a tool ask_user.")
```

### 8.7. Fluxo com retorno ao frontend

```text
Usuário pede transferência
          ↓
Gradio chama agent.invoke()
          ↓
LLM solicita transferir()
          ↓
HITL detecta tool protegida
          ↓
LangGraph salva checkpoint
          ↓
agent.invoke() retorna GraphOutput
          ↓
result.interrupts contém a pendência
          ↓
Callback Gradio prepara painel
          ↓
Gradio mostra botões
          ↓
Usuário seleciona decisão
          ↓
Callback executa agent.invoke(Command(resume))
          ↓
LangGraph retoma a execução
          ↓
Tool é executada ou rejeitada
          ↓
Modelo continua
          ↓
Nova resposta ou novo interrupt
```

Esse último ponto é essencial: um `resume` não garante que o agente terminou. Ele pode solicitar novas tools e produzir outras interrupções.

## 9. Gradio: da interface simples à aprovação humana

Nesta seção, cada etapa acrescenta algo à anterior. Os exemplos usam o ambiente e o agente com HITL da seção 8.3. Execute as definições daquela seção antes de começar.

### 9.1. Uma primeira interface

Gradio cria interfaces no navegador usando Python. Vamos começar com um campo, um botão e uma resposta:

```python
import gradio as gr


def cumprimentar(nome: str) -> str:
    return f"Olá, {nome}!"


with gr.Blocks() as demo:
    nome = gr.Textbox(label="Seu nome")
    botao = gr.Button("Cumprimentar")
    resposta = gr.Textbox(label="Resposta")
    botao.click(fn=cumprimentar, inputs=[nome], outputs=[resposta])

demo.launch()
```

`gr.Blocks()` reúne os componentes. Ao clicar, o Gradio chama `cumprimentar`: o valor de `nome`, em `inputs`, entra na função; o retorno atualiza `resposta`, em `outputs`. Essa função acionada pelo evento é chamada de **callback**.

Execute o exemplo e abra o endereço informado. Nas próximas etapas, crie uma nova interface; não acrescente os trechos à interface de cumprimento.

### 9.2. Uma conversa com o agente

Primeiro, crie um agente sem HITL para testar somente a conversa. Ele usa a tool `somar`, definida na seção 5, e um checkpointer para guardar o histórico:

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

agente_chat = create_agent(
    model=MODEL,
    tools=[somar],
    checkpointer=InMemorySaver(),
)
```

Agora crie o callback. Ele recebe a mensagem, o histórico exibido e o identificador da conversa. O agente recupera seu próprio histórico pelo `thread_id`:

```python
def enviar(texto, historico, thread_id):
    if not texto.strip():
        return "", historico

    resultado = agente_chat.invoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": thread_id}},
        version="v2",
    )
    resposta = resultado.value["messages"][-1].content
    historico = historico + [
        {"role": "user", "content": texto},
        {"role": "assistant", "content": str(resposta)},
    ]
    return "", historico
```

O primeiro retorno limpa o campo de texto; o segundo atualiza o chat. Monte a interface e conecte o envio ao pressionar Enter:

```python
import uuid

with gr.Blocks() as demo:
    thread_id = gr.State(lambda: str(uuid.uuid4()))
    chat = gr.Chatbot()
    mensagem = gr.Textbox(label="Mensagem")

    mensagem.submit(
        fn=enviar,
        inputs=[mensagem, chat, thread_id],
        outputs=[mensagem, chat],
    )

demo.launch()
```

`gr.Chatbot` exibe as mensagens. `gr.State` guarda um valor para cada sessão do navegador; aqui, ele cria um `thread_id` diferente para cada conversa. Como no botão anterior, a ordem de `inputs` segue os parâmetros da função, e a ordem de `outputs` segue seus retornos.

Teste duas mensagens na mesma conversa. A próxima etapa trocará `agente_chat` pelo `agent` com HITL da seção 8.3.

### 9.3. Mostrar uma solicitação de aprovação

Com HITL, a chamada pode parar em `resultado.interrupts`, como vimos na seção 8. Precisamos guardar a pendência e exibir a tool e seus argumentos. Primeiro, crie uma função para preparar a interface depois de cada execução:

```python
import json


def processar_resultado(resultado, historico):
    pendencias = [
        {"id": item.id, "value": item.value}
        for item in resultado.interrupts
    ]
    if pendencias:
        acao = pendencias[0]["value"]
        aviso = f"Aprovação necessária para a tool **{acao['name']}**."
        argumentos = json.dumps(acao["args"], ensure_ascii=False, indent=2)
        return historico, pendencias, aviso, argumentos

    resposta = resultado.value["messages"][-1].content
    historico = historico + [{"role": "assistant", "content": str(resposta)}]
    return historico, [], "", ""
```

A função mostra uma pendência por vez. Se não houver interrupção, acrescenta a resposta do agente. Os argumentos são exibidos como texto JSON para que possam ser editados mais adiante.

Substitua a função `enviar` pela seguinte. Ela usa o agente protegido, impede outro envio durante a revisão e delega a atualização a `processar_resultado`:

```python
def enviar(texto, historico, thread_id, pendencias):
    if pendencias:
        raise gr.Error("Resolva a aprovação pendente antes de enviar outra mensagem.")
    if not texto.strip():
        return "", historico, pendencias, "", ""

    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": texto}]},
        config={"configurable": {"thread_id": thread_id}},
        version="v2",
    )
    historico = historico + [{"role": "user", "content": texto}]
    historico, pendencias, aviso, argumentos = processar_resultado(resultado, historico)
    return "", historico, pendencias, aviso, argumentos
```

Substitua a interface da etapa anterior por esta:

```python
with gr.Blocks() as demo:
    thread_id = gr.State(lambda: str(uuid.uuid4()))
    pendencias = gr.State([])
    chat = gr.Chatbot()
    mensagem = gr.Textbox(label="Mensagem")
    aviso = gr.Markdown()
    argumentos = gr.Textbox(label="Argumentos JSON", lines=3)

    mensagem.submit(
        fn=enviar,
        inputs=[mensagem, chat, thread_id, pendencias],
        outputs=[mensagem, chat, pendencias, aviso, argumentos],
    )

demo.launch()
```

O novo `gr.State` guarda os IDs e dados das interrupções da sessão. `gr.Markdown` mostra o aviso; o campo de argumentos permite revisar o que o modelo propôs. Peça uma transferência simulada: se o modelo solicitar `transferir`, a interface mostrará a pendência. Ainda falta escolher uma decisão.

### 9.4. Botão Aprovar

Para retomar o agente, precisamos do ID da interrupção e do mesmo `thread_id`. A função abaixo recebe uma decisão e volta a processar o resultado, pois a retomada pode gerar outra interrupção:

```python
from langgraph.types import Command


def resume_agent(decisao, historico, pendencias, thread_id):
    if not pendencias:
        raise gr.Error("Não há aprovação pendente.")

    resultado = agent.invoke(
        Command(resume={pendencias[0]["id"]: decisao}),
        config={"configurable": {"thread_id": thread_id}},
        version="v2",
    )
    return processar_resultado(resultado, historico)
```

O callback de aprovação fornece a decisão `approve`, já apresentada na seção 8:

```python
def aprovar(historico, pendencias, thread_id):
    return resume_agent({"type": "approve"}, historico, pendencias, thread_id)
```

Na interface da etapa 9.3, acrescente o botão e seu evento **após o bloco que cria os componentes e antes de `demo.launch()`**:

```python
with demo:
    botao_aprovar = gr.Button("Aprovar")
    botao_aprovar.click(
        fn=aprovar,
        inputs=[chat, pendencias, thread_id],
        outputs=[chat, pendencias, aviso, argumentos],
    )
```

Mantenha o evento `mensagem.submit` e `demo.launch()`. Execute novamente a interface, solicite uma transferência e aprove. Quando não houver outra pendência, o chat recebe a resposta e os campos de revisão são limpos.

### 9.5. Botão Rejeitar

A rejeição também usa `resume_agent`, agora com um motivo:

```python
def rejeitar(historico, pendencias, thread_id, motivo):
    decisao = {
        "type": "reject",
        "message": motivo.strip() or "Operação não autorizada.",
    }
    return resume_agent(decisao, historico, pendencias, thread_id)
```

Acrescente após o bloco que cria a interface e antes de `demo.launch()`:

```python
with demo:
    motivo = gr.Textbox(label="Motivo da rejeição")
    botao_rejeitar = gr.Button("Rejeitar")
    botao_rejeitar.click(
        fn=rejeitar,
        inputs=[chat, pendencias, thread_id, motivo],
        outputs=[chat, pendencias, aviso, argumentos],
    )
```

Execute novamente, solicite outra transferência e rejeite. O agente recebe o motivo, e a chamada rejeitada não é executada.

### 9.6. Botão Editar e aprovar

O campo `argumentos` já contém o JSON proposto. O callback abaixo o converte em dicionário, valida os campos da transferência e envia a decisão `edit`:

```python
import math


def editar(historico, pendencias, thread_id, texto_json):
    if not pendencias:
        raise gr.Error("Não há aprovação pendente.")
    try:
        args = json.loads(texto_json)
    except json.JSONDecodeError:
        raise gr.Error("Informe um JSON válido.")

    if not isinstance(args, dict) or set(args) != {"destino", "valor"}:
        raise gr.Error("Informe os campos destino e valor.")
    if not isinstance(args["destino"], str) or not args["destino"].strip():
        raise gr.Error("Informe um destino não vazio.")
    if isinstance(args["valor"], bool) or not isinstance(args["valor"], (int, float)):
        raise gr.Error("O valor deve ser um número.")
    if not math.isfinite(args["valor"]) or args["valor"] <= 0:
        raise gr.Error("O valor deve ser positivo e finito.")

    decisao = {
        "type": "edit",
        "edited_action": {"name": pendencias[0]["value"]["name"], "args": args},
    }
    return resume_agent(decisao, historico, pendencias, thread_id)
```

Acrescente também antes de `demo.launch()`:

```python
with demo:
    botao_editar = gr.Button("Editar e aprovar")
    botao_editar.click(
        fn=editar,
        inputs=[chat, pendencias, thread_id, argumentos],
        outputs=[chat, pendencias, aviso, argumentos],
    )
```

Solicite uma nova transferência, altere o valor no JSON e clique em **Editar e aprovar**. Se o JSON ou os campos forem inválidos, `gr.Error` mostra o problema e o agente permanece pausado. A validação acima é específica de `transferir`; outras tools precisam de validações apropriadas aos seus argumentos.

O fluxo completo é: mensagem → agente → pendência → decisão → retomada → resposta ou nova pendência. A transferência deste exemplo é simulada.

## 10. Integração dos componentes

Os trechos da seção 9 mostram como conectar o agente à interface.

A transferência é simulada. Para uma aplicação real, configure persistência, autenticação, isolamento por usuário e tratamento de erros adequados.

### 10.1. Mapa das conexões

| Conceito definido      | Ponto de conexão                           | Quem o executa                  |
| ---------------------- | ------------------------------------------ | ------------------------------- |
| `somar()`              | `tools=[somar, ...]`                       | Runtime de tools                |
| `transferir()`         | `tools=[..., transferir]`                  | Runtime, depois da aprovação    |
| `salvar_preferencia()` | `tools=[...]`                              | Runtime                         |
| `log_model()`          | `middleware=[...]`                         | Runtime antes do LLM            |
| `log_model_call()`     | `middleware=[...]`                         | Runtime envolvendo o LLM        |
| `log_tool()`           | `middleware=[...]`                         | Runtime envolvendo tools        |
| `hitl`                 | `middleware=[hitl, ...]`                   | Runtime das tools               |
| `checkpointer`         | `checkpointer=checkpointer`                | LangGraph                       |
| `store`                | `store=store`                              | LangGraph/ToolRuntime           |
| `Context`              | `context_schema=Context`                   | Validação e injeção na execução |
| `enviar()`             | `mensagem.submit(fn=...)`                   | Gradio                          |
| `processar_resultado()` | Chamada em `enviar` e `resume_agent` | Seu código                      |
| `resume_agent()`       | Chamada pelos callbacks de decisão         | Seu código                      |
| `aprovar()`            | `botao_aprovar.click(fn=...)`                | Gradio                          |
| `editar()`             | `botao_editar.click(fn=...)`                   | Gradio                          |
| `rejeitar()`           | `botao_rejeitar.click(fn=...)`                 | Gradio                          |

### 10.2. O ciclo completo, desde o texto até a aprovação

```text
Usuário digita mensagem
    │
    ▼
mensagem.submit(...)
    │
    ▼
enviar(...)
    │
    ├── prepara config com thread_id
    │
    ▼
agent.invoke(...)
    │
    ├── Checkpointer lê AgentState
    │
    ├── before_model
    │
    ├── wrap_model_call
    │       └── LLM
    │
    └── tool_call: transferir(...)
              │
              ▼
          wrap_tool_call
              │
              ▼
           HITL
              │
              ▼
          INTERRUPT
              │
       Checkpoint salvo
              │
              ▼
    agent.invoke() retorna
              │
              ▼
       processar_resultado()
              │
              ├── extrai result.interrupts
              ├── guarda pendências
              └── prepara aviso e argumentos JSON
              │
              ▼
         Gradio atualiza UI
              │
       ┌──────┼─────────┐
       │      │         │
    Aprovar  Editar   Rejeitar
       │      │         │
       └──────┼─────────┘
              │
              ▼
         resume_agent()
              │
              ▼
   agent.invoke(Command(resume=...))
              │
              ▼
   Checkpointer recupera execução
              │
              ▼
    Middleware recebe decisão
              │
        ┌─────┴──────┐
        │            │
    Autoriza       Rejeita
        │            │
        ▼            │
     Tool            │
        │            │
        └─────┬──────┘
              │
              ▼
         ToolMessage
              │
              ▼
             LLM
              │
          ┌───┴─────┐
          │         │
       Resposta   Novo interrupt
          │         │
          └────┬────┘
               ▼
       processar_resultado()
               │
               ▼
         Gradio atualiza
```

### 10.3. Mostrar os controles somente durante a interrupção

Após executar as definições da seção 9, substitua a interface anterior por esta. O painel começa oculto e aparece quando o agente precisa de uma decisão:

```python
def atualizar_painel(historico, pendencias, aviso, argumentos):
    if pendencias:
        aviso = (
            f"⏸️ **Agente pausado:** {aviso} "
            "Revise os argumentos e escolha como continuar."
        )
    return historico, pendencias, aviso, argumentos, gr.update(visible=bool(pendencias))


def enviar_ui(texto, historico, thread_id, pendencias):
    texto, historico, pendencias, aviso, argumentos = enviar(
        texto, historico, thread_id, pendencias
    )
    return texto, *atualizar_painel(historico, pendencias, aviso, argumentos)


def aprovar_ui(historico, pendencias, thread_id):
    return atualizar_painel(*aprovar(historico, pendencias, thread_id))


def editar_ui(historico, pendencias, thread_id, argumentos):
    return atualizar_painel(*editar(historico, pendencias, thread_id, argumentos))


def rejeitar_ui(historico, pendencias, thread_id, motivo):
    return atualizar_painel(*rejeitar(historico, pendencias, thread_id, motivo))


with gr.Blocks() as demo:
    thread_id = gr.State(lambda: str(uuid.uuid4()))
    pendencias = gr.State([])
    chat = gr.Chatbot()
    mensagem = gr.Textbox(label="Mensagem")

    with gr.Column(visible=False) as painel:
        aviso = gr.Markdown()
        argumentos = gr.Textbox(label="Argumentos JSON", lines=3)
        motivo = gr.Textbox(label="Motivo da rejeição (opcional)")
        with gr.Row():
            botao_aprovar = gr.Button("Aprovar")
            botao_editar = gr.Button("Editar e aprovar")
            botao_rejeitar = gr.Button("Rejeitar")

    saidas = [chat, pendencias, aviso, argumentos, painel]
    mensagem.submit(enviar_ui, [mensagem, chat, thread_id, pendencias], [mensagem, *saidas])
    botao_aprovar.click(aprovar_ui, [chat, pendencias, thread_id], saidas)
    botao_editar.click(editar_ui, [chat, pendencias, thread_id, argumentos], saidas)
    botao_rejeitar.click(rejeitar_ui, [chat, pendencias, thread_id, motivo], saidas)

demo.launch()
```

Enquanto houver pendência, o painel informa que o agente está pausado e mostra a operação para revisão. Após a decisão, ele desaparece se a execução terminar ou apresenta a próxima interrupção. **Aprovar** usa os argumentos originais; para aplicar alterações no JSON, escolha **Editar e aprovar**.

## 11. Comportamentos importantes e situações especiais

### 11.1. Múltiplas tool calls na mesma resposta

O modelo pode solicitar duas transferências:

```python
transferir(destino="João", valor=100)
transferir(destino="Maria", valor=200)
```

No modo `per_call`, cada chamada protegida gera sua própria interrupção, sem garantia de ordenação. A documentação permite respondê-las individualmente ou por um dicionário de decisões.

Para processar uma pendência por vez, podemos usar:

```python
pending = [{"id": item.id, "value": item.value} for item in result.interrupts]
current = pending[0]
```

A interface apresenta uma revisão por vez. Após a decisão:

```python
result = agent.invoke(
    Command(resume={current["id"]: decision}),
    config=config,
    version="v2",
)
```

a função `processar_resultado()` examina novamente as interrupções retornadas. Se houver outra pendência, os campos mostram a próxima operação.

Também é possível responder a várias interrupções juntas:

```python
decisions = {
    interrupt_1.id: {"type": "approve"},
    interrupt_2.id: {
        "type": "reject",
        "message": "Não autorizado.",
    },
}
result = agent.invoke(
    Command(resume=decisions),
    config=config,
    version="v2",
)
```

Para ações com efeitos colaterais, responder individualmente facilita a validação. A documentação alerta que, ao enviar múltiplas decisões, uma decisão inválida pode coexistir com outras que já foram executadas; reenviar inadvertidamente aprovações anteriores pode duplicar ações.

### 11.2. E se o usuário atualizar a página durante a aprovação?

O `gr.State` é específico da sessão. Ao atualizar a página, seu estado pode ser reiniciado.

Entretanto, o estado interno do agente permanece no checkpointer enquanto esse armazenamento existir.

Isso significa:

- Com `InMemorySaver`, a execução pode continuar disponível no processo Python.
- Com um checkpointer persistente, ela pode sobreviver ao reinício da aplicação.
- Para recuperar uma aprovação pendente após atualizar a página, sua aplicação precisa recuperar o `thread_id` e consultar o estado/checkpoint correspondente.

O exemplo utiliza `gr.State` porque é didático. Para autenticação e recuperação de sessões reais, seria necessário acrescentar essas funcionalidades.

### 11.3. Onde devem ficar os efeitos colaterais?

A regra é evitar efeitos irreversíveis antes da aprovação.

Por exemplo, isso seria inadequado:

```python
@wrap_tool_call
def middleware_perigoso(request, handler):
    cobrar_cartao()  # Efeito antes da autorização
    return handler(request)
```

Um retry ou retomada pode tornar esse efeito problemático.

A estrutura preferível é:

```text
Tool proposta
    ↓
HITL
    ↓
Aprovação
    ↓
Tool efetivamente executada
    ↓
Operação externa
```

Para integrações reais, utilize identificadores de operação e mecanismos de idempotência, principalmente quando houver retries ou possibilidade de reenvio.

### 11.4. Como adicionar tratamento de erros?

Um middleware de retry pode ser registrado assim:

```python
from langchain.agents.middleware import ToolRetryMiddleware
retry = ToolRetryMiddleware(max_retries=2)
agent = create_agent(
    model=MODEL,
    tools=[somar, transferir],
    middleware=[
        hitl,
        retry,
    ],
    checkpointer=checkpointer,
)
```

No modo `per_call`, a documentação recomenda colocar HITL antes de middlewares de retry e tratamento de erros, para evitar que a aprovação seja solicitada novamente durante retries.

O tratamento de erros da interface é outro assunto. Por exemplo, `editar()` utiliza `raise gr.Error(...)` para avisar que o JSON enviado é inválido, sem prosseguir com a operação.

### 11.5. O papel do `respond`

Além de `approve`, `edit` e `reject`, o HITL permite `respond` para tools nas quais o humano substitui a execução.

Exemplo:

```python
@tool
def ask_user(pergunta: str) -> str:
    """Solicita uma informação ao usuário."""
    return "Esta implementação é substituída pelo HITL."
```

Política:

```python
hitl = HumanInTheLoopMiddleware(
    interrupt_on={
        "ask_user": {
            "allowed_decisions": ["respond"]
        }
    },
    interrupt_mode="per_call",
)
```

Resposta humana:

```python
decision = {
    "type": "respond",
    "message": "Minha conta preferida é a conta principal.",
}
```

O texto será fornecido como resultado sintético da tool, sem executar sua implementação. Para uma interface Gradio, bastaria utilizar um campo de resposta humana e um callback que criasse esse `decision`, reutilizando `resume_agent()`.

## 12. Testes práticos para validar o aprendizado

Após montar uma aplicação com os exemplos, experimente os cenários abaixo e observe os logs do terminal.

Tool comum

Teste: Use a ferramenta de soma para calcular 35 + 47.

Esperado: O agente pode chamar somar, produzir um ToolMessage e responder sem HITL.

Memória curta

Teste: Meu nome é Bruno. Depois, em outra mensagem: qual é meu nome?

Esperado: O histórico é recuperado pela mesma thread.

Memória longa

Teste: Guarde que prefiro respostas curtas. Depois consulte essa preferência.

Esperado: salvar_preferencia e consultar_preferencia acessam o mesmo Store.

Aprovação HITL

Teste: Simule uma transferência de R$ 500 para João.

Esperado: O painel aparece; aprovar permite a execução simulada.

Edição HITL

Teste: Simule uma transferência de R$ 500 para Maria. Edite para R$ 100.

Esperado: O argumento alterado é enviado pela decisão edit.

Rejeição HITL

Teste: Simule uma transferência de R$ 300 para Pedro e rejeite.

Esperado: A tool não executa e o agente recebe o feedback.

Múltiplas chamadas

Teste: Simule duas transferências separadas, uma para João e outra para Maria.

Esperado: Se o modelo gerar ambas as chamadas, a interface apresenta cada pendência.

O resultado exato de uma solicitação depende do modelo: ele pode optar por não chamar uma ferramenta. O que deve ser validado é o comportamento da infraestrutura quando a tool call efetivamente acontece.

## 13. Referência rápida: definição, registro, execução e resultado

| Conceito           | Definição                       | Registro / acionamento           |
| ------------------ | ------------------------------- | -------------------------------- |
| Agente             | `create_agent(...)`             | `agent.invoke(...)`              |
| Tool               | `@tool def func(...)`           | `tools=[func]`                   |
| State              | `AgentState`                    | Runtime, `runtime.state`         |
| Context            | `@dataclass class Context`      | `context_schema`, `context=...`  |
| ToolRuntime        | `runtime: ToolRuntime`          | Injetado na tool                 |
| Memória curta      | `InMemorySaver()`               | `checkpointer=...` + `thread_id` |
| Memória longa      | `InMemoryStore()`               | `store=...`, `runtime.store`     |
| Middleware de nó   | `@before_model` etc.            | `middleware=[...]`               |
| Middleware wrapper | `@wrap_tool_call` etc.          | `handler(request)`               |
| HITL               | `HumanInTheLoopMiddleware(...)` | `middleware=[hitl]`              |
| Interrupt          | Produzido pelo runtime          | `result.interrupts`              |
| Resume             | `Command(resume=...)`           | `agent.invoke(...)`              |
| Gradio             | `gr.Blocks()`                   | `.launch()`                      |
| Evento Gradio      | `.submit()` / `.click()`        | `fn=callback`                    |
| Atualização da UI  | `return` do callback            | Componentes em `outputs`         |
| Revisão HITL       | `gr.Markdown()` e `gr.Textbox()` | Retornos do callback em `outputs` |

## 14. Modelo mental definitivo

A implementação inteira pode ser entendida em três camadas:

Camada 1 — Agente: você define tools, middlewares, memória e contexto, registra tudo no `create_agent` e chama `agent.invoke()`. O LangChain/LangGraph executa o ciclo interno.

Camada 2 — Interrupção: quando uma tool protegida é solicitada, o HITL suspende o fluxo. O checkpointer mantém o estado, e `result.interrupts` identifica as decisões pendentes.

Camada 3 — Interface: o Gradio recebe esse resultado, mostra os argumentos e os botões, coleta a escolha humana e chama novamente `agent.invoke(Command(resume=...))`. A partir daí, o runtime volta a assumir o controle.

A grande distinção é que o código da aplicação controla o começo, as decisões humanas e a apresentação; o runtime do agente controla o processamento interno, a execução das tools e a continuação após cada decisão.

### Documentação oficial consultada

- [LangChain — Agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain — Tools e ToolRuntime](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain — Custom Middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [LangChain — Short-term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)
- [LangChain — Long-term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory)
- [LangChain — Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [Gradio — Blocks e eventos](https://www.gradio.app/docs/gradio/blocks)
- [Gradio — Gerenciamento de estado](https://www.gradio.app/guides/state-in-blocks)
