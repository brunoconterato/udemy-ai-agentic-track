# Guia completo — LangChain `create_agent`, Tools, Middleware, Memória, HITL e Gradio

Guia de estudo e implementação · APIs atuais do LangChain 1.x, LangGraph e Gradio · Revisado em novembro de 2026

Este guia substitui o anterior, preservando os conceitos estudados e corrigindo as lacunas de integração. O foco é entender exatamente onde cada objeto ou função é definido, onde é registrado, quem o chama e como seu resultado chega ao próximo componente.

## 1. Correções e melhorias em relação ao guia anterior

Identifiquei sete pontos relevantes que precisavam de correção ou maior detalhamento.

| Problema anterior                                                               | Correção neste guia                                                                                     |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Gradio não explicava como o HITL mostrava os botões                             | Mostrar explicitamente o callback que recebe `result.interrupts` e torna o painel de aprovação visível  |
| Aprovação e rejeição não demonstravam toda a atualização da UI                  | Cada callback retorna os valores e propriedades dos componentes Gradio                                  |
| O código não deixava clara a ligação entre `fn`, `inputs`, `outputs` e `return` | Mapear a ordem dos argumentos e valores retornados                                                      |
| Não havia tratamento completo de múltiplas interrupções                         | Revisar cada interrupção individualmente usando seu ID                                                  |
| Misturava conceitos de estado                                                   | Distinguir `AgentState`, `gr.State`, `Context`, `ToolRuntime`, `Checkpointer` e `Store`                 |
| Não explicava adequadamente o retorno após `Command(resume)`                    | Demonstrar que a retomada pode produzir outra interrupção, e não necessariamente uma resposta final     |
| Não delimitava erros e efeitos colaterais                                       | Incluir validação de edição, proteção contra novas mensagens durante uma revisão e cuidados com retries |

Há ainda uma distinção importante: no modo `per_call` atual, o HITL intercepta cada chamada protegida dentro da cadeia de middleware das tools, enquanto no modo padrão `batched` a revisão é agrupada após a resposta do modelo.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

## 2. Mapa completo da arquitetura

Gradio — Interface

Textbox · Chatbot · Buttons · gr.State

Callbacks → agent.invoke()

create_agent

Orquestra o grafo de execução

Model

Raciocínio e tool calls

Middleware

Hooks, controle e HITL

AgentState

Mensagens e estado

Tools

Funções executáveis

Checkpointer

Estado por thread_id

Store

Memória entre threads

ToolRuntime

Conecta tools ao State, Context, Store e Config

Interrupt ↔ Command(resume)

Human-in-the-Loop

Revisão humana: approve · edit · reject · respond

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

```
uv init agente-estudo
cd agente-estudo

uv add "langchain>=1.4.6" langgraph langchain-openai gradio
```

Configure sua chave de API:

```
export OPENAI_API_KEY="sua-chave"
```

Nos exemplos, utilizaremos:

```
MODEL = "openai:gpt-5.5"
```

O modelo deve suportar tool calling. A escolha de modelo é independente da implementação de memória, middleware ou Gradio.

## 4. Conceito central: `create_agent`

O `create_agent` constrói um agente sobre LangGraph.

```
from langchain.agents import create_agentagent = create_agent(    model=MODEL,    tools=[],)
```

Para executar:

```
result = agent.invoke({    "messages": [        {"role": "user", "content": "Olá"}    ]})print(result["messages"][-1].content)
```

### Quem executa o quê?

```
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

```
from langchain.tools import tool@tooldef somar(a: float, b: float) -> float:    """Soma dois números."""    return a + b
```

### 5.2. Registro

```
agent = create_agent(    model=MODEL,    tools=[somar],)
```

### 5.3. Acionamento

```
result = agent.invoke({    "messages": [        {"role": "user", "content": "Some 20 e 30."}    ]})
```

Se o modelo solicitar:

```
{    "name": "somar",    "args": {"a": 20, "b": 30},}
```

o runtime executa `somar(a=20, b=30)`, cria o `ToolMessage` com o resultado e devolve a informação ao modelo.

Não é necessário:

```
somar.invoke(...)
```

após a resposta do modelo.

### 5.4. Estrutura das mensagens

```
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

