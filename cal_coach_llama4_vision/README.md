# cal_coach_app

A Flask web app that acts as an AI nutrition coach. Upload a food image and get a detailed nutritional breakdown powered by Llama 4 Maverick's vision capabilities.

## How it works

The user uploads a food image (optionally with a query). The image is base64-encoded and sent alongside a structured nutritionist system prompt to the WatsonX vision model. The model returns a formatted breakdown covering:

1. Food identification (each item listed)
2. Portion size and calorie estimate per item
3. Total calorie count
4. Macro/micronutrient breakdown (protein, carbs, fats, vitamins, minerals)
5. Health evaluation paragraph
6. Nutritional disclaimer

The raw response is parsed from Markdown to HTML and rendered in the browser.

**Model:** `meta-llama/llama-4-maverick-17b-128e-instruct-fp8` (IBM WatsonX)

## Pattern

Vision, Prompt engineering

## Tools

**Flask**, **IBM WatsonX** (Llama 4 Maverick), **Pillow**

## Setup

```bash
python3.11 -m venv my_env
source my_env/bin/activate
pip install ibm-watsonx-ai flask Pillow requests
```

## Run

```bash
python app.py
```

The app starts on `http://127.0.0.1:5000`. Upload a food photo via the form and hit submit.
