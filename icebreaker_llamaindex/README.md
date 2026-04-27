# icebreaker

An AI-powered assistant that generates personalised icebreakers and conversation starters from LinkedIn profiles. Scrapes profile data via ProxyCurl, builds a RAG index with IBM WatsonX embeddings, and answers questions about the person using LlamaIndex.

## How it works

1. LinkedIn profile data is retrieved via ProxyCurl API (or mock data if no key is provided).
2. The profile text is split into chunks and embedded using IBM WatsonX embeddings.
3. Embeddings are stored in a vector index via LlamaIndex.
4. On query, relevant profile sections are retrieved and passed to an IBM WatsonX LLM for generation.

The default output is three interesting facts about the person as a conversation starter. Follow-up questions are answered via RAG over the indexed profile.

## Pattern

RAG

## Tools

**LlamaIndex**, **IBM WatsonX** (WatsonxLLM, WatsonxEmbeddings), **ProxyCurl API**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Optionally add a ProxyCurl API key to `config.py` for live profile lookups. Without it, mock data is used.

## Run

```bash
# CLI
python main.py --mock
python main.py --url "https://www.linkedin.com/in/username/" --api-key "your_key"

# Gradio web interface
python app.py
```

The web interface starts at `http://127.0.0.1:7860`.

## Project structure

```
icebreaker/
├── app.py                  # Gradio interface
├── main.py                 # CLI entry point
├── config.py               # API keys and prompt templates
└── requirements.txt
```
