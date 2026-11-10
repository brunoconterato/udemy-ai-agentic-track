# LangChain e LangGraph

## Histórico resumido

O LangChain surgiu no final de 2022 para facilitar a invocação de modelos de
linguagem. A linha do tempo apresentada nas imagens resume esta evolução:

- **Outubro de 2022:** LangChain foi lançado como código aberto por Harrison
  Chase.
- **2023:** consolidou-se como uma das primeiras camadas de abstração para a
  invocação de LLMs. A biblioteca simplificava o uso de diferentes APIs,
  permitia combinar chamadas e reunia *chains*, templates de prompt e RAG
  (*Retrieval-Augmented Generation*).
- **2023:** o projeto tornou-se o repositório que mais crescia no GitHub e
  recebeu US$ 35 milhões em investimentos de fundos de capital de risco,
  incluindo Benchmark e Sequoia.
- **Agosto de 2023:** foi introduzida a LCEL (*LangChain Expression Language*),
  com uma sintaxe de pipe (`|`) poderosa, mas inicialmente considerada pesada.
- **Início de 2024:** foram lançados o LangGraph, para orquestrar chamadas de
  LLM em grafos de dependências confiáveis e repetíveis, e o LangSmith, para
  observar modelos e aplicações em execução, especialmente em produção.
- **2025:** a versão 1.0 trouxe uma grande reformulação do framework e do
  ecossistema. A migração podia exigir uma refatoração extensa, inclusive a
  troca de pacotes importados. No mesmo período, a empresa alcançou uma
  avaliação de US$ 1,25 bilhão.
- **Hoje:** o foco está fortemente voltado para agentes e engenharia de
  agentes, com produtos como Deep Agents e recursos de agentes presentes em
  diferentes partes da plataforma.

## O ecossistema LangChain

O nome **LangChain** pode indicar coisas diferentes, por isso o contexto é
importante. Ele pode se referir à empresa, ao framework de código aberto, à
biblioteca específica LangChain (ou `langchain-core`) ou ao ecossistema de
produtos como um todo.

Na imagem, o ecossistema é organizado em quatro partes:

- **LangChain:** é um framework de código aberto que reúne componentes para
  modelos, mensagens, ferramentas e agentes, incluindo `create_agent` e
  *middleware*. Dentro dele existem bibliotecas como o LangChain Core.
- **LangGraph:** é o segundo framework de código aberto. Cuida da
  orquestração dos fluxos, normalmente organizando chamadas do LangChain em
  grafos de dependências.
- **LangSmith:** é a plataforma de observabilidade para acompanhar modelos e
  agentes, avaliar respostas e monitorar aplicações em produção. Há uma oferta
  gratuita para desenvolvedores, com planos pagos para usos que ultrapassam os
  limites do plano gratuito.
- **LangSmith Deployment:** é a infraestrutura gerenciada para implantar
  agentes em produção e executá-los no hardware da LangChain. Antes, esse
  produto era chamado de **LangGraph Platform**.

### Como as partes se relacionam

Uma forma simples de entender a divisão é:

1. **LangChain** fornece componentes e abstrações para construir agentes.
2. **LangGraph** organiza e executa o fluxo do agente.
3. **LangSmith** mostra o que aconteceu e ajuda a avaliar o resultado.
4. **LangSmith Deployment** oferece a infraestrutura gerenciada para produção.

## Camadas de abstração para criar agentes

A imagem mostra quatro níveis disponíveis no ecossistema LangChain. Eles vão
dos blocos mais básicos, na parte inferior, até uma solução pronta para
agentes, na parte superior.

A regra geral é simples: **as camadas inferiores oferecem mais controle e
exigem mais código; as camadas superiores oferecem mais conveniência e já
tomam várias decisões por você**.

### Camada 1: blocos de construção — `langchain-core`

É a camada mais fundamental. Ela fornece os componentes para:

- chamar modelos de linguagem de forma padronizada;
- enviar mensagens;
- conectar ferramentas (*tools*) aos modelos;
- encadear chamadas;
- transformar respostas em objetos estruturados.

Aqui o desenvolvedor controla praticamente tudo. Em compensação, precisa
montar manualmente o loop do agente, o tratamento das ferramentas, o estado e
os mecanismos necessários para tornar a execução confiável.

### Camada 2: orquestração — LangGraph

LangGraph organiza as chamadas em um grafo de dependências. Nesse grafo:

- **nós** representam etapas de processamento;
- **arestas** representam os caminhos entre as etapas;
- o **estado** guarda as informações compartilhadas pelo fluxo;
- *checkpoints* permitem persistir o progresso e retomar a execução.

