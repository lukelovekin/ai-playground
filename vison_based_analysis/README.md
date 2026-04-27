# vison_based_analysis

A Gradio fashion analysis app that matches an uploaded outfit image to a Taylor Swift style dataset via cosine similarity, then generates a detailed garment breakdown using a vision LLM.

## How it works

1. The uploaded image is encoded into a vector embedding.
2. Cosine similarity is computed against a pre-built dataset of Taylor Swift outfit embeddings (`swift-style-embeddings.pkl`).
3. The closest matching outfit and related pieces are retrieved.
4. The matched metadata (brand, item description, pricing) plus the user's image are sent to a Llama vision model on IBM WatsonX.
5. The model returns a detailed analysis of garments, fabrics, colours, and styling with brand/pricing details where available.

**Model:** Llama Vision (IBM WatsonX)

## Pattern

Vision, Vector similarity search

## Tools

**Gradio**, **IBM WatsonX** (Llama Vision), **pandas**, **Pillow**

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Download the embeddings dataset:

```bash
wget -O swift-style-embeddings.pkl https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/95eJ0YJVtqTZhEd7RaUlew/processed-swift-style-with-embeddings.pkl
```

## Run

```bash
python app.py
```
