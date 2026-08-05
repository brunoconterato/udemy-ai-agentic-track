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
