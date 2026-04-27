# reflection_pattern

Implements the reflection pattern in two contexts: iterative chart generation with visual feedback, and self-correcting SQL generation.

## Projects

### Chart generation (`chart_generation_reflection.ipynb`)

1. GPT-4o-mini generates matplotlib chart code from a natural language description.
2. The code is executed and the chart is rendered to an image.
3. A vision model (o4-mini or Claude) inspects the rendered image and critiques it.
4. The code is revised based on the critique and re-rendered.
5. Repeat until the chart meets the specification.

### SQL generation (`sql_generation_reflection.ipynb`)

1. An LLM translates a natural language question into SQL.
2. The query is executed against a SQLite database (`products.db` — 100 products with brands, categories, colours, pricing).
3. The result (or error) is fed back to the model for self-correction.
4. A separate evaluator model assesses whether the result adequately answers the question.
5. The query is refined if needed.

## Pattern

Reflection, Self-correction

## Tools

**AISuite**, **OpenAI** (GPT-4o, GPT-4o-mini, o4-mini), **Anthropic** (Claude), **matplotlib**, **SQLite**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install aisuite openai anthropic matplotlib python-dotenv
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Run

Open either notebook in Jupyter and run all cells. `products.db` is auto-generated on first run.