Essa camada é indicada quando é necessário controlar o fluxo com precisão,
criar decisões ou loops explícitos e construir agentes mais confiáveis e
repetíveis. Ela é poderosa, mas exige que o desenvolvedor descreva o grafo.

### Camada 3: agente pronto — `create_agent`

`create_agent` fica no LangChain e simplifica os casos de uso mais comuns.
Você informa o modelo, as ferramentas e as instruções; o loop padrão do
agente já vem preparado.

Por baixo dos panos, `create_agent` constrói e executa um grafo do LangGraph,
que utiliza os componentes básicos do LangChain. Portanto, essa camada oferece
uma interface simples sem eliminar a estrutura de orquestração que existe nas
camadas inferiores.

É uma boa escolha quando você quer criar um agente rapidamente e não precisa
controlar cada nó e cada transição do fluxo.

### Camada 4: *harness* — Deep Agents

Deep Agents é a camada de nível mais alto. Funciona como um agente completo,
com várias capacidades integradas, ou “baterias incluídas”. Entre elas estão:

- planejamento;
- subagentes;
- leitura e gravação em um sistema de arquivos;
- lista de tarefas;
- execução em loop até atingir um objetivo.

O desenvolvedor fornece principalmente a intenção ou a meta. A estrutura
assume grande parte do trabalho de organizar e manter um agente de longa
duração. Em troca, há menos controle detalhado sobre a implementação interna.

### Como escolher uma camada

- Use **`langchain-core`** quando precisar controlar os componentes básicos.
- Use **LangGraph** quando o fluxo, o estado e as decisões forem o centro do
  problema.
- Use **`create_agent`** para agentes comuns, com modelo, prompt e ferramentas.
- Use **Deep Agents** quando quiser um agente completo, persistente e com
  planejamento integrado.

Essas camadas não são produtos isolados: as superiores aproveitam as
inferiores. Por isso, é possível começar com `create_agent` e descer para o
LangGraph ou para o `langchain-core` quando for necessário obter mais controle.

## Ideia central

Em termos simples, LangChain fornece componentes para trabalhar com LLMs;
LangGraph organiza esses componentes em fluxos com etapas, decisões e estados;
e LangSmith ajuda a observar o que aconteceu durante a execução.

Juntos, eles formam um ambiente para criar aplicações de IA mais estruturadas,
testáveis e fáceis de acompanhar.

## LangChain Core na prática

O `langchain-core` é a caixa de ferramentas básica do ecossistema. Ele não cria
um agente completo sozinho: oferece peças pequenas e combináveis para você
montar o comportamento que precisa.

```text
modelo  →  mensagens  →  ferramentas  →  loop  →  saída estruturada
```

### As cinco peças essenciais

1. **Modelos** — uma interface comum para conversar com diferentes LLMs. O
   método `invoke` executa uma chamada; `stream` entrega a resposta aos poucos.

   ```python
   resposta = llm.invoke("Explique agentes autônomos em uma frase")

   for parte in llm.stream("Escreva um poema de duas linhas"):
       print(parte.content, end="")
   ```

2. **Mensagens** — objetos tipados, como `SystemMessage`, `HumanMessage` e
   `AIMessage`, substituem listas soltas de dicionários. Isso deixa claro quem
   enviou cada mensagem e facilita estruturar o histórico da conversa.

   ```python
   mensagens = [
       SystemMessage("Responda em cinco palavras"),
       HumanMessage("Qual é a capital da França?"),
   ]
   resposta = llm.invoke(mensagens)
   ```

3. **Tools** — funções que o modelo pode chamar para obter dados ou executar
   ações. Com `@tool`, a documentação e as dicas de tipo da função ajudam a
   formar automaticamente o esquema que será apresentado ao modelo.

   ```python
   @tool
   def get_share_price(symbol: str) -> float:
       """Retorna o preço atual de uma ação."""
       return {"AAPL": 210.0, "MSFT": 480.0}[symbol]
   ```

4. **Loop** — na camada Core, o ciclo do agente é montado manualmente:

   ```text
   bind_tools → invoke → ler tool_calls → executar tools
       ↑                                      ↓
       └──────────── enviar ToolMessage ─────┘
   ```

   O modelo decide quando precisa de uma ferramenta; o programa executa a
   função, devolve o resultado em um `ToolMessage` e chama o modelo novamente.
   O ciclo termina quando não há mais `tool_calls`.

5. **Saída estruturada** — quando a resposta precisa seguir um formato exato,
   `with_structured_output` permite declarar um schema, por exemplo um modelo
   Pydantic, e receber um objeto em vez de texto livre.

