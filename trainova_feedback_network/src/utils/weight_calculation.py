import numpy as np
from typing import List, Dict, Any

def calculate_one_rep_max(weight: float, reps: int, formula: str = 'brzycki') -> float:
    """
    Calculate estimated one-rep max based on weight and reps performed
    
    Args:
        weight: Weight used in the set
        reps: Number of reps performed
        formula: Which formula to use ('epley', 'brzycki', etc.)
        
    Returns:
        Estimated 1RM
    """
    if reps <= 0 or weight <= 0:
        return 0
        
    if formula.lower() == 'epley':
        # Epley formula: 1RM = w * (1 + r/30)
        return weight * (1 + reps / 30)
    elif formula.lower() == 'brzycki':
        # Brzycki formula: 1RM = w * 36 / (37 - r)
        return weight * 36 / (37 - reps) if reps < 37 else weight * 1.8
    else:
        # Default to Brzycki
        return weight * 36 / (37 - reps) if reps < 37 else weight * 1.8

def calculate_weight_for_reps(one_rep_max: float, target_reps: int, formula: str = 'brzycki') -> float:
    """
    Calculate the appropriate weight to use for a specific rep target
    
    Args:
        one_rep_max: Estimated 1RM
        target_reps: Desired number of reps
        formula: Which formula to use ('epley', 'brzycki', etc.)
        
    Returns:
        Appropriate weight for the target rep count
    """
    if target_reps <= 1:
        return one_rep_max
        
    if formula.lower() == 'epley':
        # Rearranged Epley formula: w = 1RM / (1 + r/30)
        return one_rep_max / (1 + target_reps/30)
    elif formula.lower() == 'brzycki':
        # Rearranged Brzycki formula: w = 1RM × (37 - r) / 36
        return one_rep_max * (37 - target_reps) / 36
    else:
        # Default to Brzycki
        return one_rep_max * (37 - target_reps) / 36
    
def round_to_increment(weight: float, increment: float = 2.5) -> float:
    """
    Round a weight to the nearest increment (usually 2.5kg/5lb)
    
    Args:
        weight: Weight to round
        increment: Increment to round to (default 2.5)
        
    Returns:
        Rounded weight
    """
    return round(weight / increment) * increment