```
from langgraph.checkpoint.memory import InMemorySavercheckpointer = InMemorySaver()
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    checkpointer=checkpointer,)
```

Identificação da conversa:

```
config = {    "configurable": {        "thread_id": "conversa-123"    }}
```

Execução:

```
agent.invoke(    {"messages": [        {"role": "user", "content": "Meu nome é Bruno."}    ]},    config=config,)result = agent.invoke(    {"messages": [        {"role": "user", "content": "Qual é meu nome?"}    ]},    config=config,)
```

A segunda chamada recupera o histórico da mesma thread. O estado é atualizado durante o fluxo, inclusive quando tools são executadas.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

### 6.2. `Context`: informações da execução

Definição:

```
from dataclasses import dataclass@dataclassclass Context:    user_id: str
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    context_schema=Context,)
```

Fornecimento:

```
agent.invoke(    {"messages": [        {"role": "user", "content": "Olá"}    ]},    context=Context(user_id="usuario-123"),)
```

O `Context` é particularmente útil para dados como identificadores de usuários, permissões e configurações da invocação.

### 6.3. Memória longa com `Store`

Definição:

```
from langgraph.store.memory import InMemoryStorestore = InMemoryStore()
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    store=store,    context_schema=Context,)
```

O `Store` armazena informações entre threads. Ao contrário do `Checkpointer`, ele não representa necessariamente o histórico completo de uma conversa.

### 6.4. `ToolRuntime`: a conexão interna

O `ToolRuntime` é um objeto que o LangChain injeta na função.

```
from langchain.tools import tool, ToolRuntime@tooldef contar_mensagens(runtime: ToolRuntime) -> int:    """Conta mensagens da conversa."""    return len(runtime.state["messages"])
```

O modelo não precisa preencher `runtime`.

Além de `runtime.state`, uma tool pode utilizar `runtime.context`, `runtime.store`, `runtime.config` e `runtime.tool_call_id`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

### 6.5. Tools acessando memória longa

```
@tooldef salvar_preferencia(    chave: str,    valor: str,    runtime: ToolRuntime[Context],) -> str:    """Salva uma preferência do usuário."""    user_id = runtime.context.user_id    runtime.store.put(        ("usuarios", user_id),        chave,        {"valor": valor},    )    return "Preferência salva."@tooldef consultar_preferencia(    chave: str,    runtime: ToolRuntime[Context],) -> str:    """Consulta uma preferência do usuário."""    user_id = runtime.context.user_id    item = runtime.store.get(        ("usuarios", user_id),        chave,    )    return item.value["valor"] if item else "Não encontrada."
```

Conexão no agente:

```
agent = create_agent(    model=MODEL,    tools=[        salvar_preferencia,        consultar_preferencia,    ],    store=store,    context_schema=Context,)
```

Acionamento:

