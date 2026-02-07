# Week 1 - Day 2 - Theory Notes

## Agentic Systems

Anthropic distinguishes between two types of AI systems: **Workflows** and **Agents**.

- **Workflows** are systems where LLMs and tools are orchestrated through predefined code paths.
- **Agents** are systems where LLMs dinamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.

### Comments and examples

- **🔁 Workflows**: An example of a workflow is a customer support chatbot that follows a fixed script to answer common questions. The LLM processes user input and selects from a set of predefined responses or actions based on the input, without deviating from the established flow.
- **🤖 Agents**: An example of an agent is a personal assistant AI that can autonomously decide which tools to use (like calendar management, email drafting, or web searching) based on the user's requests. The agent evaluates the context and determines the best course of action to fulfill the user's needs, adapting its strategy as necessary.

## 🔁 Workflow design patterns

### 1. Prompt Chaining Pattern

Link multiple LLM prompts together, passing the output of one as the input to the next.

Example schema:

```mermaid
flowchart LR
    Input["Input"] --> P1["LLM Prompt 1"] --> O1["Output 1"] --> P2["LLM Prompt 2"] --> O2["Output 2"] --> Ellipsis["..."] --> PN["LLM Prompt N"] --> OF["Final Output"]
        classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
        classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
        class P1,P2,PN llm
        class Input,O1,O2,OF io
```

### 2. Routing Pattern

Direct an input into different paths based on its content.

Example schema:

```mermaid
flowchart LR
    Input["Input"] --> Router["LLM Router"]
    Router -->|if condition A| LLM1["LLM 1"] --> OutputA["Output A"]
    Router -->|if condition B| LLM2["LLM 2"] --> OutputB["Output B"]
    Router -->|if condition C| LLM3["LLM 3"] --> OutputC["Output C"]
        classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
        classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
        class Router,LLM1,LLM2,LLM3 llm
        class Input,OutputA,OutputB,OutputC io
```

### 3. Parallelization Pattern

Breaking down a task into multiple sub-tasks that can be processed simultaneously.

```mermaid
flowchart TB
    Input((Input)) --> Coordinator["Coordinator (code)"]
    Coordinator --> Sub1["Sub-task 1<br/>output 1"]
    Coordinator --> Sub2["Sub-task 2<br/>output 2"]
    Coordinator --> Sub3["Sub-task 3<br/>output 3"]
    Sub1 --> Aggregator["Aggregator"]
    Sub2 --> Aggregator
    Sub3 --> Aggregator
    Aggregator --> Final((Final output))
        classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
        classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
        class Input,Final io
```

### 4. Orchestrator-Worker Pattern

Complex tasks are broken down dinamically and combined.

```mermaid
flowchart TB
    Input((Input)) --> Orchestrator["Orchestrator LLM"]
    Orchestrator --> Worker1["Worker LLM 1<br/>task 1"]
    Orchestrator --> Worker2["Worker LLM 2<br/>task 2"]
    Orchestrator --> Tool1["Tool 1<br/>task 3"]
    Worker1 --> Synthesizer["Synthesizer LLM"]
    Worker2 --> Synthesizer
    Tool1 --> Synthesizer
    Synthesizer --> Final((Final output))
        classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
        classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
        class Orchestrator,Worker1,Worker2,Synthesizer llm
        class Input,Final io
```

### 5. Evaluator-Optimizer Pattern

LLM output is validated by another.

```mermaid
flowchart TB
    Input((Input)) --> Generator["Generator LLM"]
    Generator --> Output1["Generated Output"]
    Output1 --> Evaluator["Evaluator LLM"]
    Evaluator -->|if output is good| Final["Final Output"]
    Evaluator -->|if output is bad| Generator
        classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
        classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
        class Generator,Evaluator llm
        class Input,Output1,Final io
```

## Legend

```mermaid
graph TD
    subgraph Legend
        LLMLegend["LLM (yellow)"]
        IOLegend["Input/Output (orange)"]
    end
    classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
    classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
    class LLMLegend llm
    class IOLegend io
```

## By contrast, Agents

1. Open-ended
   - Workflows have a predefined path; agents can adapt and change their approach.
2. Feedback loops
   - Agents can evaluate their own performance and adjust strategies.
3. No fixed paths
   - Agents decide which tools to use and when, rather than following a set sequence.

```mermaid
flowchart LR
    Human((HUMAN)) --> LLM["LLM<br>Call"]
    LLM --|Action|--> Env((ENVIRONMENT))
    Env --|Feedback|--> LLM
    LLM --> Stop([STOP])
    classDef llm fill:#ffeb3b,stroke:#333,stroke-width:1px,color:#000
    classDef io fill:#ff9800,stroke:#333,stroke-width:1px,color:#000
    classDef stop fill:#1976d2,stroke:#333,stroke-width:1px,color:#fff
    class LLM llm
    class Human,Env io
    class Stop stop
```

## Risks of Agents Frameworks

- Unpredictable path
- Unpredicted outputs
- Unpredictable costs

### Mitigation Strategies

- Monitoring
  - Specially when multi-agent systems are used
  - OpenAi trace, LangGraph, LangSmith etc.
- Guardrails
  - Limit actions and outputs
  - "Guardrail ensure your agents behave safely, consistently, and within your intended boundaries."

## Summary

- Workflows are suitable for well-defined tasks with clear steps, while agents excel in dynamic environments requiring adaptability and decision-making.
- The agentic paradigm is better when compared with the Evaluator-Optimizer Pattern because it allows for more flexibility and adaptability in complex tasks. It's more fluid and can handle unexpected situations better than rigid workflows.
