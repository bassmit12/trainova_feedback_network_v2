import unittest
from src.utils.weight_calculation import calculate_weight_for_reps
from src.utils.rep_utils import generate_suggested_reps
from src.utils.feedback_utils import generate_feedback_message, update_prediction_weights

class TestUtils(unittest.TestCase):

    def test_calculate_weight_for_reps(self):
        one_rep_max = 100
        target_reps = 5
        expected_weight = 87.5  # Example expected value based on the formula
        calculated_weight = calculate_weight_for_reps(one_rep_max, target_reps, formula='brzycki')
        self.assertAlmostEqual(calculated_weight, expected_weight, places=2)

    def test_generate_suggested_reps(self):
        base_reps = 10
        expected_reps = [10, 9, 8]
        suggested_reps = generate_suggested_reps(base_reps)
        self.assertEqual(suggested_reps, expected_reps)

    def test_generate_feedback_message(self):
        score = 0.1
        expected_message = "The prediction was slightly conservative. Minor adjustments will be made."
        message = generate_feedback_message(score)
        self.assertEqual(message, expected_message)

    def test_update_prediction_weights(self):
        prediction_weights = {"consistency": 0.5, "progress": 0.5}
        score = -0.2
        updated_weights = update_prediction_weights(prediction_weights, score)
        self.assertGreater(updated_weights["consistency"], 0.5)
        self.assertLess(updated_weights["progress"], 0.5)

if __name__ == '__main__':
    unittest.main()