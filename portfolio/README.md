---
title: Luke Lovekin - Software Engineer
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.13.0"
python_version: "3.12"
app_file: app.py
pinned: false
---

# portfolio

**Live demo:** https://huggingface.co/spaces/LukeLovekin/about_me_agent

A personal portfolio chatbot where visitors can ask an AI about Luke's background, projects, and skills. Backed by ChromaDB RAG over curated personal data files, streamed through Groq (Llama 3.3 70B), and served via a clean Gradio chat UI. A GitHub MCP server integration is planned for Phase 2 to pull live project data directly from GitHub.

## How it works

```
Visitor asks a question
         │
         ▼
  Gradio Chat UI
         │
         ▼
  ChromaDB RAG
  (Sentence-Transformers)
  retrieves relevant chunks
  from data/ files
         │
         ▼
  Groq API
  (Llama 3.3 70B, streaming)
         │
         ▼
  Streamed answer
  back to UI
```

### Phase 2 (planned)

```
LangGraph ReAct Agent
    ├── Custom FastMCP server     get_bio · get_skills · get_experience
    └── GitHub MCP server         live repos · READMEs · recent activity
```

## Pattern

RAG, Streaming, MCP (planned)

## Tools

**Groq** (Llama 3.3 70B), **ChromaDB**, **Sentence-Transformers**, **Gradio**, **python-dotenv**

## Setup

```bash
cd portfolio
mkvenv                        # or: python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY
```

Build the ChromaDB index (re-run any time `data/` files change):

```bash
python backend/ingest.py
```

## Run

```bash
python app.py
# → http://localhost:7860
```

## Project structure

```
portfolio/
├── app.py                      # Gradio UI + streaming chat
├── backend/
│   ├── ingest.py               # Load data/ into ChromaDB (run once)
│   └── rag.py                  # Retrieval from ChromaDB
├── data/                       # Edit these — re-run ingest.py after changes
│   ├── bio.md                  # Personal bio, personality, links
│   ├── skills.md               # Technical skills by category
│   └── experience.md           # Work history, education, highlights
├── prof_portrait.JPG
├── .env.example
├── .gitignore
└── requirements.txt
```