### Ideia para memorizar

`langchain-core` fornece os componentes; o desenvolvedor decide como conectá-
los. Por isso, é a camada que oferece mais controle — e também exige que você
implemente o loop, o estado e o tratamento das ferramentas. O LangGraph entra
depois para organizar esse fluxo em um grafo mais confiável.

## LangGraph: transformar um fluxo em grafo

Quando uma aplicação tem várias etapas, decisões e repetições, é útil
representá-la como um **grafo direcionado**:

```text
START → classificar → responder
                 ↘ buscar → responder
```

- **Nó**: uma função que executa uma etapa.
- **Aresta**: uma ligação que define qual etapa vem depois.
- **Estado**: os dados compartilhados entre os nós.
- **`START`**: ponto de entrada.
- **`END`**: ponto de saída.
- **Grafo compilado**: o fluxo pronto para ser executado.

O LangGraph não depende de um modelo de linguagem. O mesmo mecanismo pode
orquestrar funções comuns, chamadas de API ou modelos.

### Estado, `TypedDict` e atualização parcial

O **estado** é um dicionário compartilhado pelo grafo. Ele contém os dados
que um nó pode ler e os dados que os nós podem atualizar. `TypedDict` descreve
esse formato para o Python e para quem lê o código; ele não executa nada e não
é uma classe que precise ser instanciada:

```python
from typing_extensions import TypedDict

class State(TypedDict):
    pergunta: str
    resposta: str
```

Uma execução começa com um dicionário compatível com esse formato:

```python
estado_inicial = {
    "pergunta": "O que é um grafo?",
    "resposta": "",
}
```

Um **nó** é uma função que foi registrada no `StateGraph` com um nome. A
função, sozinha, é apenas uma função Python comum. Ela se torna uma etapa do
fluxo quando é conectada ao grafo:

```python
def responder(state: State) -> dict:
    return {"resposta": f"Você perguntou: {state['pergunta']}"}

builder.add_node("responder", responder)
```

Quando o fluxo chega ao nó `responder`, o LangGraph faz três coisas:

```text
estado atual → responder(state) → atualização retornada → estado atualizado
```

Neste exemplo, a função lê `state["pergunta"]` e retorna somente o novo valor
de `resposta`. Isso é uma **atualização parcial**: o nó não precisa devolver o
estado inteiro. Campos que não aparecem no retorno permanecem como estavam.

O estado inicial e o estado final podem ser vistos assim:

```text
antes:  {pergunta: "O que é um grafo?", resposta: ""}
                         │
                         └─ responder retorna {resposta: "Você perguntou..."}
                         │
depois: {pergunta: "O que é um grafo?", resposta: "Você perguntou..."}
```

O próprio grafo define quando essa função será chamada:

```python
from langgraph.graph import END, START, StateGraph

builder = StateGraph(State)
builder.add_node("responder", responder)
builder.add_edge(START, "responder")
builder.add_edge("responder", END)

graph = builder.compile()
resultado = graph.invoke(estado_inicial)
print(resultado["resposta"])
```

Assim, `graph.invoke(...)` não chama `responder` diretamente. Ele inicia o
grafo, passa o estado ao nó conectado a `START`, aplica a atualização retornada
e segue as arestas até `END`.

### Reducers e `Annotated`

Quando um nó retorna um campo, o LangGraph precisa decidir como aplicar esse
valor ao estado. A regra padrão é substituir:

```text
valor antigo: "rascunho"
atualização:  "resposta final"
resultado:    "resposta final"
```

Um **reducer** é uma função que recebe o valor atual e a atualização e decide
como combiná-los. Ele é útil quando substituir não é o comportamento desejado,
como no histórico de uma conversa.

`Annotated[tipo, reducer]` associa essa regra a um campo do estado. No chat,
`add_messages` é o reducer que adiciona ou mescla as novas mensagens ao
histórico:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
```

Leia a declaração desta forma:

```text
messages é uma lista
e suas atualizações devem ser aplicadas por add_messages
```

Sem o reducer, retornar `{"messages": [nova_mensagem]}` substituiria o
histórico inteiro. Com `add_messages`, o resultado é acumulado:

```text
estado:       [mensagem do usuário]
atualização:  [resposta do modelo]
estado novo:  [mensagem do usuário, resposta do modelo]
```

Um nó de conversa pode, portanto, retornar apenas a nova mensagem:

```python
from langchain_core.messages import AIMessage

