# Pesquisa Web Local para `finantial_researcher_bruno`

Este documento explica, de forma manual, como configurar o projeto para que o agente pesquise na web sem depender de APIs pagas de busca.

O objetivo e manter apenas dependencias locais para:

- modelo LLM;
- busca web;
- leitura de paginas;
- extracao de texto.

## O que existe hoje no projeto

Hoje o projeto ja esta estruturado assim:

- `pesquisador_financeiro` usa um LLM local via Ollama;
- o agente ja tem uma tool de pesquisa web configurada em `crew.py`;
- o fluxo usa `tasks.yaml` para guiar pesquisa e analise.

O ponto importante e este:

- se a sua meta for reduzir custo e evitar APIs pagas, voce precisa garantir que a busca web tambem seja local;
- para isso, o caminho mais previsivel e usar um serviço local de busca como o DDGS e uma etapa local de download/extracao como `trafilatura`.

## As duas ferramentas locais recomendadas

Para um setup totalmente local, o agente de pesquisa deve ter acesso a duas capacidades:

1. Busca web local
2. Leitura/extração de pagina local

Na pratica:

- a busca retorna URLs e pequenos sinais textuais;
- a extração baixa o HTML da URL e transforma em texto limpo.

## Como isso se encaixa no projeto

Sem implementar nada agora, o encaixe conceitual e este:

- `src/finantial_researcher_bruno/crew.py`
  - centraliza o LLM e as tools do agente;
  - e o lugar onde voce conecta as tools locais ao `pesquisador_financeiro`.

- `src/finantial_researcher_bruno/tools/`
  - e o lugar mais limpo para criar as tools separadas;
  - uma tool para buscar;
  - outra para extrair o conteudo da pagina.

- `src/finantial_researcher_bruno/config/tasks.yaml`
  - deve orientar o pesquisador a usar URLs completas e priorizar fontes publicas;
  - pode reforcar que a pesquisa deve registrar limitacoes quando um site nao responder.

## Configuracao manual recomendada

### 1. Mantenha o Ollama como LLM local

O projeto ja suporta isso.

Use:

- `MODEL=ollama/<seu-modelo>`
- `OLLAMA_API_BASE=http://localhost:11434`
- `EMBEDDINGS_OLLAMA_MODEL_NAME=nomic-embed-text`

Isso evita API paga para a parte de raciocinio e geracao.

### 2. Suba um servidor local de busca DDGS

O repositorio do DDGS pode rodar como API local e expor:

- `http://localhost:4479/search/text`
- `http://localhost:4479/health`

O compose dele mapeia a porta externa `4479` para a interna `8000`.

Esse servidor e a base da busca local.

### 3. Use `trafilatura` para baixar pagina e extrair texto

Depois de obter a URL, a etapa de leitura deve:

- baixar o conteudo com `fetch_url`;
- extrair o texto com `extract`;
- retornar um texto enxuto para o agente resumir.

### 4. Ligue as duas tools ao mesmo agente

O `pesquisador_financeiro` deve receber:

- uma tool de busca;
- uma tool de leitura de pagina.

Se voce quiser manter o projeto previsivel, evite depender de uma tool que esconda a origem da busca em um fornecedor externo.

## Fluxo mental da execucao

O fluxo ideal fica assim:

1. O agente de pesquisa recebe a empresa e a data.
2. Ele gera termos de busca.
3. A tool local de busca consulta o DDGS.
4. A tool de leitura baixa cada URL e extrai o texto.
5. O pesquisador junta os fatos.
6. O analista transforma isso em relatorio executivo.

## Passos manuais para configurar do zero

### Ambiente

- Instale `uv`.
- Instale `docker`.
- Use Python compatível com o projeto, ou seja, `>=3.10,<3.13`.

### Dependencias do projeto

No diretório do projeto:

```bash
uv sync
```

### Dependencias para leitura de pagina

Se o ambiente ainda nao tiver `trafilatura`, instale-a no ambiente usado pelo notebook ou pela crew:

```bash
uv pip install trafilatura
```

### Serviço de busca local

Se voce ainda nao tiver o repo do DDGS:

```bash
git clone https://github.com/deedy5/ddgs /home/bruno/Workspace/lib/ddgs
```

Depois suba o serviço:

```bash
cd /home/bruno/Workspace/lib/ddgs
docker compose up -d --build
```

### Ollama

Suba o container local:

```bash
docker start ollama-local
```

Ou recrie usando o helper do workspace:

```bash
../script/run_ollama_docker.sh
```

### Execucao

Depois disso, rode a crew:

```bash
uv run crewai run
```

## O que ajustar se voce for implementar as tools depois

Quando for transformar estas instrucoes em codigo, os pontos de ajuste mais provaveis sao:

- `crew.py`
  - trocar a dependencia da tool de busca para a tool local;
  - adicionar a tool de leitura de pagina.

- `tools/custom_tool.py`
  - usar como base para uma tool local propria;
  - ou criar dois arquivos separados para busca e extracao.

- `tasks.yaml`
  - reforcar que a pesquisa deve priorizar fontes publicas e URLs completas.

## Checklist rapido

- Ollama respondendo em `http://localhost:11434`
- DDGS respondendo em `http://localhost:4479/health`
- `trafilatura` instalada no ambiente
- `uv sync` executado no projeto
- `crewai run` funcionando sem depender de API paga de busca

