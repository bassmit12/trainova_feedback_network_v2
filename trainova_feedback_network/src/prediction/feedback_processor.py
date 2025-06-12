from typing import Dict, Any, List

class FeedbackProcessor:
    def __init__(self, feedback_influence: float = 0.1):
        self.feedback_influence = feedback_influence
        self.feedback_history = []

    def provide_feedback(self, 
                         exercise: str, 
                         predicted_weight: float, 
                         actual_weight: float, 
                         success: bool,
                         reps: int = None,
                         rir: int = None) -> Dict[str, Any]:
        weight_diff = actual_weight - predicted_weight
        score = self._calculate_feedback_score(predicted_weight, actual_weight, weight_diff, success, rir)
        
        feedback_entry = {
            'exercise': exercise,
            'predicted_weight': predicted_weight,
            'actual_weight': actual_weight,
            'success': success,
            'score': score,
            'reps': reps,
            'rir': rir
        }
        self.feedback_history.append(feedback_entry)
        self._update_prediction_weights(score)
        
        return {
            'feedback_recorded': True,
            'score': round(score, 3),
            'message': self._generate_feedback_message(score)
        }

    def _calculate_feedback_score(self, predicted_weight: float, actual_weight: float, weight_diff: float, success: bool, rir: int) -> float:
        if predicted_weight > 0:
            relative_diff = weight_diff / predicted_weight
        else:
            relative_diff = 0
        
        score = max(min(relative_diff, 1.0), -1.0)
        
        if rir is not None:
            score += (rir / 10) * self.feedback_influence
        
        if not success:
            score -= 0.1
        
        return score

    def _update_prediction_weights(self, score: float):
        adjustment_factor = abs(score) * self.feedback_influence
        
        if score < 0:
            # Increase weight of consistency
            pass
        else:
            # Increase weight of progress
            pass
        
        # Normalize weights to ensure they sum to 1
        total = sum(self.prediction_weights.values())
        for key in self.prediction_weights:
            self.prediction_weights[key] /= total

    def _generate_feedback_message(self, score: float) -> str:
        if abs(score) < 0.05:
            return "The prediction was very accurate!"
        elif score > 0.15:
            return "The prediction was too low. We'll adjust future predictions upward."
        elif score > 0.05:
            return "The prediction was slightly conservative. Minor adjustments will be made."
        elif score < -0.15:
            return "The prediction was too high. We'll be more conservative next time."
        elif score < -0.05:
            return "The prediction was slightly aggressive. Minor adjustments will be made."
        else:
            return "The prediction was reasonably accurate."