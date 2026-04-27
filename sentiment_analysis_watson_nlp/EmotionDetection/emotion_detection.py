"""
Emotion detection using the Watson NLP REST API.
"""
import requests 


def emotion_detector(text_to_analyze):
    """
    Calls the Watson NLP emotion detection API for the given text.
    Returns a dict with anger, disgust, fear, joy, sadness scores
    and the dominant_emotion key.
    Returns None values when the API responds with status code 400
    (e.g. blank or invalid input).
    """
    url = (
        'https://sn-watson-emotion.labs.skills.network'
        '/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'
    )
    headers = {
        'grpc-metadata-mm-model-id': 'emotion_aggregated-workflow_lang_en_stock'
    }
    input_json = {'raw_document': {'text': text_to_analyze}}

    response = requests.post(url, json=input_json, headers=headers, timeout=10)

    if response.status_code == 400:
        return {
            'anger': None,
            'disgust': None,
            'fear': None,
            'joy': None,
            'sadness': None,
            'dominant_emotion': None,
        }

    response_json = response.json()
    emotions = response_json['emotionPredictions'][0]['emotion']

    emotion_scores = {
        'anger': emotions['anger'],
        'disgust': emotions['disgust'],
        'fear': emotions['fear'],
        'joy': emotions['joy'],
        'sadness': emotions['sadness'],
    }
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    emotion_scores['dominant_emotion'] = dominant_emotion
    return emotion_scores
