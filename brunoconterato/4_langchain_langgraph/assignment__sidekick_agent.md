# Assignment — Sidekick Agent

## Objetivo

Desenvolva o **Sidekick**, um agente autônomo com LangChain capaz de receber uma tarefa e seus critérios de sucesso, planejar a execução, utilizar ferramentas e continuar trabalhando até que o objetivo seja atingido.

Use `create_agent` como base principal da implementação.

O agente deve ser um trabalhador baseado em `create_agent`, envolvido por um
loop próprio que avalia o resultado e, quando necessário, devolve feedback ao
agente para uma nova tentativa.

## Requisitos

O Sidekick deve:

- receber uma **tarefa** e **critérios de sucesso**;
- criar e atualizar uma **Todo List**;
- manter **memória/estado** durante a execução;
- utilizar ferramentas reais;
- permitir **Human-in-the-Loop**;
- aplicar **guardrails**;
- possuir um **limite de execução ou orçamento**;
- submeter o resultado a um **Evaluator independente**.

O estado deve ser preservado entre chamadas de ferramenta e pausas. Quando o
navegador ou o sistema de arquivos forem usados via MCP, mantenha as sessões
ativas durante a execução para que o trabalho possa continuar do mesmo ponto.

### Ferramentas obrigatórias

Implemente acesso a:

- **Browser / Playwright** para navegação web;
- **File System** para leitura e escrita de arquivos;
- **Push Notification**, como Pushover, para notificar o usuário.

### Middleware

Utilize middleware para incluir:

- gerenciamento da Todo List;
- proteção/redação de informações pessoais;
- controle de orçamento, chamadas ou número máximo de passos.

Também é recomendável tratar falhas de ferramentas como feedback para o
modelo, permitindo recuperação sem encerrar o agente imediatamente.

### Human-in-the-Loop

O agente deve poder pausar a execução para solicitar uma decisão humana e depois continuar utilizando o estado existente.

### Evaluator

Crie uma chamada separada a um LLM que receba:

```text
Tarefa + Critérios de sucesso + Resultado
```

e retorne uma avaliação estruturada.

Exemplo:

```json
{
  "approved": false,
  "feedback": ["Falta comparar os preços."]
}
```

Se reprovado, o feedback deve voltar ao Sidekick para uma nova tentativa. Se aprovado, a execução termina.

## Fluxo esperado

```text
Usuário
  ↓
Sidekick
  ↓
Planejamento / Todo List
  ↓
Ferramentas
  ↓
Resultado
  ↓
Evaluator
  ├─ aprovado → concluir
  └─ reprovado → feedback → Sidekick
```

## Demonstração

Execute pelo menos uma tarefa que exija múltiplas etapas e uso real das ferramentas.

Exemplo:

```text
Tarefa:
Pesquise três plataformas para execução de modelos de IA
e produza um relatório comparativo.

Critérios:
- comparar pelo menos três opções;
- incluir preços;
- apresentar vantagens e desvantagens;
- salvar o relatório em Markdown;
- enviar uma notificação ao concluir.
```

## Exemplos de aplicação do notebook

Use os exemplos abaixo como referência para a demonstração ou para criar uma
variação própria. Eles representam diferentes níveis do Sidekick:

1. **Pesquisa rápida e notificação:** pesquisar quem ganhou o Nobel de Física
   de 2023 e enviar um resumo curto por push notification.
2. **Ação com aprovação humana:** solicitar o agendamento de uma reunião com
   Sam na sexta-feira. O agente deve pausar antes de executar a ferramenta;
   a pessoa pode aprovar, editar ou rejeitar a ação.
3. **Consulta no navegador:** acessar o Hacker News e informar o título da
   notícia que está no topo da página naquele momento.
4. **Pesquisa comparativa com artefato:** procurar as três melhores opções de
   voo de ida e volta entre Nova York e Londres, priorizando preço e depois
   duração, salvar as opções e a recomendação em `flights.md` e notificar o
   preço da escolha principal.
5. **Intervenção humana no navegador:** iniciar uma pesquisa no Expedia e,
   ao chegar à tela de login, pedir que a pessoa faça o login, captcha ou
   autenticação de dois fatores na janela do navegador e depois continuar.

Em tarefas que envolvam informação pessoal, confirme também que os e-mails de
entrada e os números de cartão presentes nos resultados das ferramentas são
redigidos antes de chegar ao modelo ou ao resultado final.

## Exemplo de radação de aplicação

Tarefa: Pesquise três plataformas para execução de modelos de IA e produza um relatório comparativo.

Critérios de sucesso:

- apresentar pelo menos três alternativas;
- comparar preços;
- apresentar vantagens e desvantagens;
- produzir uma recomendação;
- salvar o relatório em Markdown;
- enviar uma notificação ao terminar.

## Entregáveis

Entregue:

- código-fonte executável;
- `README.md` com instruções de instalação e uso;
- `.env.example` sem credenciais;
- uma demonstração completa da execução.

## Critério de conclusão

O projeto estará completo quando demonstrar:

`create_agent` + ferramentas + memória + Todo List + middleware + guardrails + limite de execução + Human-in-the-Loop + Evaluator independente.

Na demonstração completa, mostre a Todo List durante a execução, o ponto de
pausa e retomada, o artefato produzido, a notificação (quando aplicável) e a
decisão do Evaluator. Se a avaliação reprovar o resultado, mostre pelo menos
uma nova tentativa usando o feedback recebido.

> **O usuário define a tarefa e o que significa sucesso. O Sidekick decide como executar o trabalho e continua até atingir esses critérios.**
