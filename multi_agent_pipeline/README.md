# multi_agent_pipeline

A multi-agent research system where four specialised agents collaborate via an orchestrator to produce a polished research report.

## How it works

```
Planner → Researcher → Writer → Editor
```

1. **Planner** — breaks the research topic into focused sub-questions.
2. **Researcher** — queries Tavily (web), arXiv (academic papers), and Wikipedia for each sub-question.
3. **Writer** — drafts a structured report from the gathered findings.
4. **Editor** — reviews and polishes the final output for clarity and coherence.

Each agent is a separate LLM call with a distinct system prompt and role. The orchestrator coordinates the handoffs between agents.

## Tools available to agents

| Tool | Source |
|---|---|
| `arxiv_search_tool` | arXiv API |
| `tavily_search_tool` | Tavily web search |
| `wikipedia_search_tool` | Wikipedia summaries |

## Pattern

Multi-agent orchestration

## Tools

**AISuite**, **Tavily** (web search), **arXiv API**, **Wikipedia API**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install aisuite tavily-python wikipedia python-dotenv requests
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Run

Open `multi_agent_research_pipeline.ipynb` in Jupyter and run all cells.
