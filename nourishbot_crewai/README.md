# nourishbot

A CrewAI-powered nutrition assistant that analyses food images to detect ingredients, apply dietary filters, estimate calories, and suggest recipes. Built with a Gradio interface and IBM WatsonX vision and language models.

## How it works

Two distinct CrewAI workflows share a common base crew of agents, selected at runtime based on the chosen mode:

```
                       ┌─────────────┐
                       │    image    │
                       └──────┬──────┘
                              │
                 ┌────────────┴─────────────┐
              recipe                     analysis
                 │                           │
                 ▼                           ▼
  ┌──────────────────────────┐   ┌───────────────────────────┐
  │   Ingredient Detection   │   │     Nutrient Analysis     │
  │  ExtractIngredientsTool  │   │   NutrientAnalysisTool    │
  │  FilterIngredientsTool   │   │  (Llama 3.2 90B Vision)   │
  │  (Llama 3.2 90B Vision)  │   └─────────────┬─────────────┘
  └─────────────┬────────────┘                 │
                │                              ▼
                ▼                       ┌──────────────┐
  ┌──────────────────────────┐          │    output    │
  │     Dietary Filtering    │          └──────────────┘
  │     DietaryFilterTool    │
  │       (Granite 3 8B)     │
  └─────────────┬────────────┘
                │
                ▼
  ┌──────────────────────────┐
  │     Recipe Suggestion    │
  │   (Llama 3.2 90B Vision) │
  └─────────────┬────────────┘
                │
                ▼
         ┌──────────────┐
         │    output    │
         └──────────────┘
```

### Agents & tools

| Agent | Tool | Model |
|---|---|---|
| Ingredient Detection | `ExtractIngredientsTool` — base64-encodes image, calls vision LLM | Llama 3.2 90B Vision |
| Dietary Filtering | `DietaryFilterTool` — LLM filters ingredients against restriction | Granite 3 8B |
| Nutrient Analysis | `NutrientAnalysisTool` — full nutrient breakdown from image | Llama 3.2 90B Vision |
| Recipe Suggestion | (no tool — pure LLM generation from filtered ingredient list) | Llama 3.2 90B Vision |

Agent and task configs are declared in `src/config/agents.yaml` and `src/config/tasks.yaml`. Pydantic models in `src/models.py` enforce structured JSON output for recipe and nutrient analysis responses.

## Pattern

Multi-agent orchestration, Vision

## Tools

**CrewAI**, **Gradio**, **IBM WatsonX** (Llama 3.2 90B Vision, Granite 3 8B), **Pydantic**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
WATSONX_API_KEY=your_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_project_id
```

## Run

```bash
# Gradio UI
python app.py

# CLI
python src/main.py <image_path> <dietary_restrictions> recipe
python src/main.py <image_path> analysis
```

The Gradio app starts at `http://127.0.0.1:5000`.

## Project structure

```
nourishbot_crewai/
├── app.py                      # Gradio UI
├── src/
│   ├── crew.py                 # CrewAI crew definitions (recipe + analysis)
│   ├── tools.py                # LangChain tools for extraction, filtering, analysis
│   ├── models.py               # Pydantic output schemas
│   ├── main.py                 # CLI entry point
│   └── config/
│       ├── agents.yaml         # Agent role/goal/backstory config
│       └── tasks.yaml          # Task descriptions and expected outputs
└── requirements.txt
```
