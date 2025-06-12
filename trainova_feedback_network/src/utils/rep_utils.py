from typing import List, Dict, Any
import numpy as np
from .weight_calculation import calculate_one_rep_max

def generate_suggested_reps(base_reps: int) -> List[int]:
    """
    Generate suggested reps for a workout based on base rep count
    
    Args:
        base_reps: Base rep count to build suggestions from
        
    Returns:
        List of suggested rep counts for each set
    """
    # Default to 3 sets with a descending pattern
    return [base_reps, max(base_reps - 1, 1), max(base_reps - 2, 1)]

def generate_intensity_based_reps(previous_weight: float, previous_reps: int, predicted_weight: float) -> List[int]:
    """
    Generate rep scheme based on intensity relationship 
    
    Args:
        previous_weight: Weight from previous workout
        previous_reps: Reps from previous workout
        predicted_weight: Predicted weight for next workout
        
    Returns:
        List of suggested rep counts for sets
    """
    # Calculate estimated 1RM based on previous performance
    estimated_1rm = calculate_one_rep_max(previous_weight, previous_reps, formula='brzycki')
    
    # Calculate intensity percentage of the predicted weight relative to 1RM
    intensity = (predicted_weight / estimated_1rm) if estimated_1rm > 0 else 0.75
    
    # Map intensity to appropriate rep ranges
    # Standard intensity-rep mapping based on strength training principles
    intensity_mapping = {
        1.00: 1,    # 100% 1RM = 1 rep
        0.95: 2,    # 95% 1RM = 2 reps
        0.93: 3,    # 93% 1RM = 3 reps
        0.90: 4,    # 90% 1RM = 4 reps
        0.87: 5,    # 87% 1RM = 5 reps
        0.85: 6,    # 85% 1RM = 6 reps
        0.83: 7,    # 83% 1RM = 7 reps
        0.80: 8,    # 80% 1RM = 8 reps
        0.77: 9,    # 77% 1RM = 9 reps
        0.75: 10,   # 75% 1RM = 10 reps
        0.73: 11,   # 73% 1RM = 11 reps
        0.70: 12,   # 70% 1RM = 12 reps
        0.65: 15,   # 65% 1RM = 15 reps
        0.60: 20,   # 60% 1RM = 20 reps
    }
    
    # Find the closest intensity level in our mapping
    closest_intensity = min(intensity_mapping.keys(), key=lambda x: abs(x - intensity))
    suggested_base_reps = intensity_mapping[closest_intensity]
    
    # Create a rep scheme based on the base rep count
    # For intermediate and advanced lifters, a slight rep drop is common across sets
    if suggested_base_reps <= 5:
        # For low-rep/high-intensity work, keep reps consistent to maintain intensity
        return [suggested_base_reps] * 3
    elif suggested_base_reps <= 8:
        # For moderate rep ranges, use a slight drop-off
        return [suggested_base_reps, suggested_base_reps - 1, suggested_base_reps - 1]
    else:
        # For higher rep ranges, use a more pronounced drop-off
        return [suggested_base_reps, suggested_base_reps - 2, suggested_base_reps - 3]