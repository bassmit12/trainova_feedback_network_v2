from flask import Flask, request, jsonify
import os
import sys
import json
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..models.feedback_prediction_model import FeedbackBasedPredictionModel

app = Flask(__name__)

# Initialize the model
prediction_model = FeedbackBasedPredictionModel()

@app.route('/')
def home():
    """Welcome endpoint for the API"""
    return jsonify({
        "message": "Welcome to the Trainova Feedback Network API",
        "version": "2.0",
        "endpoints": {
            "/predict": "POST - Get weight prediction based on workout history",
            "/feedback": "POST - Provide feedback on a prediction",
            "/health": "GET - Check API health status"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/predict', methods=['POST'])
def predict_weight():
    """
    Predict the weight for the next workout based on previous workout data.
    
    Expected JSON payload:
    {
        "exercise": "string",
        "previous_workouts": [
            {
                "exercise": "string", 
                "weight": float,
                "reps": int,
                "date": "YYYY-MM-DD" (optional),
                "success": bool (optional),
                "rir": int (optional)
            }
        ],
        "debug": bool (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        exercise = data.get('exercise')
        previous_workouts = data.get('previous_workouts', [])
        debug = data.get('debug', False)
        
        if not exercise:
            return jsonify({"error": "Exercise name is required"}), 400
            
        if not previous_workouts:
            return jsonify({"error": "No previous workout data provided"}), 400
        
        # Make prediction
        prediction = prediction_model.predict(exercise, previous_workouts, debug)
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def provide_feedback():
    """
    Provide feedback on a prediction to improve future predictions.
    
    Expected JSON payload:
    {
        "exercise": "string",
        "predicted_weight": float,
        "actual_weight": float,
        "success": bool (optional),
        "reps": int (optional),
        "rir": int (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        exercise = data.get('exercise')
        predicted_weight = data.get('predicted_weight')
        actual_weight = data.get('actual_weight')
        success = data.get('success', True)
        reps = data.get('reps')
        rir = data.get('rir')
        
        if not all([exercise, predicted_weight is not None, actual_weight is not None]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Provide feedback
        feedback_result = prediction_model.provide_feedback(
            exercise=exercise,
            predicted_weight=predicted_weight,
            actual_weight=actual_weight,
            success=success,
            reps=reps,
            rir=rir
        )
        
        return jsonify(feedback_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This conditional is used when running this file directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)