```
agent.invoke(    {"messages": [{        "role": "user",        "content": "Guarde que prefiro respostas curtas."    }]},    context=Context(user_id="usuario-123"),)
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

Os hooks de nó e os hooks de wrapper possuem comportamentos diferentes. Os primeiros executam em pontos específicos; os segundos envolvem a execução e recebem um `handler`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

### 7.1. Middleware que observa o estado

```
from langchain.agents import AgentStatefrom langchain.agents.middleware import before_modelfrom langgraph.runtime import Runtime@before_modeldef log_model(state: AgentState, runtime: Runtime):    print("Mensagens:", len(state["messages"]))    return None
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    middleware=[log_model],)
```

### 7.2. Middleware que envolve tools

```
from langchain.agents.middleware import wrap_tool_call@wrap_tool_calldef log_tool(request, handler):    print("Início:", request.tool_call["name"])    result = handler(request)    print("Fim da tool")    return result
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    middleware=[log_model, log_tool],)
```

O `handler(request)` continua a cadeia de execução. Ele pode passar por outros middlewares antes de chegar à tool.

### 7.3. Middleware que envolve o modelo

```
from langchain.agents.middleware import wrap_model_call@wrap_model_calldef log_model_call(request, handler):    print("Chamando o LLM")    response = handler(request)    print("LLM respondeu")    return response
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    middleware=[        log_model,        log_model_call,        log_tool,    ],)
```

### 7.4. Middlewares predefinidos

Por exemplo, resumir histórico para controlar o tamanho do contexto:

```
from langchain.agents.middleware import SummarizationMiddlewaresummary = SummarizationMiddleware(    model="openai:gpt-5.4-mini",    trigger=("tokens", 4000),    keep=("messages", 20),)
```

Registro:

```
agent = create_agent(    model=MODEL,    tools=[somar],    middleware=[summary, log_tool],    checkpointer=checkpointer,)
```

Existem também middlewares de retry, tratamento de erros, proteção de dados e limites de execução.

## 8. Human-in-the-Loop: o que realmente acontece

### 8.1. Definição da ferramenta sensível

```
@tooldef transferir(destino: str, valor: float) -> str:    """Simula uma transferência financeira."""    return f"Transferidos R$ {valor:.2f} para {destino}"
```

### 8.2. Definição da política

```
from langchain.agents.middleware import HumanInTheLoopMiddlewarehitl = HumanInTheLoopMiddleware(    interrupt_on={        "transferir": {            "allowed_decisions": ["approve", "edit", "reject"]        },        "somar": False,    },    interrupt_mode="per_call",)
```

### 8.3. Registro

```
agent = create_agent(    model=MODEL,    tools=[somar, transferir],    middleware=[hitl],    checkpointer=InMemorySaver(),)
```

### 8.4. Invocação que pode produzir interrupção

```
config = {    "configurable": {        "thread_id": "conversa-123"    }}result = agent.invoke(    {"messages": [{        "role": "user",        "content": "Transfira R$ 500 para João."    }]},    config=config,    version="v2",)
```

Ponto importante: `result.interrupts` só existirá com uma interrupção pendente se o modelo realmente propuser uma tool protegida.

```
if result.interrupts:    interrupt = result.interrupts[0]    print(interrupt.id)    print(interrupt.value)
```

O interrupt fornece a identificação e os argumentos da chamada proposta. Ele não executa a tool.

### 8.5. Decisões possíveis

```
approve = {"type": "approve"}reject = {    "type": "reject",    "message": "Operação não autorizada.",}edit = {    "type": "edit",    "edited_action": {        "name": "transferir",        "args": {            "destino": "João",            "valor": 200,        },    },}respond = {    "type": "respond",    "message": "Resposta fornecida pelo humano.",}
```

`respond` é indicado para ferramentas do tipo `ask_user`, quando o humano substitui a resposta da própria ferramenta. Para negar uma operação, use `reject`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

### 8.6. Retomada

```
from langgraph.types import Commandresult = agent.invoke(    Command(        resume={            interrupt.id: approve        }    ),    config=config,    version="v2",)
```

O mesmo `thread_id` identifica a execução suspensa.

### 8.7. Fluxo com retorno ao frontend

```
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

## 9. Gradio: integração completa com HITL

Esta é a principal seção corrigida em relação ao guia anterior.

### 9.1. O que o Gradio precisa fazer

O Gradio precisa conectar seis etapas:

