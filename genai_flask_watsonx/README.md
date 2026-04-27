# genai_flask_app

A Flask web app with a chat interface that lets users send a message and select which IBM WatsonX model responds. Each model uses a model-specific prompt template and returns a structured JSON response.

## How it works

The `/generate` endpoint accepts a user message and a model selection (`llama`, `granite`, or `mistral`). The selected model is called via LangChain with a model-specific prompt template, and the output is parsed into a structured JSON object via Pydantic.

### Response format

```json
{
  "summary": "Brief summary of the user's message",
  "sentiment": 75,
  "response": "Suggested reply to the user",
  "duration": 1.23
}
```

`sentiment` is an integer from 0 (negative) to 100 (positive).

### Models

| Selection | Model ID |
|---|---|
| `llama` | `meta-llama/llama-3-2-11b-vision-instruct` |
| `granite` | `ibm/granite-3-3-8b-instruct` |
| `mistral` | `mistralai/mistral-small-3-1-24b-instruct-2503` |

All models run on IBM WatsonX (greedy decoding, 256 max tokens).

## Pattern

Prompt engineering, Structured output

## Tools

**Flask**, **LangChain**, **IBM WatsonX** (Llama, Granite, Mistral)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install flask langchain langchain-ibm ibm-watsonx-ai pydantic
```

## Run

```bash
python app.py
```

The app starts on `http://127.0.0.1:5000`.
