from typing import List, Dict

def create_engineered_features(previous_workouts: List[Dict[str, float]]) -> Dict[str, float]:
    # Function to create engineered features from previous workouts
    features = {}
    
    if not previous_workouts:
        return features
    
    # Example feature: Average weight lifted
    weights = [workout['weight'] for workout in previous_workouts if 'weight' in workout]
    features['avg_weight'] = sum(weights) / len(weights) if weights else 0.0
    
    # Example feature: Average reps completed
    reps = [workout['reps'] for workout in previous_workouts if 'reps' in workout]
    features['avg_reps'] = sum(reps) / len(reps) if reps else 0.0
    
    # Example feature: Total volume lifted
    features['total_volume'] = sum(workout['weight'] * workout['reps'] for workout in previous_workouts)
    
    return features

def calculate_trend(previous_workouts: List[Dict[str, float]]) -> Dict[str, float]:
    # Function to analyze trends in workout data
    trends = {}
    
    if not previous_workouts:
        return trends
    
    # Example trend: Weight trend slope
    weights = [workout['weight'] for workout in previous_workouts if 'weight' in workout]
    if len(weights) > 1:
        trends['weight_trend_slope'] = (weights[-1] - weights[0]) / (len(weights) - 1)
    else:
        trends['weight_trend_slope'] = 0.0
    
    return trends

def feature_scaling(features: Dict[str, float], scaling_factor: float) -> Dict[str, float]:
    # Function to scale features based on a given factor
    return {key: value * scaling_factor for key, value in features.items()}