def chatbot(state: ChatState) -> dict:
    ultima = state["messages"][-1].content
    return {"messages": [AIMessage(content=f"Você disse: {ultima}")]}
```

Para transformar esse nó em um fluxo executável, é preciso registrá-lo e
conectá-lo:

```python
builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
chat_graph = builder.compile()

result = chat_graph.invoke({
    "messages": [{"role": "user", "content": "Olá!"}]
})

for message in result["messages"]:
    print(message.content)
```

O dicionário inicial fornece a primeira mensagem. O nó lê o histórico, produz
uma nova mensagem e o reducer a incorpora ao campo `messages`. Em um agente
real, o nó pode trocar a função de eco por `llm.invoke(state["messages"])`.

O reducer não é chamado manualmente pelo nó. O nó retorna a atualização; o
LangGraph aplica automaticamente a regra declarada no `ChatState`.

### Montagem e execução

Depois de definir o estado e os nós, o builder descreve o caminho do fluxo.
`compile()` valida essa descrição e devolve um objeto executável; é esse objeto
que recebe entradas com `invoke`.

```python
from langgraph.graph import START, END, StateGraph

builder = StateGraph(State)
builder.add_node("responder", responder)
builder.add_edge(START, "responder")
builder.add_edge("responder", END)

graph = builder.compile()
resultado = graph.invoke({"pergunta": "O que é um grafo?", "resposta": ""})
```

A sequência mental é:

```text
definir estado → criar builder → adicionar nós → adicionar arestas → compilar → executar
```

### Arestas condicionais e loops

Uma aresta comum sempre segue para o mesmo nó. Uma **aresta condicional** chama
uma função de roteamento, que escolhe o próximo nó com base no estado. Isso
permite decisões e ciclos:

```text
modelo
  ├─ pediu ferramenta? ─ sim → tools → modelo → ...
  └─ não               ─────────────→ END
```

O ciclo termina quando a condição deixa de apontar para `tools`. Todo loop de
agente precisa de uma condição de parada para evitar execução infinita e custo
desnecessário.

No fluxo com ferramentas, `ToolNode` executa as funções solicitadas pelo
modelo e `tools_condition` escolhe entre voltar às ferramentas ou finalizar.
O modelo apenas solicita a ferramenta; o programa é quem a executa:

```python
from langgraph.prebuilt import ToolNode, tools_condition

tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: ChatState) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
graph = builder.compile()
```

Se o modelo produzir `tool_calls`, o roteador envia o estado para `tools`. O
`ToolNode` executa as chamadas, adiciona os resultados ao histórico e o fluxo
volta ao modelo. Se não houver `tool_calls`, o roteador termina o fluxo.

## Memória, threads e checkpoints

Há duas durações diferentes:

1. O estado existe enquanto uma chamada a `invoke` percorre o grafo.
2. Um checkpointer salva esse estado para ser recuperado em outra chamada.

Sem checkpointer, duas chamadas são independentes, mesmo que usem o mesmo
objeto `graph`.

Um **checkpointer** salva versões do estado após cada etapa. Um
`thread_id` identifica a conversa ou execução à qual esses estados pertencem.
O mesmo identificador recupera o histórico; outro identificador começa uma
conversa separada:

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
chat_graph = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "cliente-42"}}

chat_graph.invoke(
    {"messages": [{"role": "user", "content": "Meu nome é Ana."}]},
    config=config,
)
resultado = chat_graph.invoke(
    {"messages": [{"role": "user", "content": "Qual é meu nome?"}]},
    config=config,
)
# O segundo turno pode consultar as mensagens salvas do primeiro.
```

Há duas ideias diferentes:

- **Histórico no estado**: mensagens acumuladas durante o fluxo.
- **Checkpointer**: snapshots persistidos entre chamadas.

`InMemorySaver` é simples, mas perde os dados ao encerrar o processo. Para
persistir entre reinicializações, use um checkpointer durável, como o de
SQLite, e mantenha o mesmo `thread_id`:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("checkpoints.db") as saver:
    chat_graph = builder.compile(checkpointer=saver)
    chat_graph.invoke(entrada, config=config)
