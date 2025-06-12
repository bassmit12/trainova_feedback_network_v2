class BaseModel:
    """
    Base class for all models in the feedback prediction system.
    Provides shared functionality and properties for derived models.
    """
    
    def __init__(self):
        self.feedback_history = []
        self.prediction_weights = {
            "last_weight": 0.0,
            "avg_progress": 0.0,
            "consistency": 0.0,
            "volume": 0.0
        }
        self.feedback_influence = 0.5  # Default influence of feedback on predictions

    def save(self):
        """
        Save the model state to a file or database.
        This method should be implemented in derived classes.
        """
        raise NotImplementedError("Save method must be implemented in derived classes.")

    def load(self):
        """
        Load the model state from a file or database.
        This method should be implemented in derived classes.
        """
        raise NotImplementedError("Load method must be implemented in derived classes.")

    def _round_to_increment(self, weight: float, increment: float = 2.5) -> float:
        """
        Round the weight to the nearest increment (usually 2.5kg/5lb).
        
        Args:
            weight: Weight to round.
            increment: Increment to round to.
            
        Returns:
            Rounded weight.
        """
        return round(weight / increment) * increment