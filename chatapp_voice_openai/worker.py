import requests
from openai import OpenAI

openai_client = OpenAI()


def speech_to_text(audio_binary):
    base_url = "https://sn-watson-stt.labs.skills.network"
    api_url = base_url + '/speech-to-text/api/v1/recognize'
    params = {'model': 'en-US_Multimedia'}

    response = requests.post(api_url, params=params, data=audio_binary).json()

    if response.get('results'):
        print('speech to text response:', response)
        text = response['results'].pop()['alternatives'].pop()['transcript']
        print('recognised text:', text)
        return text

    return None


def text_to_speech(text, voice=""):
    base_url = "https://sn-watson-tts.labs.skills.network"
    api_url = base_url + '/text-to-speech/api/v1/synthesize?output=output_text.wav'

    if voice not in ("", "default"):
        api_url += "&voice=" + voice

    headers = {
        'Accept': 'audio/wav',
        'Content-Type': 'application/json',
    }

    response = requests.post(api_url, headers=headers, json={'text': text})
    print('text to speech response:', response)
    return response.content


def openai_process_message(user_message):
    prompt = (
        "Act like a personal assistant. You can respond to questions, translate sentences, "
        "summarize news, and give recommendations. Keep responses concise - 2 to 3 sentences maximum."
    )
    openai_response = openai_client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message},
        ],
        max_completion_tokens=1000,
    )
    print("openai response:", openai_response)
    return openai_response.choices[0].message.content
