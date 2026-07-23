# engineering_team

A crewAI project using JSON-first configuration.

## Início rápido

```bash
crewai run
```

As tools de sandbox recebem `module_name` e organizam os arquivos em
`sandbox/<modulo_normalizado>`. Por exemplo, `Relatório de Vendas` vira
`sandbox/relatorio_de_vendas`. A tool de listar arquivos cria essa pasta quando
necessário; as demais também a criam antes de ler, escrever ou executar.

## Running

```bash
crewai run
```

## Project Structure

- `agents/` - Agent definitions (JSONC)
- `crew.jsonc` - Crew definition with tasks and configuration
- `tools/` - Custom tools (Python)
- `knowledge/` - Knowledge files for agents

> **Note:** `custom:<name>` tool references execute `tools/<name>.py` as local
> Python code when the crew loads. Only run crew projects from sources you
> trust.
