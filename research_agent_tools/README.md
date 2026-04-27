# research_agent_tools

An agentic research pipeline that accepts a research question, searches multiple sources in parallel, synthesises a structured report, reflects on gaps, then converts the final output to styled HTML.

## How it works

1. **Research** — the agent calls arXiv (academic papers) and Tavily (web) in parallel using tool calling.
2. **Synthesise** — results are combined into a structured Markdown report.
3. **Reflect** — the model reviews its own output, identifies gaps or weak sections, and revises.
4. **Publish** — the final report is converted to styled HTML for presentation.

## Tools available to the agent

| Tool | Source |
|---|---|
| `arxiv_search_tool` | arXiv API — returns titles, authors, abstracts, PDF links |
| `tavily_search_tool` | Tavily API — general web search |
| `wikipedia_search_tool` | Wikipedia — article summaries |

## Pattern

Agentic tool use, Reflection

## Tools

**OpenAI**, **Tavily** (web search), **arXiv API**, **Wikipedia API**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install openai tavily-python wikipedia python-dotenv
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Run

Open `research_agent.ipynb` in Jupyter and run all cells.
