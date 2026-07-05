# Local Web Research Stack

Este guia documenta o padrao usado em `brunoconterato/2_openai/my_deep_research.ipynb` para fazer pesquisa na web sem depender de APIs pagas para busca.

O objetivo aqui e servir como referencia reutilizavel para qualquer projeto dentro de `brunoconterato` que precise:

- buscar paginas na web;
- baixar o conteudo de uma pagina;
- resumir o material com um modelo local;
- rodar do zero em uma maquina nova com `python`, `uv` e `docker`.

## Visao geral

O fluxo do notebook e este:

1. Um agente `Planner` gera termos de busca.
2. Um agente `Search agent` chama uma tool local chamada `search_web`.
3. `search_web` consulta um servidor local na porta `4479`.
4. Esse servidor retorna resultados de busca com URLs.
5. O notebook baixa cada URL com `trafilatura` e extrai o texto limpo da pagina.
6. Um agente `WriterAgent` sintetiza o relatorio final.

As duas pecas locais principais sao:

- Ollama para o modelo LLM;
- DDGS API para busca web.

## O que roda localmente

### 1. Modelo

O notebook aponta para o Ollama local:

- `http://localhost:11434/v1`

Isso significa que a geracao do texto nao precisa de OpenAI API, desde que o modelo esteja rodando no Ollama.

### 2. Busca web

A tool `search_web` faz uma chamada HTTP para:

- `http://localhost:4479/search/text`

Esse endpoint pertence ao servidor local do projeto `ddgs`.

### 3. Download e extracao de pagina

Depois de receber as URLs, o notebook usa `trafilatura`:

- `fetch_url(url)` para baixar a pagina;
- `extract(...)` para limpar e extrair o texto.

Isso permite ler conteudo de paginas diretamente, sem usar um servico pago de scraping.

## O que nao e local

Mesmo sem API paga, a busca ainda depende da internet, porque o DDGS consulta fontes publicas na web.

Entao o custo fica assim:

- sem custo de API para busca;
- sem custo de API para extracao;
- ainda precisa de conexao com a internet;
- ainda precisa aceitar que alguns sites podem bloquear, redirecionar ou falhar.

## Como o notebook funciona

### 1. Modelo Ollama

O notebook cria um cliente OpenAI-compativel apontando para o Ollama:

```python
ollama_client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
model = OpenAIChatCompletionsModel(model=CONFIG.model, openai_client=ollama_client)
```

O ponto importante e:

- `base_url` precisa apontar para o Ollama;
- `CONFIG.model` precisa existir no Ollama;
- a chave `api_key` e apenas um placeholder para a interface OpenAI-compativel.

### 2. Tool de busca

A tool local e esta:

```python
@function_tool
async def search_web(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:4479/search/text",
            params={"query": query, "max_results": 5},
        )
```

Depois disso:

- a resposta JSON e percorrida;
- cada resultado traz `title` e `href`;
- a URL em `href` e baixada com `trafilatura`;
- o texto extraido vira entrada para o agente de resumo.

### 3. Pipeline de agentes

O pipeline final e:

- `planner_agent`: cria o plano de busca;
- `search_agent`: pesquisa e resume cada termo;
- `writer_agent`: escreve o relatorio final.

O fluxo assicrono executa as buscas em paralelo com `asyncio.gather`, o que deixa o processo bem mais rapido.

## Capacidades verificadas

Este stack consegue:

- buscar na web por texto;
- obter resultados com titulo e link;
- baixar o conteudo de uma pagina;
- extrair texto limpo da pagina;
- resumir o resultado localmente com Ollama.

Este stack nao faz, por padrao:

- navegacao visual com browser automatizado;
- clique em pagina com Playwright/Selenium;
- screenshot;
- login em site;
- bypass de paywall ou captcha.

Se um projeto precisar disso, e outra camada, nao esta neste notebook.

## Como descobrir o DDGS aqui nesta maquina

O container que existia nesta maquina aparece como:

- `ddgs-ddgs-api-1`

O projeto que o criou fica em:

- `/home/bruno/Workspace/lib/ddgs`

Os metadados do Docker mostram que ele veio do compose desse diretorio e que expoe:

- container interno: `8000`
- porta publica: `4479`

## Como iniciar o DDGS

Se o projeto ainda nao existir nesta maquina, clone primeiro:

```bash
git clone https://github.com/deedy5/ddgs /home/bruno/Workspace/lib/ddgs
```