```

O banco guarda o estado da aplicação, não uma “memória” inteligente. Cabe ao
desenvolvedor definir quais dados entram no estado e por quanto tempo devem ser
mantidos.

Como cada checkpoint representa um momento do fluxo, também é possível
inspecionar a trajetória, voltar a um ponto anterior e criar uma nova
ramificação a partir dele. Isso é útil para depuração, recuperação de falhas e
comparação de decisões.

Uma execução também pode ser entendida em **super-steps**: uma unidade em que
um conjunto de nós é executado antes de o estado ser salvo novamente. Por
exemplo, o modelo pode executar em um super-step e as ferramentas solicitadas
no seguinte. Cada checkpoint representa um desses pontos e pode ser usado
para inspecionar ou retomar o fluxo.

## Agentes com `create_agent`

Um agente combina três elementos:

- **modelo**: interpreta a solicitação e decide o próximo passo;
- **prompt de sistema**: define comportamento, limites e contexto;
- **ferramentas**: funções que o programa executa quando o modelo as solicita.

O `create_agent` monta o loop entre esses elementos:

```python
from langchain.agents import create_agent

agent = create_agent(
    model="provedor:modelo",
    tools=[get_weather],
    system_prompt="Ajude o usuário usando as ferramentas disponíveis.",
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "Como está o tempo?"}]
})
print(result["messages"][-1].content)
```

Conceitualmente, esse agente contém um grafo semelhante ao fluxo montado
manualmente:

```text
modelo → decisão → tools → modelo → resposta final
```

A diferença é o nível de abstração: o framework monta o loop, enquanto o
desenvolvedor fornece o modelo, as ferramentas e as instruções. Quando for
necessário controlar cada transição, o LangGraph continua sendo a opção mais
explícita. `create_agent` é conveniente; não é um tipo diferente de execução.
Internamente, o agente também é um grafo compilado.

### Execução assíncrona

`ainvoke` é a versão assíncrona de `invoke`: recebe a mesma entrada e devolve
um resultado equivalente, mas precisa ser aguardada com `await` dentro de uma
função assíncrona:

```python
async def responder():
    result = await agent.ainvoke({
        "messages": [{"role": "user", "content": "Pesquise isto"}]
    })
    return result["messages"][-1].content

# Em um programa assíncrono:
# resposta = await responder()
```

Use a versão assíncrona quando o agente ou uma ferramenta usa rede, navegador
ou outro processo assíncrono. Não misture `await` em uma função comum; torne a
função `async def` e propague o uso de `await` até o ponto que inicia a tarefa.

### Saída estruturada do agente

Uma resposta estruturada é um objeto validado por um schema, em vez de texto
livre. O agente ainda pode usar ferramentas antes de preencher o objeto:

```python
from pydantic import BaseModel

class Resumo(BaseModel):
    titulo: str
    confianca: float

agent = create_agent(
    model="provedor:modelo",
    response_format=Resumo,
)

result = agent.invoke({"messages": [{"role": "user", "content": "Resuma o tema"}]})
resumo = result["structured_response"]
print(resumo.titulo, resumo.confianca)
```

Um schema limita o formato esperado e facilita validar e consumir a resposta
em código. Isso é diferente de pedir apenas “responda em JSON” no prompt:
nesse último caso, ainda seria necessário analisar e validar manualmente o
texto retornado.

## Middleware: pontos de controle do agente

**Middleware** é código executado em pontos definidos do ciclo do agente. Ele
permite observar, alterar ou bloquear comportamentos sem reescrever o loop.

Pense nele como uma camada ao redor de uma etapa:

```text
pedido → middleware antes → ferramenta → middleware depois → resultado
```

Exemplos de responsabilidades:

- registrar chamadas de ferramentas;
- resumir conversas longas;
- remover dados pessoais;
- limitar quantidade de chamadas ao modelo;
- tentar novamente após falhas;
- pedir aprovação antes de uma ação sensível.

Um middleware ao redor de uma ferramenta pode registrar a chamada e depois
deixar que ela prossiga:

```python
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def registrar(request, handler):
    print("Ferramenta:", request.tool_call["name"])
    return handler(request)

agent = create_agent(
    model="provedor:modelo",
    tools=[get_weather],
    middleware=[registrar],
)
```

O princípio é separar a política transversal — observação, segurança ou
limites — da lógica específica de cada ferramenta. O `handler` é a continuação
do fluxo: se o middleware não o chamar, a ferramenta não será executada. Isso
permite bloquear, alterar ou tratar erros antes de deixar a chamada prosseguir.

Além de middleware próprio, há middleware pronto para resumir conversas,
remover dados pessoais, limitar chamadas, repetir operações e pausar para
aprovação humana. Use middleware para regras que devem valer para várias
ferramentas ou para toda a execução, não para a lógica normal de uma única
função.

## Provedores, credenciais e visualização

O modelo é uma dependência configurável. A mesma abstração de chat pode se
conectar a provedores diferentes, desde que o adaptador saiba traduzir
mensagens, ferramentas e respostas para a API escolhida:

```python
import os
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="modelo-exemplo",
    api_key=os.environ["OPENAI_API_KEY"],
)
```

Na prática, chaves e endereços de serviços devem vir de um gerenciador de
segredos ou de variáveis de ambiente, nunca de código versionado. Ferramentas
de busca, notificações e navegadores também dependem de credenciais próprias.
Uma falha de autenticação é uma falha da integração, não uma resposta válida
do modelo.

Um grafo compilado pode ser desenhado em Mermaid ou outra representação visual.
O diagrama ajuda a conferir se todos os caminhos têm entrada, saída e condição
de parada:

```text
START → agente → tools → agente
             └────────→ END