1. Receber mensagem: `gr.Textbox.submit()` chama `send_message()`.
2. Executar agente: `send_message()` chama `agent.invoke()`.
3. Detectar HITL: o callback verifica `result.interrupts`.
4. Exibir a revisão: o callback retorna `gr.update(visible=True)` para o painel e apresenta a tool e seus argumentos.
5. Receber decisão: os botões chamam `approve_action()`, `reject_action()` ou `edit_action()`.
6. Retomar o agente: esses callbacks enviam `Command(resume=...)`, recebem o novo resultado e atualizam toda a interface.

O Gradio não detecta automaticamente o HITL. É o callback Python que interpreta `result.interrupts` e torna os componentes visíveis.

### 9.2. Ligação entre `inputs`, parâmetros, `return` e `outputs`

Considere:

```
def somar_interface(a, b):    resultado = a + b    return resultado
```

E:

```
button.click(    fn=somar_interface,    inputs=[input_a, input_b],    outputs=[resultado_textbox],)
```

Mapeamento:

```
inputs[0] ──→ parâmetro a
inputs[1] ──→ parâmetro b

fn ─────────→ somar_interface()

return ─────→ resultado_textbox
```

Para múltiplos retornos:

```
def atualizar():    return "Texto", gr.update(visible=True)
```

```
button.click(    fn=atualizar,    inputs=[],    outputs=[status, painel],)
```

A primeira saída atualiza o conteúdo de `status`. A segunda altera a visibilidade de `painel`.

É exatamente assim que o HITL será apresentado ao usuário. A documentação do Gradio especifica que os argumentos da função correspondem aos componentes em `inputs`, e os valores retornados correspondem aos componentes em `outputs`.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://gradio.app&sz=32)

Gradio+2

### 9.3. Definir os componentes da interface

```
import gradio as grimport uuidwith gr.Blocks() as demo:    thread_id = gr.State(        lambda: str(uuid.uuid4())    )    pending = gr.State([])    chatbot = gr.Chatbot(        type="messages"    )    message = gr.Textbox(        label="Mensagem"    )    with gr.Group(visible=False) as review_panel:        review_info = gr.Markdown()        edited_args = gr.Code(            label="Argumentos JSON",            language="json",            interactive=True,        )        reject_reason = gr.Textbox(            label="Motivo da rejeição"        )        approve_btn = gr.Button("Aprovar")        edit_btn = gr.Button("Editar e aprovar")        reject_btn = gr.Button("Rejeitar")
```

Inicialmente:

```
gr.Group(visible=False)
```

significa que o painel de revisão está oculto.

Ele aparecerá quando o callback retornar:

```
gr.update(visible=True)
```

para o componente `review_panel`.

### 9.4. Função que interpreta o resultado do agente

Esta função é a ligação entre LangGraph e Gradio.

```
import jsondef process_result(result, history):    interrupts = list(result.interrupts)    if interrupts:        pending = [            {                "id": item.id,                "value": item.value,            }            for item in interrupts        ]        current = pending[0]        action = current["value"]        review_text = (            f"### Aprovação necessária\n\n"            f"**Tool:** `{action['name']}`\n\n"            f"**Interrupções pendentes:** {len(pending)}"        )        edited_json = json.dumps(            action["args"],            indent=2,            ensure_ascii=False,        )        return (            history,                     # Chatbot            pending,                     # gr.State            review_text,                 # Markdown            edited_json,                 # Code            gr.update(visible=True),     # Group        )    # Sem interrupções: execução terminou    answer = result.value["messages"][-1].content    history = history + [{        "role": "assistant",        "content": str(answer),    }]    return (        history,        [],        "",        "",        gr.update(visible=False),    )
```

O ponto que faltava no guia anterior é esta conexão:

```
result.interrupts        ↓process_result()        ↓gr.update(visible=True)        ↓review_panel aparece
```

Não existe uma chamada automática para `approve_btn.click()`. O middleware apenas produz a interrupção; o Gradio espera que o usuário clique.

### 9.5. Callback de envio

