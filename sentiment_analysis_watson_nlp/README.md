# sentiment_analysis

A Flask web app that performs emotion detection on user-submitted text using the IBM Watson NLP REST API.

## How it works

The `/emotionDetector` route receives text, calls the IBM Watson NLP emotion detection endpoint, and returns scores for five emotions plus the dominant emotion. Handles blank or invalid input with appropriate error messages.

### Response format

```
'anger': 0.12, 'disgust': 0.05, 'fear': 0.03, 'joy': 0.78, 'sadness': 0.02.
The dominant emotion is joy.
```

### Emotions detected

- anger
- disgust
- fear
- joy
- sadness

## Pattern

NLP, Emotion detection

## Tools

**Flask**, **IBM Watson NLP API**

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install flask
```

## Run

```bash
python server.py
```

The app starts on `http://0.0.0.0:5000`.

## Tests

```bash
python test_emotion_detection.py
```