Se o container ja existe, o jeito mais direto e:

```bash
docker start ddgs-ddgs-api-1
```

Se voce quer recriar do zero a partir do projeto fonte:

```bash
cd /home/bruno/Workspace/lib/ddgs
docker compose up -d --build
```

O repo do DDGS tambem fornece um script de inicio:

```bash
./start_api.sh
```

Esse script:

- cria `.venv` se faltar;
- instala `ddgs[api]`;
- sobe o FastAPI/Uvicorn em `0.0.0.0:8000`.

O `docker-compose.yml` mapeia isso para a porta local `4479`.

## Como validar que subiu

Cheque estes endpoints:

```bash
curl http://localhost:11434/v1/models
curl http://localhost:4479/health
```

Se a segunda chamada responder `200`, o buscador local esta pronto.

## Passo a passo para uma maquina nova

### Requisitos

- Python 3.12 ou mais novo, porque o workspace raiz usa `requires-python = ">=3.12"`.
- `uv` instalado.
- `docker` instalado e rodando.
- acesso a internet.

### 1. Clonar o workspace

```bash
git clone <repo>
cd udemy-ai-agentic-track
```

### 2. Instalar dependencias do workspace

```bash
uv sync
```

Isso prepara o ambiente raiz com `openai-agents`, `httpx`, `ipykernel` e demais dependencias do workspace.

### 3. Garantir `trafilatura`

O notebook usa `trafilatura`, entao verifique se ela esta instalada no ambiente que vai executar o notebook.

Se faltar, instale uma vez no ambiente do projeto sem alterar o `pyproject.toml`:

```bash
uv pip install trafilatura
```

Se voce nao quiser alterar o `pyproject.toml`, use apenas a instalacao local correspondente ao seu fluxo de notebook.

### 4. Subir o Ollama

No projeto `brunoconterato`, existe um helper para isso:

```bash
cd brunoconterato/script
./run_ollama_docker.sh
```

Ou, se o container ja estiver criado:

```bash
docker start ollama-local
```

### 5. Subir o DDGS

Se voce ainda nao tiver o repo do DDGS nesta maquina, clone primeiro:

```bash
git clone https://github.com/deedy5/ddgs /home/bruno/Workspace/lib/ddgs
```

Depois suba o serviço:

```bash
cd /home/bruno/Workspace/lib/ddgs
docker compose up -d --build
```

Se estiver reaproveitando um container parado:

```bash
docker start ddgs-ddgs-api-1
```

### 6. Abrir o notebook

Use o fluxo que voce ja adota para notebooks nesse workspace.

Se quiser rodar em Jupyter, certifique-se de usar o mesmo ambiente do `uv sync`.

### 7. Executar a pesquisa

No notebook, o fluxo final chama:

```python
result = await deep_research(CONFIG.query_example)
```

## Como adaptar para outros projetos em `brunoconterato`

Se outro projeto precisar do mesmo padrao, reutilize esta estrutura:

1. Um agente para planejar a busca.
2. Uma tool local para consultar o DDGS.
3. Uma etapa para baixar e limpar cada pagina.
4. Um agente para sintetizar a resposta final.

Esse desenho e bom quando voce quer:

- reduzir custo;
- manter a busca fora de APIs pagas;
- manter a explicacao do fluxo simples;
- trocar facilmente o modelo local depois.

## Observacoes praticas

- Se `http://localhost:4479/search/text` falhar, o problema quase sempre e o DDGS parado ou a porta errada.
- Se `http://localhost:11434/v1` falhar, o problema quase sempre e o Ollama parado.
- Se uma pagina nao extrair texto, tente outra URL do mesmo dominio ou reduza a dependencia de paginas dinamicas.
- Se o projeto for levado para outra maquina, o caminho absoluto do DDGS pode mudar; o importante e manter a porta `4479`.

## Resumo final

Este notebook faz pesquisa web local sem usar `WebSearchTool` pago da OpenAI.

O desenho real e:

- Ollama local para inferencia;
- DDGS local para busca web;
- `trafilatura` para baixar e extrair paginas;
- agentes do OpenAI Agents SDK para planejar, resumir e escrever o relatorio.

Para reproduzir do zero, o essencial e:

1. `uv sync`
2. subir Ollama
3. subir DDGS na porta `4479`
4. garantir `trafilatura`
5. executar o notebook