```

Visualizar o grafo antes de adicionar mais funcionalidades é uma forma simples
de encontrar caminhos esquecidos e loops acidentais. O desenho é apenas uma
visão do fluxo; ele não executa o agente.

## MCP: ferramentas em processos externos

O **Model Context Protocol (MCP)** é um padrão para disponibilizar ferramentas
e recursos através de um servidor separado. A função pode não estar no mesmo
programa Python: um servidor externo expõe suas capacidades e um adaptador as
carrega para o agente.

```text
agente Python ── cliente MCP ── transporte ── servidor MCP
       └──────────── ferramentas disponíveis ────────────┘
```

Para o agente, uma ferramenta MCP se comporta como qualquer outra: possui
nome, descrição, argumentos e resultado. A diferença é que sua execução ocorre
fora do processo principal. Isso permite integrar navegadores, bancos de
dados, sistemas internos e outros programas sem reimplementar tudo em Python.

O fluxo de integração é:

1. iniciar ou localizar o servidor MCP;
2. abrir um cliente com o transporte configurado;
3. pedir ao cliente a lista de ferramentas;
4. entregar essa lista a `create_agent` ou `create_deep_agent`;
5. fechar a conexão ao terminar.

Uma consequência prática é que muitas ferramentas MCP são assíncronas:

```python
cliente = await conectar_servidor()
try:
    tools = await cliente.get_tools()
    agent = create_agent(model="provedor:modelo", tools=tools)
    resultado = await agent.ainvoke(entrada)
finally:
    await cliente.close()
```

`conectar_servidor` e `close` representam o adaptador escolhido; o transporte
pode ser stdio, HTTP ou outro suportado pelo servidor. O ponto importante é
que o agente recebe as ferramentas descobertas, mas a execução continua sendo
feita pelo servidor externo.

### Automação de navegador

Uma ferramenta de navegador pode abrir páginas, clicar, preencher campos e
ler conteúdo. O navegador é um recurso com estado: a sessão pode manter
cookies, abas e autenticação entre chamadas.

Automação real exige cuidados: credenciais não devem ser entregues ao modelo,
ações irreversíveis devem pedir confirmação e o agente deve saber quando
devolver o controle a uma pessoa. Se a sessão do servidor for encerrada entre
duas chamadas, cookies e abas podem desaparecer; por isso, tarefas longas
devem manter a sessão aberta e fechá-la explicitamente ao final.

## Deep Agents: planejamento e trabalho longo

Um Deep Agent é um *harness*: uma estrutura pronta para tarefas abertas, longas
e com vários artefatos. Ele adiciona convenções ao agente comum:

- **planejamento**: uma lista de tarefas que pode ser criada e atualizada;
- **filesystem**: arquivos para anotações, resultados intermediários e
  entregáveis;
- **subagentes**: especialistas com contexto separado;
- **execução iterativa**: trabalhar até concluir o objetivo.

Use essa camada quando a tarefa tiver pesquisa, várias etapas e arquivos como
resultado. Para uma pergunta curta, um agente simples costuma ser suficiente.

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

agent = create_deep_agent(
    model="provedor:modelo",
    tools=[search],
    backend=FilesystemBackend(root_dir="./sandbox"),
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Pesquise o tema e escreva o resultado em /relatorio.md",
    }]
})
```

O sistema de arquivos dá ao agente uma memória de trabalho explícita. Uma
instrução como “escreva `/relatorio.md`” pode produzir um arquivo no diretório
configurado, que depois pode ser revisado por uma pessoa ou por outro agente.
O caminho `/relatorio.md` é virtual para o agente e corresponde a um arquivo
dentro de `./sandbox` no programa. Separe memória de trabalho de arquivos
definitivos e aplique permissões mínimas às ferramentas de escrita.

### Subagentes

Um subagente é um especialista chamado pelo agente principal para executar uma
parte delimitada do trabalho:

