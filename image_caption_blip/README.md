# image_caption

Automatic image captioning using Salesforce's BLIP model. Runs fully locally — no API key required.

## How it works

The Salesforce BLIP (`blip-image-captioning-base`) model is loaded from HuggingFace Transformers. An uploaded image is converted to RGB, processed by the BLIP processor, and the model generates a descriptive caption (up to 50 tokens).

## Pattern

Vision, Image captioning

## Tools

**Transformers** (Salesforce BLIP), **Gradio**, **Pillow**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install transformers torch gradio Pillow
```

## Run

```bash
# Gradio web interface
python image_captioning_app.py
```

Upload an image in the browser — the caption appears instantly. Also includes:
- `image_cap.py` — standalone script for single image captioning
- `automate_url_captioner.py` — batch captions images from URLs
