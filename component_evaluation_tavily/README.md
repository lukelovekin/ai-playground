# component_evaluation

A component-level evaluation harness for an agentic research pipeline. Tests the retrieval step in isolation, validates that returned URLs come from trusted domains, and computes a PASS/FAIL accuracy metric.

## How it works

Rather than evaluating the full pipeline end-to-end, this project isolates and tests the **research/retrieval agent** independently:

1. Run the research agent for a query.
2. Extract all URLs from the returned results.
3. Compare each URL's domain against a predefined `TOP_DOMAINS` allow-list.
4. Compute an approval ratio — PASS if ratio ≥ threshold (default 40%).

The evaluator handles multiple input formats: Tavily-style result lists, JSON strings, and plain text with embedded URLs.

## Key functions (`utils.py`)

| Function | Description |
|---|---|
| `evaluate_anytext_against_domains` | Core evaluator — accepts list, dict, or raw text |
| `evaluate_references` | Finds the most recent research_agent output in history and evaluates it |
| `evaluate_tavily_results` | Targeted evaluator for Tavily result lists |
| `extract_urls` | Extracts URLs from arbitrary text |

## Pattern

Agent evaluation

## Tools

**AISuite**, **Tavily** (web search)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install aisuite tavily-python python-dotenv
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Run

Open `component_evaluation.ipynb` in Jupyter and run all cells.
