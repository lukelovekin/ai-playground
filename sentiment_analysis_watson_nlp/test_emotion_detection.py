"""
Unit tests for the EmotionDetection package.
"""
import unittest
from EmotionDetection.emotion_detection import emotion_detector


class TestEmotionDetector(unittest.TestCase):
    """Tests for emotion_detector function."""

    def test_joy_dominant(self):
        """Joy should be the dominant emotion for a positive statement."""
        result = emotion_detector("I am glad this happened")
        self.assertEqual(result['dominant_emotion'], 'joy')

    def test_anger_dominant(self):
        """Anger should be the dominant emotion for an angry statement."""
        result = emotion_detector("I am really mad about this")
        self.assertEqual(result['dominant_emotion'], 'anger')

    def test_disgust_dominant(self):
        """Disgust should be the dominant emotion for a disgusting statement."""
        result = emotion_detector("I feel disgusted just hearing about this")
        self.assertEqual(result['dominant_emotion'], 'disgust')

    def test_sadness_dominant(self):
        """Sadness should be the dominant emotion for a sad statement."""
        result = emotion_detector("I am so sad about this")
        self.assertEqual(result['dominant_emotion'], 'sadness')

    def test_fear_dominant(self):
        """Fear should be the dominant emotion for a fearful statement."""
        result = emotion_detector("I am really afraid that this will happen")
        self.assertEqual(result['dominant_emotion'], 'fear')

    def test_blank_input_returns_none(self):
        """Blank input should return None for all fields including dominant_emotion."""
        result = emotion_detector("")
        self.assertIsNone(result['dominant_emotion'])


if __name__ == '__main__':
    unittest.main()
