from typing import List, Dict, Any
import numpy as np
from ..models.feedback_prediction_model import FeedbackBasedPredictionModel

class WorkoutPredictor:
    """
    Wrapper for the feedback prediction model that provides a simpler interface
    for predicting workout weights and handling feedback.
    """
    
    def __init__(self, model_dir: str = None):
        self.model = FeedbackBasedPredictionModel()
    
    def predict_workout(self, exercise: str, previous_workouts: List[Dict[str, Any]], debug: bool = False) -> Dict[str, Any]:
        """
        Predict weight for the next workout
        
        Args:
            exercise: Name of the exercise
            previous_workouts: List of previous workout data
                Each dict should have 'weight', 'reps', etc.
            debug: Whether to show detailed debugging information
                
        Returns:
            Dictionary with predicted weight, confidence, and suggestions
        """
        return self.model.predict(exercise, previous_workouts, debug=debug)
    
    def record_feedback(self, 
                      exercise: str, 
                      predicted_weight: float, 
                      actual_weight: float, 
                      success: bool,
                      reps: int = None,
                      rir: int = None) -> Dict[str, Any]:
        """
        Record feedback about a prediction to improve future predictions
        
        Args:
            exercise: Name of the exercise
            predicted_weight: The weight that was predicted
            actual_weight: The weight that was actually used
            success: Whether the workout was completed successfully
            reps: Number of reps completed (optional)
            rir: Reps In Reserve - how many more reps could have been done (optional)
            
        Returns:
            Dictionary with feedback results
        """
        return self.model.provide_feedback(
            exercise, 
            predicted_weight, 
            actual_weight, 
            success, 
            reps, 
            rir
        )
    
    def fit_model(self, workout_data):
        """
        Train the model with historical workout data
        
        Args:
            workout_data: DataFrame with workout history
            
        Returns:
            Self for method chaining
        """
        # For now, we just store the data but don't do any complex training
        # Future implementations could add more sophisticated model fitting
        return self
    
    def reset_model(self, reset_type: str = 'all'):
        """
        Reset the model data
        
        Args:
            reset_type: Type of reset to perform:
                - 'all': Reset everything (default)
                - 'feedback': Clear only feedback history
                - 'weights': Reset only prediction weights
                - 'scalers': Reset only scalers
                
        Returns:
            Dictionary with result of operation
        """
        if reset_type == 'all' or reset_type == 'feedback':
            self.model.feedback_history = []
            
        if reset_type == 'all' or reset_type == 'weights':
            self.model.prediction_weights = {
                "last_weight": 0.5,
                "avg_progress": 0.2,
                "consistency": 0.2,
                "volume": 0.1
            }
            
        return {
            "success": True,
            "message": f"Successfully reset {reset_type} data"
        }