```
def send_message(message, history, thread_id, pending):    history = history or []    if pending:        raise gr.Error(            "Resolva a aprovação pendente antes de enviar outra mensagem."        )    if not message.strip():        return (            history, pending, message,            "", "", gr.update(visible=False)        )    config = {        "configurable": {            "thread_id": thread_id        }    }    result = agent.invoke(        {"messages": [            {"role": "user", "content": message}        ]},        config=config,        context=Context(user_id="usuario-demo"),        version="v2",    )    history = history + [{        "role": "user",        "content": message,    }]    (        history,        pending,        review_text,        edited_json,        panel_update,    ) = process_result(result, history)    return (        history,        pending,        "",              # Limpa campo de mensagem        review_text,        edited_json,        panel_update,    )
```

O `agent.invoke()` termina ao produzir o interrupt. A função então devolve a informação para o Gradio.

### 9.6. Conectar o envio à interface

```
message.submit(    fn=send_message,    inputs=[        message,        chatbot,        thread_id,        pending,    ],    outputs=[        chatbot,        pending,        message,        review_info,        edited_args,        review_panel,    ],)
```

Mapeamento explícito:

| `return` de `send_message`      | Componente atualizado |
| ------------------------------- | --------------------- |
| `history`                       | `chatbot`             |
| `pending`                       | `gr.State`            |
| `""`                            | `message`             |
| `review_text`                   | `review_info`         |
| `edited_json`                   | `edited_args`         |
| `gr.update(visible=True/False)` | `review_panel`        |

### 9.7. Função central para retomar o agente

As três decisões humanas possuem um comportamento comum: gerar um `Command`, chamar `agent.invoke()` e processar o resultado.

Podemos centralizar essa lógica:

```
from langgraph.types import Commanddef resume_agent(    decision,    history,    pending,    thread_id,):    if not pending:        raise gr.Error("Não há interrupção pendente.")    current = pending[0]    config = {        "configurable": {            "thread_id": thread_id        }    }    result = agent.invoke(        Command(            resume={                current["id"]: decision            }        ),        config=config,        context=Context(user_id="usuario-demo"),        version="v2",    )    return process_result(result, history)
```

Essa função não chama nenhuma tool manualmente.

```
resume_agent()
     ↓
Command(resume={interrupt_id: decision})
     ↓
agent.invoke()
     ↓
LangGraph recupera checkpoint
     ↓
HITL recebe decisão
     ↓
runtime continua execução
     ↓
result
     ↓
process_result()
     ↓
Gradio atualiza componentes
```

### 9.8. Botão Aprovar — callback completo

```
def approve_action(history, pending, thread_id):    decision = {        "type": "approve"    }    return resume_agent(        decision=decision,        history=history,        pending=pending,        thread_id=thread_id,    )
```

Conexão:

```
approve_btn.click(    fn=approve_action,    inputs=[        chatbot,        pending,        thread_id,    ],    outputs=[        chatbot,        pending,        review_info,        edited_args,        review_panel,    ],)
```

### 9.9. Botão Rejeitar — callback completo

```
def reject_action(    history,    pending,    thread_id,    reason,):    decision = {        "type": "reject",        "message": (            reason.strip()            or "Operação não autorizada. Não repita a chamada."        ),    }    return resume_agent(        decision=decision,        history=history,        pending=pending,        thread_id=thread_id,    )
```

Conexão:

```
reject_btn.click(    fn=reject_action,    inputs=[        chatbot,        pending,        thread_id,        reject_reason,    ],    outputs=[        chatbot,        pending,        review_info,        edited_args,        review_panel,    ],)
```

### 9.10. Botão Editar — callback completo

Aqui a validação acontece antes de retomar o agente.

