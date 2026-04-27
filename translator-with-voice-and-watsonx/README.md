# translator-with-voice-and-watsonx

A voice-enabled Flask translation app powered by IBM WatsonX. Audio in, translated speech out — fully pipeline-based with no frontend state.

## How it works

```
User audio → IBM Watson STT → Watsonx LLM (Mistral) → IBM Watson TTS → base64 WAV
```

1. `POST /speech-to-text` — receives raw audio bytes, returns a JSON transcript.
2. `POST /process-message` — receives the transcript and preferred voice, calls the WatsonX LLM for a response, synthesises it to speech, and returns both the text and a base64-encoded WAV.

**Model:** Mistral Medium 2505 (IBM WatsonX)

## Pattern

STT → LLM → TTS pipeline

## Tools

**Flask**, **IBM WatsonX** (Mistral), **IBM Watson** (STT, TTS)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python server.py
```

The server starts on `http://0.0.0.0:8000`.

### Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/speech-to-text` | Transcribe raw audio bytes → JSON `{text}` |
| `POST` | `/process-message` | `{userMessage, voice}` → `{watsonxResponseText, watsonxResponseSpeech}` |

## Docker

```bash
docker build -t translator-watsonx .
docker run -p 8000:8000 translator-watsonx
```
