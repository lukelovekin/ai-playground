# autonomous_agents

Two autonomous agent patterns — a multi-agent market research pipeline and a code-as-action customer service agent.

## Projects

### Market research pipeline (`market_research_pipeline.ipynb`)

A team of agents produces a complete product campaign:

1. **Researcher** — gathers market data via Tavily web search.
2. **Image generator** — DALL-E generates product imagery based on the research.
3. **Copywriter** — writes marketing copy using the image as multimodal input (vision + text).
4. **Executive** — compiles everything into a final structured report.

### Customer service agent (`customer_service_agent.ipynb`)

A code-as-action agent that handles natural language inventory queries by dynamically writing and executing DuckDB queries against a live sunglasses inventory — rather than calling pre-defined tool functions.

The agent can:
- Look up products by name or ID
- Update stock quantities
- Record transactions and recalculate balances
- Validate business rules (non-negative stock, required fields)

Tool functions are registered in a `TOOL_REGISTRY` and dispatched by the agent at runtime.

### Code execution agent (`code_execution_agent.ipynb`)

Demonstrates an agent that generates and executes Python code as its action mechanism.

## Pattern

Multi-agent, Code-as-action

## Tools

**OpenAI** (GPT-4o, DALL-E), **AISuite**, **DuckDB**, **TinyDB**, **Tavily** (web search), **pandas**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install aisuite openai tavily-python duckdb tinydb pandas python-dotenv
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Run

Open the relevant notebook in Jupyter and run all cells.
