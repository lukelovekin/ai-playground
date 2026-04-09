"""
Executing this function initiates the emotion detection application
over the Flask channel and deploys it on localhost:5000.
"""
from flask import Flask, render_template, request  # pylint: disable=import-error
from EmotionDetection.emotion_detection import emotion_detector

app = Flask(__name__)


@app.route("/emotionDetector")
def emotion_detector_route():
    """
    Receives text from the HTML interface and runs emotion detection
    using emotion_detector(). Returns emotion scores and the dominant
    emotion for the provided text.
    """
    text_to_analyze = request.args.get('textToAnalyze')

    result = emotion_detector(text_to_analyze)

    if result['dominant_emotion'] is None:
        return "Invalid text! Please try again."

    anger = result['anger']
    disgust = result['disgust']
    fear = result['fear']
    joy = result['joy']
    sadness = result['sadness']
    dominant = result['dominant_emotion']

    return (
        f"For the given statement, the system response is "
        f"'anger': {anger}, 'disgust': {disgust}, 'fear': {fear}, "
        f"'joy': {joy} and 'sadness': {sadness}. "
        f"The dominant emotion is {dominant}."
    )


@app.route("/")
def render_index_page():
    """
    Initiates the rendering of the main application page over the Flask channel.
    """
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
