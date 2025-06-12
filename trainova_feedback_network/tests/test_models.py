from src.models.feedback_prediction_model import FeedbackBasedPredictionModel
from src.models.lstm_model import LSTMModel
from src.prediction.predictor import Predictor
from src.prediction.feedback_processor import FeedbackProcessor
import unittest

class TestFeedbackBasedPredictionModel(unittest.TestCase):
    def setUp(self):
        self.model = FeedbackBasedPredictionModel()

    def test_provide_feedback(self):
        result = self.model.provide_feedback("Squat", 100, 110, True, reps=8, rir=2)
        self.assertTrue(result['feedback_recorded'])
        self.assertIn('score', result)
        self.assertIn('message', result)

    def test_update_prediction_weights(self):
        initial_weights = self.model.prediction_weights.copy()
        self.model._update_prediction_weights(0.1)
        self.assertNotEqual(initial_weights, self.model.prediction_weights)

class TestLSTMModel(unittest.TestCase):
    def setUp(self):
        self.model = LSTMModel()

    def test_forward_pass(self):
        import torch
        input_data = torch.randn(1, 10, 1)  # (batch_size, seq_len, input_size)
        output = self.model(input_data)
        self.assertEqual(output.shape, (1, 1))  # (batch_size, output_size)

class TestPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = Predictor()

    def test_predict(self):
        previous_workouts = [{'weight': 100, 'reps': 8}, {'weight': 105, 'reps': 6}]
        result = self.predictor.predict("Bench Press", previous_workouts)
        self.assertIn('weight', result)
        self.assertIn('confidence', result)

class TestFeedbackProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = FeedbackProcessor()

    def test_process_feedback(self):
        feedback = {'exercise': 'Deadlift', 'predicted_weight': 150, 'actual_weight': 160, 'success': True}
        self.processor.process_feedback(feedback)
        self.assertIn(feedback['exercise'], self.processor.feedback_history)

if __name__ == '__main__':
    unittest.main()