```
def edit_action(    history,    pending,    thread_id,    edited_json,):    if not pending:        raise gr.Error("Não há interrupção pendente.")    current = pending[0]    original = current["value"]    try:        args = json.loads(edited_json)    except json.JSONDecodeError as exc:        raise gr.Error(f"JSON inválido: {exc}")    if not isinstance(args, dict):        raise gr.Error("Os argumentos precisam ser um objeto JSON.")    if original["name"] == "transferir":        if set(args) != {"destino", "valor"}:            raise gr.Error(                "Informe somente os campos destino e valor."            )        if not isinstance(args["destino"], str):            raise gr.Error("Destino inválido.")        if not args["destino"].strip():            raise gr.Error("Destino não pode ser vazio.")        try:            valor = float(args["valor"])
```

Conexão:

```
edit_btn.click(    fn=edit_action,    inputs=[        chatbot,        pending,        thread_id,        edited_args,    ],    outputs=[        chatbot,        pending,        review_info,        edited_args,        review_panel,    ],)
```

Agora a interface possui três operações completas, independentes, mas reutilizando `resume_agent()`.

### 9.11. O que acontece depois de clicar?

1\. Tool proposta

`transferir(destino="João", valor=500)`

2\. Painel Gradio apresentado

Exemplo ilustrativo do que a interface construída acima exibirá

Tool: `transferir`

```
{
  "destino": "João",
  "valor": 500
}
```

Aprovar

Editar

Rejeitar

3\. Callback escolhido

`approve_action()` / `edit_action()` / `reject_action()`

↓ `resume_agent()` → `agent.invoke(Command(...))`

4\. Resultado

Se houver novo interrupt, mantém o painel aberto. Caso contrário, exibe a resposta final e oculta o painel.

# 10. Aplicação integrada e executável — `app.py`

Agora reuniremos todos os conceitos em um único programa, sem funções omitidas, pseudocódigo ou objetos deixados como `...`.

Inclui:

- `create_agent` e tool calling automático;
- tools comuns e tools com `ToolRuntime`;
- `AgentState`, `Context`, memória curta e longa;
- middlewares `before_model`, `wrap_model_call` e `wrap_tool_call`;
- `HumanInTheLoopMiddleware` com `per_call`;
- Gradio com chatbot, painel condicional, edição de JSON, aprovação e rejeição;
- tratamento de múltiplas interrupções;
- callbacks completos de envio e retomada.

O exemplo de transferência é simulado: nenhuma movimentação financeira ocorre.

## 10.1. Código completo

```
import jsonimport mathimport uuidfrom dataclasses import dataclassimport gradio as grfrom langchain.agents import AgentState, create_agentfrom langchain.agents.middleware import (    HumanInTheLoopMiddleware,    before_model,    wrap_model_call,    wrap_tool_call,)from langchain.tools import tool, ToolRuntimefrom langgraph.checkpoint.memory import InMemorySaverfrom langgraph.store.memory import InMemoryStorefrom langgraph.runtime import Runtimefrom langgraph.types import Commandfrom langchain_core.messages import AIMessage# ==========================================================# 1. CONFIGURAÇÕES# ==========================================================MODEL = "openai:gpt-5.5"@dataclassclass Context:    """Dados fornecidos a cada invocação do agente."""
```

Execute com:

```
uv run python app.py
```

O código foi construído de acordo com as assinaturas documentadas, mas não foi executado contra um modelo real nesta conversa. Isso significa que o comportamento de escolha de ferramentas pelo LLM e possíveis particularidades das versões instaladas precisam ser validados no seu ambiente.

## 10.2. Mapa exato das conexões no código integrado

