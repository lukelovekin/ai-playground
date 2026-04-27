# stt_and_analyzer

Audio transcription and analysis using OpenAI's Whisper model. Includes a standalone transcription script and a Gradio app that summarises key points from the transcript using IBM WatsonX.

## Scripts

### `simple_speech2text.py`

Downloads an MP3 from a remote URL and transcribes it locally using the Whisper pipeline (`openai/whisper-tiny.en`). No API key required — runs fully locally.

### `speech2text_app.py`

A minimal Gradio app for audio transcription only — upload a file and get the raw transcript back. Uses Whisper locally.

### `speech_analyzer.py`

A Gradio app that combines transcription with summarisation:

1. Upload an audio file.
2. Whisper (`openai/whisper-tiny.en`) transcribes it locally.
3. The transcript is sent to IBM WatsonX Llama (`meta-llama/llama-3-2-11b-vision-instruct`) with a prompt to extract and list key points.
4. The summary is returned in the Gradio interface.

## Pattern

STT, Summarisation

## Tools

**Transformers** (Whisper), **Gradio**, **IBM WatsonX** (Llama), **LangChain**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install transformers torch gradio langchain ibm-watson-machine-learning ibm-watsonx-ai
```

## Run

```bash
# Transcription + summarisation app
python speech_analyzer.py

# Transcription only
python speech2text_app.py
```

Both apps start on `http://0.0.0.0:7860`.
