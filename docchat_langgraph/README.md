# DocChat

A document Q&A application powered by [Docling](https://github.com/DS4SD/docling), LangGraph, and IBM WatsonX AI. Upload documents, ask questions, and get verified answers backed by a multi-agent pipeline.

## How it works

```
Upload docs → Docling parsing → Hybrid retrieval → LangGraph multi-agent pipeline → Answer + Verification report
```

### Multi-agent pipeline

The LangGraph workflow runs three agents in sequence:

1. **RelevanceChecker** (`ibm/granite-8b-code-instruct`) — classifies whether the retrieved chunks can answer the question (`CAN_ANSWER`, `PARTIAL`, or `NO_MATCH`). If `NO_MATCH`, the pipeline stops early.
2. **ResearchAgent** (`meta-llama/llama-3-2-11b-vision-instruct`) — generates a draft answer grounded in the retrieved context.
3. **VerificationAgent** (`ibm/granite-4-h-small`) — checks the draft answer for factual support, unsupported claims, and contradictions. If verification fails, the workflow loops back to re-research.

```
                    ┌──────────────────┐
                    │  check_relevance  │
                    └────────┬─────────┘
                             │
               ┌─────────────┴─────────────┐
           relevant                    NO_MATCH
               │                           │
               ▼                           ▼
       ┌──────────────┐               ┌─────────┐
  ┌───►│   research   │               │   END   │
  │    └──────┬───────┘               └─────────┘
  │           │
  │           ▼
  │    ┌──────────────┐
  │    │    verify    │
  │    └──────┬───────┘
  │           │
  │    ┌──────┴──────────────┐
  │ re_research             end
  │           │               │
  └───────────┘               ▼
                          ┌─────────┐
                          │   END   │
                          └─────────┘
```

### Document processing

Documents are parsed with **Docling** (handles PDF, DOCX, TXT, MD) and exported to Markdown. Chunks are split by Markdown headers (`#`, `##`) and cached to disk (SHA-256 keyed, 7-day TTL) so repeated uploads skip re-processing.

### Hybrid retrieval

Two retrievers are combined via `EnsembleRetriever`:

- **BM25** (keyword-based, weight 0.4)
- **ChromaDB vector store** with `ibm/slate-125m-english-rtrvr-v2` embeddings via WatsonX (semantic, weight 0.6)

## Project structure

```
docchat/
├── app.py                          # Gradio UI and entry point
├── agents/
│   ├── workflow.py                 # LangGraph StateGraph orchestration
│   ├── relevance_checker.py        # Granite 8B relevance classification
│   ├── research_agent.py           # Llama 3.2 11B answer generation
│   └── verification_agent.py       # Granite 4H answer verification
├── document_processor/
│   └── file_handler.py             # Docling parsing, chunking, disk cache
├── retriever/
│   └── builder.py                  # BM25 + ChromaDB hybrid retriever
├── config/
│   ├── settings.py                 # Pydantic settings (reads .env)
│   └── constants.py                # File size limits, allowed types
└── utils/
    └── logging.py                  # Logger setup
```

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

> WatsonX credentials are picked up from your environment via `ibm_watsonx_ai`. Ensure `WATSONX_APIKEY` (or equivalent) is set.

## Run

```bash
python app.py
```

The app launches at `http://127.0.0.1:5000` with a public share link via Gradio.

## Configuration

Key settings in `.env` or environment variables (defaults shown):

| Variable | Default | Description |
|---|---|---|
| `CHROMA_DB_PATH` | `./chroma_db` | ChromaDB persistence directory |
| `VECTOR_SEARCH_K` | `10` | Number of results from vector retriever |
| `HYBRID_RETRIEVER_WEIGHTS` | `[0.4, 0.6]` | BM25 / vector weights |
| `CACHE_DIR` | `document_cache` | Document chunk cache directory |
| `CACHE_EXPIRE_DAYS` | `7` | Cache TTL in days |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Supported file types

`.pdf`, `.docx`, `.txt`, `.md` — up to 50 MB per file, 200 MB total.
