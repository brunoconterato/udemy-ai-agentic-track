# AGENTS.md

## Objetivo

Este repositório reúne materiais e projetos do curso de AI agentic.
Trabalhe sempre com mudanças pequenas, focadas e fáceis de validar.

## Como navegar

- Antes de editar um diretório, leia o `README.md` ou a documentação local dele.
- Se houver mais de um subprojeto, mexa só no que estiver no escopo da tarefa.
- Prefira instruções locais quando existirem, porque elas têm prioridade sobre este arquivo.

## Estrutura geral

- `1_foundations/`, `2_openai/`, `3_crew/`, `4_langgraph/`, `5_autogen/`, `6_mcp/`: materiais e exemplos do curso.
- `brunoconterato/`: anotações e exercícios do aluno.
- `assets/`: imagens e recursos compartilhados.
- `setup/` e `guides/`: documentação de apoio.

## Comandos úteis

- Instalar dependências: `uv sync`
- Executar código Python no ambiente: `uv run python <arquivo>`
- Abrir notebooks: `uv run jupyter lab` ou o fluxo já usado no subprojeto

Se um subprojeto tiver comandos próprios no `README.md`, use esses comandos antes dos genéricos.

## Convenções

- Mantenha o estilo já usado no arquivo alterado.
- Evite refatorações grandes fora do pedido.
- Não adicione dependências sem necessidade clara.
- Não edite arquivos gerados, caches ou artefatos de build.
- Não mexa em segredos, chaves, `.env` ou credenciais.

## Notebooks

- Preserve a intenção didática do notebook.
- Evite limpar saídas ou reformatar células sem motivo.
- Se a mudança for só em texto ou exemplo, altere apenas a parte necessária.

## Validação

- Rode o menor conjunto de checagens possível para confirmar a mudança.
- Se não houver teste automatizado no subprojeto, explique como validou.
- Considere pronto quando o diff ficar restrito ao escopo pedido e a alteração estiver consistente com a documentação local.