| Conceito definido      | Ponto de conexão                           | Quem o executa                  |
| ---------------------- | ------------------------------------------ | ------------------------------- |
| `somar()`              | `tools=[somar, ...]`                       | Runtime de tools                |
| `transferir()`         | `tools=[..., transferir]`                  | Runtime, depois da aprovação    |
| `salvar_preferencia()` | `tools=[...]`                              | Runtime                         |
| `log_before_model()`   | `middleware=[...]`                         | Runtime antes do LLM            |
| `log_model_call()`     | `middleware=[...]`                         | Runtime envolvendo o LLM        |
| `log_tool()`           | `middleware=[...]`                         | Runtime envolvendo tools        |
| `hitl`                 | `middleware=[hitl, ...]`                   | Runtime das tools               |
| `checkpointer`         | `checkpointer=checkpointer`                | LangGraph                       |
| `store`                | `store=store`                              | LangGraph/ToolRuntime           |
| `Context`              | `context_schema=Context`                   | Validação e injeção na execução |
| `make_config()`        | `config=make_config(thread_id)`            | Callback                        |
| `make_context()`       | `context=make_context()`                   | Callback                        |
| `send_message()`       | `message.submit(fn=...)`                   | Gradio                          |
| `process_result()`     | Chamada em `send_message` e `resume_agent` | Seu código                      |
| `resume_agent()`       | Chamada pelos callbacks de decisão         | Seu código                      |
| `approve_action()`     | `approve_btn.click(fn=...)`                | Gradio                          |
| `edit_action()`        | `edit_btn.click(fn=...)`                   | Gradio                          |
| `reject_action()`      | `reject_btn.click(fn=...)`                 | Gradio                          |

## 10.3. O ciclo completo, desde o texto até a aprovação

```
Usuário digita mensagem
    │
    ▼
message.submit(...)
    │
    ▼
send_message(...)
    │
    ├── make_config(thread_id)
    ├── make_context()
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
       process_result()
              │
              ├── extrai result.interrupts
              ├── cria pending
              ├── prepara argumentos JSON
              └── gr.update(visible=True)
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
       process_result()
               │
               ▼
         Gradio atualiza
```

## 11. Comportamentos importantes e situações especiais

### 11.1. Múltiplas tool calls na mesma resposta

O modelo pode solicitar duas transferências:

```
transferir(destino="João", valor=100)transferir(destino="Maria", valor=200)
```

No modo `per_call`, cada chamada protegida gera sua própria interrupção, sem garantia de ordenação. A documentação permite respondê-las individualmente ou por um dicionário de decisões.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

No exemplo integrado, utilizamos:

```
pending = extract_pending(result)current = pending[0]
```

A interface apresenta uma revisão por vez. Após a decisão:

```
result = agent.invoke(    Command(resume={current["id"]: decision}),    config=config,    version="v2",)
```

a função `process_result()` examina novamente as interrupções retornadas. Se houver outra pendência, o painel continua visível com a próxima operação.

Também é possível responder a várias interrupções juntas:

```
decisions = {    interrupt_1.id: {"type": "approve"},    interrupt_2.id: {        "type": "reject",        "message": "Não autorizado.",    },}result = agent.invoke(    Command(resume=decisions),    config=config,    version="v2",)
```

Para ações com efeitos colaterais, responder individualmente facilita a validação. A documentação alerta que, ao enviar múltiplas decisões, uma decisão inválida pode coexistir com outras que já foram executadas; reenviar inadvertidamente aprovações anteriores pode duplicar ações.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

### 11.2. E se o usuário atualizar a página durante a aprovação?

O `gr.State` é específico da sessão. Ao atualizar a página, seu estado pode ser reiniciado.

Entretanto, o estado interno do agente permanece no checkpointer enquanto esse armazenamento existir.

Isso significa:

- Com `InMemorySaver`, a execução pode continuar disponível no processo Python.
- Com um checkpointer persistente, ela pode sobreviver ao reinício da aplicação.
- Para recuperar uma aprovação pendente após atualizar a página, sua aplicação precisa recuperar o `thread_id` e consultar o estado/checkpoint correspondente.

O exemplo utiliza `gr.State` porque é didático. Para autenticação e recuperação de sessões reais, seria necessário acrescentar essas funcionalidades.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://gradio.app&sz=32)

Gradio+1

### 11.3. Onde devem ficar os efeitos colaterais?

A regra é evitar efeitos irreversíveis antes da aprovação.

Por exemplo, isso seria inadequado:

