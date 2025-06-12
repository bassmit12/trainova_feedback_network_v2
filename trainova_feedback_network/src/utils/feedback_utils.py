from typing import Dict, List, Any, Optional
import numpy as np

def calculate_feedback_adjustment(feedback_history: List[Dict[str, Any]], 
                                exercise: str, 
                                feedback_influence: float = 0.1) -> float:
    """
    Calculate adjustment factor based on previous feedback for an exercise
    
    Args:
        feedback_history: List of feedback entries
        exercise: Name of the exercise
        feedback_influence: How much feedback affects future predictions
        
    Returns:
        Adjustment factor to apply to prediction
    """
    # Get relevant feedback for this exercise
    relevant_feedback = [f for f in feedback_history if f.get('exercise') == exercise]
    
    if not relevant_feedback:
        return 0.0
    
    # Use more recent feedback with higher weight
    recency_weights = [1 / (i + 1) for i in range(len(relevant_feedback))]
    total_weight = sum(recency_weights)
    
    if total_weight <= 0:
        return 0.0
        
    # Calculate weighted average feedback score
    weighted_scores = [f.get('score', 0) * w for f, w in zip(relevant_feedback, recency_weights)]
    avg_score = sum(weighted_scores) / total_weight
    
    # Convert score to adjustment factor
    # Positive score means prediction was too low, so increase
    # Negative score means prediction was too high, so decrease
    adjustment = avg_score * feedback_influence
    
    return adjustment

def generate_feedback_message(score: float) -> str:
    """
    Generate a human-readable feedback message based on feedback score
    
    Args:
        score: Feedback score from -1 to 1
        
    Returns:
        Human-readable message about the prediction accuracy
    """
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

def update_prediction_weights(prediction_weights: Dict[str, float], score: float, feedback_influence: float) -> Dict[str, float]:
    adjustment_factor = abs(score) * feedback_influence
    
    if score < 0:
        prediction_weights["consistency"] -= adjustment_factor
    else:
        prediction_weights["progress"] += adjustment_factor
    
    total = sum(prediction_weights.values())
    for key in prediction_weights:
        prediction_weights[key] /= total
    
    return prediction_weights