```text
agente principal
 ├─ pesquisador de preços
 ├─ pesquisador de qualidade
 └─ comparador final
```

Cada subagente pode ter modelo, prompt, ferramentas e contexto próprios. O
contexto separado reduz distrações e permite dividir tarefas independentes.
O agente principal coordena a delegação e combina os resultados. Delegue uma
parte bem definida e diga qual formato o subagente deve devolver; o contexto
do agente principal não é automaticamente compartilhado em detalhes:

```text
principal: "pesquise dois produtos e compare-os"
   ├─ subagente A: "pesquise produto A; devolva preço e fontes"
   └─ subagente B: "pesquise produto B; devolva preço e fontes"
principal combina os dois relatórios
```

### Skills e divulgação progressiva

Uma **skill** é um conjunto de instruções reutilizáveis, geralmente guardado
em uma pasta com um arquivo `SKILL.md`. O arquivo pode descrever um padrão
visual, uma política da empresa ou um procedimento técnico.

Um arquivo mínimo tem metadados e instruções:

```markdown
---
name: relatorio-financeiro
description: Padroniza relatórios financeiros curtos.
---

Use títulos curtos, informe a fonte dos números e termine com uma recomendação.
```

Em vez de colocar todas as instruções no prompt inicial, o agente recebe
primeiro apenas o nome e a descrição. Ele lê o conteúdo completo quando a
skill se torna relevante:

```text
catálogo de skills → escolher skill relevante → ler SKILL.md → executar
```

Esse mecanismo é chamado de **divulgação progressiva**. Ele economiza contexto
e torna as instruções especializadas reutilizáveis.

## Human-in-the-loop: aprovação e intervenção

Nem toda ação deve ser executada automaticamente. O padrão
**human-in-the-loop** pausa o agente antes de uma operação sensível, como
enviar uma mensagem, reservar algo ou alterar um sistema.

```text
agente propõe ação → pausa → pessoa decide → agente continua
```

Uma decisão pode:

- **aprovar**: executar os argumentos propostos;
- **editar**: executar com argumentos corrigidos;
- **rejeitar**: não executar e devolver uma explicação ao modelo.

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

approval_agent = create_agent(
    model="provedor:modelo",
    tools=[enviar_email],
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"enviar_email": True}
    )],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "email-1"}}
pausado = approval_agent.invoke(
    {"messages": [{"role": "user", "content": "Envie o email"}]},
    config=config,
)
```

Quando uma ferramenta protegida é alcançada, o resultado contém uma
interrupção com a ação proposta. A aplicação mostra essa proposta à pessoa e
retoma o mesmo `thread_id` com uma decisão:

```python
from langgraph.types import Command

# Aprovar os argumentos originais:
final = approval_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
)

# Alternativas:
# {"type": "edit", "edited_action": {"name": "enviar_email", "args": {...}}}
# {"type": "reject", "message": "Não envie ainda."}
```

A pausa precisa de memória/checkpoint para que a execução seja retomada do
mesmo ponto, sem repetir as etapas anteriores. O mesmo padrão permite que o
agente peça ajuda para login, CAPTCHA ou autenticação de dois fatores e só
continue depois da intervenção humana. Uma aprovação deve acontecer antes da
ação externa, não depois que ela já foi executada.

## Tolerância a falhas e limites

Ferramentas externas podem falhar por timeout, autenticação, dados ausentes ou
mudança de página. Um agente robusto precisa diferenciar falha recuperável de
falha definitiva.

Uma estratégia possível é devolver o erro ao modelo como informação:

```text
tool falha → registrar erro → modelo decide outra tentativa ou alternativa
```

Isso é preferível a esconder o erro ou encerrar silenciosamente. Porém, não
devolva segredos, tokens ou uma pilha interna completa ao modelo. Converta a
falha em uma mensagem segura, com contexto suficiente para uma alternativa:

```python
try:
    dados = consultar_api(cidade)
except TimeoutError:
    return "A consulta demorou demais; tente outra fonte ou tente novamente."
```

Defina também se uma ferramenta é idempotente. Repetir uma busca costuma ser
seguro; repetir uma compra ou uma notificação pode duplicar efeitos. Ações
não idempotentes devem ter chave de deduplicação ou aprovação humana.

Ao mesmo tempo, é importante impor limites:

- máximo de chamadas ao modelo;
- máximo de tentativas por ferramenta;
- tempo máximo de execução;
- tamanho máximo de arquivos e respostas;
- aprovação para ações com efeitos externos.

Limites protegem contra loops, custos inesperados e agentes presos em uma
interface que mudou.

## Avaliação iterativa e critério de sucesso

Uma resposta plausível não prova que a tarefa foi concluída. Uma arquitetura
mais confiável separa **execução** de **avaliação**:

```text
pedido + critério
       ↓
