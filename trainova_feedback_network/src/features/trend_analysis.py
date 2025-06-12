from typing import List, Dict

def analyze_trend(previous_workouts: List[Dict[str, float]]) -> Dict[str, float]:
    if not previous_workouts:
        return {"trend": "no_data", "average_weight": 0.0}

    weights = [workout['weight'] for workout in previous_workouts if 'weight' in workout]
    if len(weights) < 2:
        return {"trend": "insufficient_data", "average_weight": sum(weights) / len(weights)}

    weight_changes = [weights[i] - weights[i - 1] for i in range(1, len(weights))]
    average_change = sum(weight_changes) / len(weight_changes)

    trend = "increasing" if average_change > 0 else "decreasing" if average_change < 0 else "stable"
    average_weight = sum(weights) / len(weights)

    return {
        "trend": trend,
        "average_weight": average_weight
    }

def calculate_weight_trend(previous_workouts: List[Dict[str, float]]) -> float:
    if not previous_workouts:
        return 0.0

    weights = [workout['weight'] for workout in previous_workouts if 'weight' in workout]
    if len(weights) < 2:
        return 0.0

    weight_changes = [weights[i] - weights[i - 1] for i in range(1, len(weights))]
    return sum(weight_changes) / len(weight_changes)