# interactive_food_search

A CLI food recommendation chatbot backed by ChromaDB vector similarity search and IBM Granite, using RAG to give contextually relevant food suggestions.

## How it works

1. Food items are loaded from `FoodDataSet.json` and embedded into a ChromaDB collection.
2. User queries are matched by semantic similarity — the top results are ranked with match scores, cuisine type, calorie info, and health benefits.
3. Matched items are passed as context to IBM Granite (`ibm/granite-3-3-8b-instruct`) which generates a conversational recommendation response.
4. Falls back to a template-based response if the LLM is unavailable.

## Features

- Natural language queries ("something spicy and healthy for dinner")
- Cuisine, calorie, and health benefit details in results
- **Compare mode** — AI-powered side-by-side comparison of two food queries
- Conversation history (last 3 turns retained for context)

## Pattern

RAG, Vector similarity search

## Tools

**ChromaDB**, **IBM WatsonX** (Granite 3.3 8B)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install ibm-watsonx-ai chromadb
```

## Run

```bash
# Enhanced RAG chatbot (recommended)
python enhanced_rag_chatbot.py

# Basic interactive search
python interactive_search.py
```

### Example queries

- `"I want something spicy and healthy for dinner"`
- `"What Italian dishes do you recommend under 400 calories?"`
- `"Suggest some protein-rich breakfast options"`
- `compare` — enter two queries for AI-powered side-by-side analysis
