from typing import Dict, Any, List
import numpy as np
import pandas as pd
from ..utils.weight_calculation import calculate_weight_for_reps, calculate_one_rep_max
from ..utils.feedback_utils import generate_feedback_message

class FeedbackBasedPredictionModel:
    def __init__(self):
        self.feedback_history = []
        self.prediction_weights = {
            "last_weight": 0.8,  # Increased from 0.5 to give more weight to recent performance
            "avg_progress": 0.1,  # Reduced to balance the weights
            "consistency": 0.05,  # Reduced to balance the weights
            "volume": 0.05       # Reduced to balance the weights
        }
        self.feedback_influence = 0.15  # Increased from 0.1 to make feedback more impactful

    def provide_feedback(self, 
                         exercise: str, 
                         predicted_weight: float, 
                         actual_weight: float, 
                         success: bool,
                         reps: int = None,
                         rir: int = None) -> Dict[str, Any]:
        weight_diff = actual_weight - predicted_weight
        relative_diff = weight_diff / predicted_weight if predicted_weight > 0 else 0
        score = max(min(relative_diff, 1.0), -1.0)

        if rir is not None:
            score += (rir / 10) * self.feedback_influence

        if not success:
            score -= 0.1

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
        self.update_prediction_weights(score)
        return {
            'feedback_recorded': True,
            'score': round(score, 3),
            'message': generate_feedback_message(score)
        }

    def predict(self, exercise: str, previous_workouts: List[Dict[str, Any]], debug: bool = False) -> Dict[str, Any]:
        if not previous_workouts:
            return {"weight": 0, "confidence": 0, "message": "No previous workout data provided"}

        # Debug information if enabled
        if debug:
            print(f"\nDebug - Processing {len(previous_workouts)} workouts for {exercise}")
        
        # Ensure proper date parsing and sorting
        for workout in previous_workouts:
            if 'date' in workout and isinstance(workout['date'], str):
                try:
                    workout['date'] = pd.to_datetime(workout['date'])
                except Exception as e:
                    if debug:
                        print(f"Date parsing error: {e} for date: {workout['date']}")
                    # Fallback to string comparison if datetime parsing fails
        
        # Sort workouts by date if available to ensure we're using the most recent data
        if 'date' in previous_workouts[0]:
            previous_workouts = sorted(previous_workouts, key=lambda x: x['date'])
            # Debug: Show date range
            if debug and len(previous_workouts) > 1:
                print(f"Date range: {previous_workouts[0]['date']} to {previous_workouts[-1]['date']}")
                print(f"Latest workout: {previous_workouts[-1]['exercise']} - {previous_workouts[-1]['weight']}kg x {previous_workouts[-1]['reps']} reps")

        # Filter for the specific exercise
        exercise_workouts = [w for w in previous_workouts if w.get('exercise') == exercise]
        if not exercise_workouts:
            return {"weight": 0, "confidence": 0, "message": f"No data found for {exercise}"}
            
        if debug:
            print(f"Found {len(exercise_workouts)} workouts for {exercise}")
            if len(exercise_workouts) > 0:
                print(f"Latest {exercise} workout: {exercise_workouts[-1]['weight']}kg x {exercise_workouts[-1]['reps']} reps on {exercise_workouts[-1]['date']}")

        # Focus on more recent workouts for progressive exercises
        # Use last 5 workouts if available, otherwise use all
        recent_workouts = exercise_workouts[-5:] if len(exercise_workouts) > 5 else exercise_workouts

        last_workout = recent_workouts[-1]
        last_weight = float(last_workout.get('weight', 0))  # Ensure we get a float
        last_reps = int(last_workout.get('reps', 0))  # Ensure we get an integer
        
        if debug:
            print(f"Using last workout weight: {last_weight}kg and reps: {last_reps}")
        
        # Target rep range: 4-8 reps for single set
        target_reps = 6  # Mid-point of our 4-8 rep range
        
        # If the last workout had reps outside our 4-8 range, we need to adjust the weight accordingly
        estimated_1rm = 0
        if last_reps > 0:
            # Estimate 1RM from last workout - FIXED CALCULATION
            estimated_1rm = calculate_one_rep_max(last_weight, last_reps)
            if debug:
                print(f"Estimated 1RM: {estimated_1rm}kg")
            
            if last_reps != target_reps:
                # Calculate intensity for target reps (6 reps = approximately 85% of 1RM)
                target_intensity = 0.85  # 85% of 1RM is generally good for 6 reps
                
                # Adjust last weight based on target intensity
                adjusted_last_weight = estimated_1rm * target_intensity
                
                # Blend with actual last weight to avoid extreme changes
                # We'll weight the actual last weight more heavily (75%) to stay closer to reality
                last_weight_adjusted = (last_weight * 0.75 + adjusted_last_weight * 0.25)
                last_weight_adjusted = self._round_to_increment(last_weight_adjusted)
                
                if debug:
                    print(f"Adjusted last weight from {last_weight}kg to {last_weight_adjusted}kg for target rep range")
                
                # Only use the adjusted weight if it makes sense
                if last_weight_adjusted > 0 and abs(last_weight_adjusted - last_weight) / last_weight < 0.2:  # Max 20% change
                    last_weight = last_weight_adjusted

        # Calculate weights from recent workouts
        weights = [float(w.get('weight', 0)) for w in recent_workouts]
        consistency = 1.0 / (1.0 + np.std(weights)) if len(weights) > 1 else 0.5

        # Calculate volumes (weight × reps)
        volumes = [float(w.get('weight', 0)) * int(w.get('reps', 0)) for w in recent_workouts]
        avg_volume = np.mean(volumes) if volumes else 0
        volume_factor = min(avg_volume / 100, 1.0)

        # Analyze progression trend
        if len(weights) > 1:
            weight_changes = np.diff(weights)
            avg_progress = np.mean(weight_changes) if len(weight_changes) > 0 else 0
            
            # Check if the user has been progressing steadily
            is_progressing = all(change >= 0 for change in weight_changes[-min(3, len(weight_changes)):])
            
            # Make progression more aggressive by amplifying positive progress
            if avg_progress >= 0:
                # More aggressive amplification (2x instead of 1.2x)
                avg_progress *= 1.25
            else:
                # If user is regressing, maintain a small positive progression anyway
                avg_progress = 0.5  # Small positive increment instead of negative
        else:
            avg_progress = 0.5  # Default small positive increment
            is_progressing = True
            
        # Calculate rep adjustment
        rep_adjustment = self._calculate_rep_adjustment(recent_workouts, target_reps)

        # Calculate weighted prediction
        weighted_prediction = (
            self.prediction_weights["last_weight"] * last_weight +
            self.prediction_weights["avg_progress"] * (last_weight + avg_progress) +
            self.prediction_weights["consistency"] * consistency * last_weight +
            self.prediction_weights["volume"] * volume_factor * last_weight
        )

        adjusted_prediction = weighted_prediction * (1 + rep_adjustment)
        
        # Add a progressive overload factor
        progressive_overload_factor = 0.05  # Always add at least 5% for progressive overload
        adjusted_prediction *= (1 + progressive_overload_factor)
        
        # For single-set training, we can typically handle slightly higher loads
        # Add a small intensity factor for single set work
        single_set_factor = 0.025  # 2.5% higher weight for single set vs multiple sets
        adjusted_prediction *= (1 + single_set_factor)
        
        # If the user has been progressing steadily, push them further
        if is_progressing:
            push_factor = 0.025  # Extra 2.5% push when already progressing
            adjusted_prediction *= (1 + push_factor)
        
        # Round to the nearest increment (typically 2.5kg/lb)
        rounded_weight = self._round_to_increment(adjusted_prediction)
        
        # Ensure the weight is challenging:
        # 1. Never predict less than the last workout weight
        # 2. If the last weight is the same as the prediction, add an increment
        if rounded_weight <= last_weight:
            rounded_weight = self._round_to_increment(last_weight + 2.5)
            
        # Check if the user has used this weight before
        has_used_weight_before = any(float(w.get('weight', 0)) == rounded_weight for w in recent_workouts)
        
        # If this exact weight has been used before, slightly increase it to push progression
        if has_used_weight_before:
            # Find the max reps achieved at this weight
            max_reps_at_weight = max([int(w.get('reps', 0)) for w in recent_workouts 
                                   if abs(float(w.get('weight', 0)) - rounded_weight) < 0.1], default=0)
            
            # If they've done more than 6 reps at this weight, increase the weight
            if max_reps_at_weight >= 6:
                rounded_weight = self._round_to_increment(rounded_weight + 2.5)
                if debug:
                    print(f"User has already done {max_reps_at_weight} reps at {rounded_weight-2.5}kg, increasing to {rounded_weight}kg")
            # Otherwise suggest more reps at the same weight
            else:
                target_reps = max_reps_at_weight + 1
                target_reps = min(max(target_reps, 4), 8)  # Keep within 4-8 range
                if debug:
                    print(f"User has only done {max_reps_at_weight} reps at {rounded_weight}kg, suggesting {target_reps} reps")

        confidence = 0.5 + (0.3 * min(len(previous_workouts) / 10, 1.0)) + (0.1 * consistency) + (0.1 * self._calculate_rep_consistency(recent_workouts))

        # Calculate suggested reps based on the weight and previous performance
        suggested_reps = self._generate_intensity_based_reps(last_weight, last_reps, rounded_weight)
        
        # Generate a more motivational message
        message = f"Time to push your limits with {rounded_weight}kg for {suggested_reps[0]} reps!"
        
        # Include analysis information
        analysis = {
            "progression_rate": f"{avg_progress:.2f} kg per session",
            "last_weight": f"{last_weight} kg",
            "intensity": f"{round((rounded_weight / estimated_1rm if estimated_1rm > 0 else 0.85) * 100)}% of estimated 1RM",
            "recommendation": "Increase weight" if rounded_weight > last_weight else "Increase reps"
        }

        if debug:
            print(f"Final prediction: {rounded_weight}kg for {suggested_reps[0]} reps")

        return {
            "weight": rounded_weight,
            "confidence": round(min(confidence, 1.0), 2),
            "message": message,
            "suggested_reps": suggested_reps,
            "analysis": analysis
        }

    def _calculate_rep_adjustment(self, previous_workouts: List[Dict[str, Any]], target_reps: int) -> float:
        all_reps = [w.get('reps', 0) for w in previous_workouts if w.get('reps', 0) > 0]
        avg_reps = np.mean(all_reps) if all_reps else 0
        rep_diff = avg_reps - target_reps
        
        # Increased from 0.025 to 0.04 to make rep differences have more impact
        adjustment = rep_diff * 0.04
        
        # Allow slightly more adjustment range (-0.25 to 0.25 instead of -0.2 to 0.2)
        return max(min(adjustment, 0.25), -0.25)

    def _calculate_rep_consistency(self, previous_workouts: List[Dict[str, Any]]) -> float:
        reps = [w.get('reps', 0) for w in previous_workouts if w.get('reps', 0) > 0]
        if len(reps) < 2:
            return 1.0
        std_dev = np.std(reps)
        mean_reps = np.mean(reps)
        return 1.0 / (1.0 + std_dev / mean_reps) if mean_reps > 0 else 0

    def _generate_intensity_based_reps(self, previous_weight: float, previous_reps: int, predicted_weight: float) -> List[int]:
        """
        Generate rep scheme based on intensity relationship, focused on 4-8 rep range for a single set
        
        Args:
            previous_weight: Weight from previous workout
            previous_reps: Reps from previous workout
            predicted_weight: Predicted weight for next workout
            
        Returns:
            List containing a single rep count for one set
        """
        # Calculate estimated 1RM from previous workout
        estimated_1rm = calculate_one_rep_max(previous_weight, previous_reps)
        
        # Calculate intensity as percentage of 1RM
        intensity = (predicted_weight / estimated_1rm) if estimated_1rm > 0 else 0.75
        
        # Cap intensity at reasonable values to prevent unrealistic rep predictions
        # No exercise should really be performed above 95% of 1RM for reps
        intensity = min(max(intensity, 0.75), 0.95)
        
        # Modified intensity mapping to focus on 4-8 rep range
        # Each intensity now maps to multiple possible rep counts
        intensity_mapping = {
            0.92: [4],            # Very high intensity: only 4 reps
            0.90: [4, 5],         # High intensity: 4-5 reps
            0.87: [4, 5, 6],      # Moderately high intensity: 4-6 reps
            0.85: [5, 6],         # Medium-high intensity: 5-6 reps
            0.83: [5, 6, 7],      # Medium intensity: 5-7 reps
            0.80: [6, 7],         # Medium-low intensity: 6-7 reps
            0.77: [6, 7, 8],      # Low intensity: 6-8 reps
            0.75: [7, 8]          # Very low intensity: 7-8 reps
        }
        
        # Find the closest intensity level in our mapping
        closest_intensity = min(intensity_mapping.keys(), key=lambda x: abs(x - intensity))
        
        # Get possible rep options for this intensity
        rep_options = intensity_mapping[closest_intensity]
        
        # Add variation based on previous reps
        # If user did higher reps before, suggest lower reps in the range (and vice versa)
        if previous_reps >= 8:
            # User did high reps last time, suggest lower reps in the range
            suggested_reps = rep_options[0] if rep_options else 4
        elif previous_reps <= 4:
            # User did low reps last time, suggest higher reps in the range
            suggested_reps = rep_options[-1] if rep_options else 8
        else:
            # Use the middle option, or a random choice if multiple options
            middle_index = len(rep_options) // 2
            suggested_reps = rep_options[middle_index] if rep_options else 6
            
        # Add training variety based on workout history
        # Every third workout, shift the rep recommendation by 1 to provide variety
        if hasattr(self, '_workout_counter'):
            self._workout_counter += 1
        else:
            self._workout_counter = 0
            
        if self._workout_counter % 3 == 0 and len(rep_options) > 1:
            # Add variety by choosing a different rep count from the available options
            current_index = rep_options.index(suggested_reps) if suggested_reps in rep_options else 0
            new_index = (current_index + 1) % len(rep_options)
            suggested_reps = rep_options[new_index]
        
        # Ensure reps stay within the 4-8 range
        suggested_reps = max(4, min(suggested_reps, 8))
        
        # Return as a single-item list for consistency with the rest of the code
        return [suggested_reps]

    def _round_to_increment(self, weight: float, increment: float = 2.5) -> float:
        return round(weight / increment) * increment

    def update_prediction_weights(self, score: float):
        adjustment_factor = abs(score) * self.feedback_influence
        if score < 0:
            self.prediction_weights["consistency"] += adjustment_factor
            self.prediction_weights["avg_progress"] -= adjustment_factor
        else:
            self.prediction_weights["avg_progress"] += adjustment_factor
            self.prediction_weights["consistency"] -= adjustment_factor
        
        # Normalize weights
        total = sum(self.prediction_weights.values())
        if total > 0:
            for key in self.prediction_weights:
                self.prediction_weights[key] /= total