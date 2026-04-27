# bee_ai_demo_multi_agent_travel_planner

A multi-agent travel planning system built with the [BeeAI Framework](https://github.com/i-am-bee/bee-agent-framework). Four specialised agents collaborate via handoff tools to produce comprehensive travel recommendations covering destinations, weather, and cultural guidance.

## How it works

A **Travel Coordinator** acts as the main interface. When given a travel query it thinks through what information is needed, then delegates to the appropriate specialist via `HandoffTool`. Results are synthesised into a single cohesive plan.

```
User query
    │
    ▼
┌─────────────────────┐
│  Travel Coordinator  │
│  (main interface)    │
└──────────┬──────────┘
           │ HandoffTool
     ┌─────┼─────────────────┐
     ▼     ▼                 ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ Destination │  │ Travel           │  │ Language & Cultural  │
│ Research    │  │ Meteorologist    │  │ Expert               │
│             │  │                  │  │                      │
│ Wikipedia   │  │ OpenMeteo        │  │ Wikipedia            │
│ ThinkTool   │  │ ThinkTool        │  │ ThinkTool            │
└─────────────┘  └──────────────────┘  └──────────────────────┘
```

### Agents

| Agent | Tools | Role |
|---|---|---|
| Travel Coordinator | `HandoffTool` × 3, `ThinkTool` | Understands the query, delegates to specialists, synthesises the final plan |
| Destination Research Expert | `WikipediaTool`, `ThinkTool` | Landmarks, transport, safety, best time to visit |
| Travel Meteorologist | `OpenMeteoTool`, `ThinkTool` | Weather forecasts, climate patterns, packing advice |
| Language & Cultural Expert | `WikipediaTool`, `ThinkTool` | Essential phrases, cultural etiquette, customs, social norms |

### Requirements-based execution

Each agent uses `ConditionalRequirement` to enforce tool-use order and invocation limits — for example, `ThinkTool` is always forced at step 1 before any search tool fires. The coordinator uses `AskPermissionRequirement` to gate handoffs, ensuring deliberate delegation rather than blind forwarding.

**Model:** `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` (IBM WatsonX, temperature 0)

## Pattern

Multi-agent orchestration, Requirements-based execution control

## Tools

**BeeAI Framework**, **IBM WatsonX** (Llama 4 Maverick), **Wikipedia API**, **Open-Meteo API**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install beeai-framework
```

WatsonX credentials are picked up from your environment. Ensure `WATSONX_APIKEY` and `WATSONX_PROJECT_ID` are set.

## Run

```bash
python main.py
```