agente tenta executar
       ↓
avaliador verifica resultado e evidências
   ├─ aprovado → finalizar
   └─ incompleto → feedback → nova tentativa
```

O avaliador pode ser outro modelo com saída estruturada, mas deve receber
evidências verificáveis: arquivos criados, chamadas de ferramentas, valores
encontrados ou mensagens retornadas.

```python
class Avaliacao(BaseModel):
    concluido: bool
    feedback: str

avaliador = llm.with_structured_output(Avaliacao)

def avaliar(resultado, criterio) -> Avaliacao:
    evidencias = resultado.get("messages", [])
    return avaliador.invoke(
        f"Critério: {criterio}\nEvidências: {evidencias}"
    )
```

O loop da aplicação pode então dar feedback ao agente:

```python
def executar_ate_concluir(agent, tarefa, criterio, max_tentativas=3):
    mensagens = [{"role": "user", "content": tarefa}]

    for _ in range(max_tentativas):
        resultado = agent.invoke({"messages": mensagens})
        avaliacao = avaliar(resultado, criterio)
        if avaliacao.concluido:
            return resultado

        mensagens += [
            resultado["messages"][-1],
            {"role": "user", "content": f"Corrija: {avaliacao.feedback}"},
        ]

    raise RuntimeError("Critério não atingido no limite de tentativas")
```

O exemplo é um esqueleto: em uma aplicação real, preserve as mensagens e as
evidências no formato esperado pelo agente e avalie arquivos ou efeitos
externos diretamente, em vez de confiar apenas no texto final. O limite de
tentativas é essencial: avaliação sem limite pode criar outro loop infinito.

## Observabilidade e interface

**Observabilidade** é a capacidade de enxergar o que aconteceu, não apenas a
resposta final. Uma execução útil para diagnóstico registra:

- entrada e saída de cada nó;
- chamadas e argumentos das ferramentas;
- duração e erros;
- tokens e custo, quando disponíveis;
- checkpoints e decisões humanas.

Uma plataforma de tracing, como o LangSmith, pode exibir essa árvore de
execução. Isso ajuda a descobrir se o problema foi o prompt, a decisão do
modelo, a ferramenta ou o fluxo.

Tracing não é memória nem avaliação: ele registra o que aconteceu para que
uma pessoa possa investigar. Não envie dados sensíveis ao serviço de tracing
sem configurar retenção e mascaramento adequados.

Uma interface como Gradio pode apenas adaptar o fluxo para uma pessoa:

```text
campo de tarefa → agente → histórico de mensagens
                         ├─ plano em andamento
                         └─ botão Aprovar quando houver pausa
```

A interface não substitui o estado do agente. Ela deve apenas mostrar o
progresso, encaminhar mensagens e enviar decisões de aprovação ou retomada ao
fluxo persistido. Em uma interface real, o botão de aprovação chama o
`invoke(Command(resume=...))` usando o mesmo `thread_id`; criar outro thread
perde o ponto em que o agente estava pausado.

## Como escolher o nível de abstração

```text
mais controle                                            mais conveniência
Core → LangGraph → create_agent → Deep Agent
```

- **Core**: controle manual de mensagens, tools, loop e schema.
- **LangGraph**: controle explícito de estado, nós, decisões, memória e
  recuperação.
- **`create_agent`**: loop padrão pronto para um agente com ferramentas.
- **Deep Agent**: planejamento, arquivos e delegação para tarefas longas.

Uma regra prática:

```text
Precisa controlar cada transição?       → LangGraph
Precisa de um agente comum com tools?   → create_agent
Precisa planejar e produzir arquivos?   → Deep Agent
Precisa só chamar modelo/tools à mão?   → langchain-core
```

As camadas podem ser combinadas. Por exemplo, um projeto pode usar
`create_agent` como trabalhador, ferramentas definidas com `@tool`, memória
do LangGraph, servidores MCP e um loop de avaliação escrito pela própria
aplicação. A melhor escolha é usar a abstração mais alta que ainda preserve o
controle necessário.

Em qualquer camada, verifique estes cinco pontos antes de considerar o agente
pronto:

1. qual estado é necessário e quando ele é persistido;
2. quais ferramentas podem causar efeitos externos;
3. qual é a condição de parada;
4. como falhas, limites e aprovações são tratados;
5. quais evidências mostram que o objetivo foi realmente alcançado.