```
@wrap_tool_calldef middleware_perigoso(request, handler):    cobrar_cartao()  # Efeito antes da autorização    return handler(request)
```

Um retry ou retomada pode tornar esse efeito problemático.

A estrutura preferível é:

```
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

```
from langchain.agents.middleware import ToolRetryMiddlewareretry = ToolRetryMiddleware(max_retries=2)agent = create_agent(    model=MODEL,    tools=[somar, transferir],    middleware=[        hitl,        retry,    ],    checkpointer=checkpointer,)
```

No modo `per_call`, a documentação recomenda colocar HITL antes de middlewares de retry e tratamento de erros, para evitar que a aprovação seja solicitada novamente durante retries.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.langchain.com&sz=32)

Docs by LangChain

O tratamento de erros da interface é outro assunto. Por exemplo, `edit_action()` utiliza `raise gr.Error(...)` para avisar que o JSON enviado é inválido, sem prosseguir com a operação.

### 11.5. O papel do `respond`

Além de `approve`, `edit` e `reject`, o HITL permite `respond` para tools nas quais o humano substitui a execução.

Exemplo:

```
@tooldef ask_user(pergunta: str) -> str:    """Solicita uma informação ao usuário."""    return "Esta implementação é substituída pelo HITL."
```

Política:

```
hitl = HumanInTheLoopMiddleware(    interrupt_on={        "ask_user": {            "allowed_decisions": ["respond"]        }    },    interrupt_mode="per_call",)
```

Resposta humana:

```
decision = {    "type": "respond",    "message": "Minha conta preferida é a conta principal.",}
```

O texto será fornecido como resultado sintético da tool, sem executar sua implementação. Para uma interface Gradio, bastaria utilizar um campo de resposta humana e um callback que criasse esse `decision`, reutilizando `resume_agent()`.

## 12. Testes práticos para validar o aprendizado

Execute a aplicação e experimente os seguintes cenários, observando também os logs do terminal.

Checklist de execução

0 de 7 verificados

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
| Painel HITL        | `gr.Group(visible=False)`       | `gr.update(visible=True)`        |

## 14. Modelo mental definitivo

A implementação inteira pode ser entendida em três camadas:

Camada 1 — Agente: você define tools, middlewares, memória e contexto, registra tudo no `create_agent` e chama `agent.invoke()`. O LangChain/LangGraph executa o ciclo interno.

Camada 2 — Interrupção: quando uma tool protegida é solicitada, o HITL suspende o fluxo. O checkpointer mantém o estado, e `result.interrupts` identifica as decisões pendentes.

Camada 3 — Interface: o Gradio recebe esse resultado, mostra os argumentos e os botões, coleta a escolha humana e chama novamente `agent.invoke(Command(resume=...))`. A partir daí, o runtime volta a assumir o controle.

A grande distinção é que o código da aplicação controla o começo, as decisões humanas e a apresentação; o runtime do agente controla o processamento interno, a execução das tools e a continuação após cada decisão.

### Documentação oficial consultada

- [LangChain — Agents](https://docs.langchain.com/oss/python/langchain/agents?utm_source=chatgpt.com)
- [LangChain — Tools e ToolRuntime](https://docs.langchain.com/oss/python/langchain/tools?utm_source=chatgpt.com)
- [LangChain — Custom Middleware](https://docs.langchain.com/oss/python/langchain/middleware/custom?utm_source=chatgpt.com)
- [LangChain — Short-term Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory?utm_source=chatgpt.com)
- [LangChain — Long-term Memory](https://docs.langchain.com/oss/python/langchain/long-term-memory?utm_source=chatgpt.com)
- [LangChain — Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop?utm_source=chatgpt.com)
- [Gradio — Blocks e eventos](https://www.gradio.app/docs/gradio/blocks?utm_source=chatgpt.com)
- [Gradio — Gerenciamento de estado](https://www.gradio.app/guides/state-in-blocks?utm_source=chatgpt.com)
