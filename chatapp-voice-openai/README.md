# chatapp-voice-openai

A voice-enabled Flask chat app. User audio is transcribed via IBM Watson STT, processed by OpenAI GPT, and the response is synthesised back to speech via IBM Watson TTS — returned as text and a base64-encoded WAV for browser playback.

## How it works

```
User audio → IBM Watson STT → OpenAI GPT → IBM Watson TTS → base64 WAV
```

The assistant is configured as a personal assistant: answering questions, translating, summarising news, and giving recommendations — with responses capped at 2–3 sentences.

**Model:** OpenAI GPT-5-nano

## Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Serves the chat UI (`index.html`) |
| `POST` | `/speech-to-text` | Raw audio bytes → JSON `{text}` |
| `POST` | `/process-message` | `{userMessage, voice}` → `{openaiResponseText, openaiResponseSpeech}` |

## Pattern

STT → LLM → TTS pipeline

## Tools

**Flask**, **OpenAI** (GPT-5-nano), **IBM Watson** (STT, TTS)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

## Run

```bash
python server.py
```

The server starts on `http://0.0.0.0:8000`.

## Docker

```bash
docker build -t chatapp-voice-openai .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key chatapp-voice-openai
```
