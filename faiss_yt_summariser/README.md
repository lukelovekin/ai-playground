# faiss_yt_summariser

A Gradio web app that takes a YouTube URL, extracts the English transcript, embeds it into a FAISS vector index, and lets you summarise the video or ask questions about it via RAG.

## How it works

### Summarisation

1. Fetch the English transcript via YouTube Transcript API (prefers manually created over auto-generated).
2. Pass the full transcript to IBM Granite with a structured summarisation prompt.
3. Return a concise single-paragraph summary.

### Q&A (RAG)

1. Chunk the transcript with LangChain's `RecursiveCharacterTextSplitter` (200 chars, 20 overlap).
2. Embed chunks using IBM WatsonX SLATE-30M embeddings.
3. Store in a FAISS index.
4. On each question, retrieve the top-7 most relevant chunks and pass them to Granite for answer generation.

**Models:**
- Generation: `ibm/granite-3-2-8b-instruct`
- Embeddings: `ibm/slate-30m-english-rtrvr-v2`

## Pattern

RAG, Summarisation

## Tools

**Gradio**, **FAISS**, **LangChain**, **IBM WatsonX** (Granite, SLATE embeddings), **YouTube Transcript API**

## Setup

```bash
python3.11 -m venv my_env
source my_env/bin/activate

pip install youtube-transcript-api==1.2.1
pip install faiss-cpu==1.8.0
pip install langchain==0.2.6 langchain-community==0.2.6
pip install ibm-watsonx-ai==1.0.10 langchain-ibm==0.1.8
pip install gradio==4.44.1
pip install huggingface_hub==0.16.4
```

## Run

```bash
python3.11 ybot.py
```

The app starts on `http://0.0.0.0:7860`. Paste a YouTube URL, then click **Summarize Video** or enter a question and click **Ask a Question**.
