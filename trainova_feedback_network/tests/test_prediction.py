from src.models.feedback_prediction_model import FeedbackBasedPredictionModel
from src.prediction.predictor import Predictor
from src.prediction.feedback_processor import FeedbackProcessor
import unittest

class TestFeedbackBasedPredictionModel(unittest.TestCase):

    def setUp(self):
        self.model = FeedbackBasedPredictionModel()
        self.exercise = "Squat"
        self.predicted_weight = 100.0
        self.actual_weight = 95.0
        self.success = True
        self.reps = 5
        self.rir = 2

    def test_provide_feedback(self):
        feedback = self.model.provide_feedback(
            exercise=self.exercise,
            predicted_weight=self.predicted_weight,
            actual_weight=self.actual_weight,
            success=self.success,
            reps=self.reps,
            rir=self.rir
        )
        self.assertIn('feedback_recorded', feedback)
        self.assertTrue(feedback['feedback_recorded'])
        self.assertIn('score', feedback)
        self.assertIn('message', feedback)

    def test_update_prediction_weights(self):
        initial_weights = self.model.prediction_weights.copy()
        score = 0.1
        self.model._update_prediction_weights(score)
        self.assertNotEqual(initial_weights, self.model.prediction_weights)

class TestPredictor(unittest.TestCase):

    def setUp(self):
        self.predictor = Predictor()
        self.previous_workouts = [
            {'weight': 100, 'reps': 5},
            {'weight': 105, 'reps': 5},
            {'weight': 110, 'reps': 4}
        ]

    def test_predict(self):
        response = self.predictor.predict("Squat", self.previous_workouts)
        self.assertIn('weight', response)
        self.assertIn('confidence', response)
        self.assertIn('message', response)
        self.assertIn('suggested_reps', response)

class TestFeedbackProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = FeedbackProcessor()
        self.exercise = "Bench Press"
        self.predicted_weight = 80.0
        self.actual_weight = 85.0
        self.success = False

    def test_process_feedback(self):
        feedback = self.processor.process_feedback(
            exercise=self.exercise,
            predicted_weight=self.predicted_weight,
            actual_weight=self.actual_weight,
            success=self.success
        )
        self.assertIn('feedback_recorded', feedback)
        self.assertTrue(feedback['feedback_recorded'])

if __name__ == '__main__':
    unittest.main()