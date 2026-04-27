# research_agent

A reflective writing workflow that chains three LLM calls to improve output quality beyond what a single-pass generation can achieve.

## How it works

1. **Draft** — GPT-4o generates an initial piece of writing based on the prompt.
2. **Critique** — o4-mini (reasoning model) reviews the draft and returns specific, actionable feedback.
3. **Revise** — GPT-4o rewrites the draft incorporating the critique.

The pattern demonstrates that routing tasks to models best suited for each role (generative vs. evaluative) consistently outperforms a single-model approach.

## Pattern

Reflection

## Tools

**AISuite**, **OpenAI** (GPT-4o, o4-mini)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install aisuite openai python-dotenv
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

## Run

Open `main.ipynb` in Jupyter and run all cells.
