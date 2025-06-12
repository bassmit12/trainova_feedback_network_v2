#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..prediction.predictor import WorkoutPredictor
from .data_collection import DataCollector

class CommandHandler:
    """
    Handles the execution of CLI commands for the Trainova feedback network.
    """
    
    def __init__(self):
        """Initialize the command handler with data collector and predictor."""
        self.data_collector = DataCollector()
        self.predictor = WorkoutPredictor()
    
    def handle_pretrain(self, args: argparse.Namespace) -> None:
        """
        Handle the pretrain command to pretrain the model with existing data.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Pretraining Model ===")
        
        # If generating mock data was requested
        if args.generate_mock:
            print(f"Generating {args.samples} mock workout records...")
            exercises = args.exercises.split(',') if args.exercises else None
            self.data_collector.generate_and_save_mock_data(
                num_samples=args.samples,
                exercises=exercises
            )
        
        # If importing from a CSV file was requested
        if args.import_file:
            if not os.path.exists(args.import_file):
                print(f"Error: File not found: {args.import_file}")
                return
                
            print(f"Importing data from {args.import_file}...")
            self.data_collector.import_from_csv(args.import_file, is_pretraining=True)
        
        # Load the training data
        print("Loading training data...")
        training_data = self.data_collector.load_training_data(include_pretraining=True)
        
        if training_data.empty:
            print("No training data available. Please generate mock data or import a CSV file first.")
            return
        
        # Train the model
        print(f"Pretraining model with {len(training_data)} workout records...")
        self.predictor.fit_model(training_data)
        
        print("Model pretraining complete!")
    
    def handle_collect(self, args: argparse.Namespace) -> None:
        """
        Handle the collect command to gather workout data interactively.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Collecting Workout Data ===")
        
        # Interactive data collection
        workout_data = self.data_collector.interactive_data_entry(args.exercise)
        
        # Save the data
        self.data_collector.save_workout_data(workout_data, is_pretraining=args.pretraining)
        
        # Ask if the user wants to add more data
        while input("\nAdd another workout? (y/n): ").lower().startswith('y'):
            workout_data = self.data_collector.interactive_data_entry(args.exercise)
            self.data_collector.save_workout_data(workout_data, is_pretraining=args.pretraining)
    
    def handle_interactive_training(self, args: argparse.Namespace) -> None:
        """
        Handle the interactive training command to train the model with user feedback.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Interactive Training ===")
        
        # Check if there's any data to work with
        training_data = self.data_collector.load_training_data(include_pretraining=True)
        
        if training_data.empty:
            print("No training data available. Please collect some data first.")
            return
        
        # Fit the model if not already trained
        print("Ensuring model is trained with existing data...")
        self.predictor.fit_model(training_data)
        
        # Exercise selection for prediction
        if args.exercise:
            exercise = args.exercise
        else:
            # List available exercises from the data
            available_exercises = training_data['exercise'].unique()
            print("\nAvailable exercises:")
            for i, ex in enumerate(available_exercises, 1):
                print(f"{i}. {ex}")
            
            # Let user select an exercise
            selection = input("\nSelect an exercise (number or name): ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(available_exercises):
                exercise = available_exercises[int(selection) - 1]
            elif selection in available_exercises:
                exercise = selection
            else:
                print("Invalid selection. Please enter a new exercise name:")
                exercise = input().strip()
        
        # Get previous workouts for this exercise
        exercise_data = training_data[training_data['exercise'] == exercise]
        
        if len(exercise_data) == 0:
            print(f"No previous data for {exercise}. Starting with a new exercise.")
            previous_workouts = []
        else:
            # Convert DataFrame rows to dictionaries
            previous_workouts = exercise_data.to_dict('records')
        
        # Make a prediction
        prediction_result = self.predictor.predict_workout(exercise, previous_workouts)
        
        print(f"\nPredicted weight for {exercise}: {prediction_result['weight']} kg/lb")
        print(f"Confidence: {prediction_result['confidence']:.2f}")
        print(f"Suggested reps: {prediction_result['suggested_reps']}")
        
        if 'analysis' in prediction_result:
            print("\nAnalysis:")
            for key, value in prediction_result['analysis'].items():
                print(f"- {key}: {value}")
        
        # Ask if the user performed this workout
        if input("\nDid you perform this workout? (y/n): ").lower().startswith('y'):
            # Collect actual results
            print("\nEnter the actual results:")
            actual_weight = self.data_collector._get_validated_numeric_input("Actual weight used (kg/lb): ")
            reps = self.data_collector._get_validated_numeric_input("Reps completed: ", is_int=True)
            
            rir_input = input("RIR (Reps In Reserve, optional): ").strip()
            rir = int(rir_input) if rir_input and rir_input.isdigit() else None
            
            success = input("Was the workout successful? (y/n): ").lower().startswith('y')
            
            # Record feedback
            feedback = self.predictor.record_feedback(
                exercise=exercise,
                predicted_weight=prediction_result['weight'],
                actual_weight=actual_weight,
                success=success,
                reps=reps,
                rir=rir
            )
            
            print(f"\nFeedback recorded: {feedback['message']}")
            
            # Save this workout to the training data
            workout_data = {
                "exercise": exercise,
                "weight": actual_weight,
                "reps": reps,
                "sets": 1,  # Default to 1 set for simplicity
                "date": datetime.now().date().isoformat(),
                "rir": rir,
                "success": success
            }
            
            self.data_collector.save_workout_data(workout_data)
            
            # Make a new prediction with the updated data
            print("\nUpdating prediction with new feedback...")
            previous_workouts.append(workout_data)
            new_prediction = self.predictor.predict_workout(exercise, previous_workouts)
            
            print(f"\nNext workout prediction for {exercise}: {new_prediction['weight']} kg/lb")
            print(f"Confidence: {new_prediction['confidence']:.2f}")
            print(f"Suggested reps: {new_prediction['suggested_reps']}")
        
        print("\nInteractive training session complete!")
    
    def handle_predict(self, args: argparse.Namespace) -> None:
        """
        Handle the predict command to make a weight prediction.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Making a Prediction ===")
        
        # Load training data
        training_data = self.data_collector.load_training_data(include_pretraining=True)
        
        if training_data.empty:
            print("No training data available. Please collect some data first.")
            return
        
        # Ensure model is trained
        self.predictor.fit_model(training_data)
        
        # Get the exercise
        exercise = args.exercise
        
        if not exercise:
            # List available exercises
            available_exercises = training_data['exercise'].unique()
            print("\nAvailable exercises:")
            for i, ex in enumerate(available_exercises, 1):
                print(f"{i}. {ex}")
            
            # Let user select an exercise
            selection = input("\nSelect an exercise (number or name): ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(available_exercises):
                exercise = available_exercises[int(selection) - 1]
            elif selection in available_exercises:
                exercise = selection
            else:
                print("Invalid selection. Please enter a new exercise name:")
                exercise = input().strip()
        
        # Get previous workouts for this exercise
        exercise_data = training_data[training_data['exercise'] == exercise]
        
        if len(exercise_data) == 0:
            print(f"No previous data for {exercise}. Cannot make a prediction.")
            return
        
        # Convert DataFrame rows to dictionaries
        previous_workouts = exercise_data.to_dict('records')
        
        # Make a prediction, passing the debug flag
        prediction_result = self.predictor.predict_workout(
            exercise, 
            previous_workouts,
            debug=getattr(args, 'debug', False)  # Get the debug flag or default to False
        )
        
        print(f"\nPredicted weight for {exercise}: {prediction_result['weight']} kg/lb")
        print(f"Confidence: {prediction_result['confidence']:.2f}")
        print(f"Suggested reps: {prediction_result['suggested_reps']}")
        
        if 'analysis' in prediction_result:
            print("\nAnalysis:")
            for key, value in prediction_result['analysis'].items():
                print(f"- {key}: {value}")
    
    def handle_reset(self, args: argparse.Namespace) -> None:
        """
        Handle the reset command to reset model data.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Resetting Model Data ===")
        
        reset_type = args.type if args.type else 'all'
        
        if reset_type not in ['all', 'feedback', 'weights', 'scalers']:
            print(f"Invalid reset type: {reset_type}")
            print("Valid types are: all, feedback, weights, scalers")
            return
        
        # Confirm reset
        if not args.yes:
            confirm = input(f"Are you sure you want to reset {reset_type} data? This cannot be undone. (y/n): ")
            if not confirm.lower().startswith('y'):
                print("Reset cancelled.")
                return
        
        # Perform the reset
        result = self.predictor.reset_model(reset_type)
        
        if result.get('success', False):
            print(f"Successfully reset {reset_type} data.")
        else:
            print(f"Failed to reset {reset_type} data: {result.get('message', 'Unknown error')}")
    
    def handle_export(self, args: argparse.Namespace) -> None:
        """
        Handle the export command to export training data.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Exporting Data ===")
        
        # Get the export file path
        file_path = args.file
        
        if not file_path:
            # Generate a default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"trainova_data_export_{timestamp}.csv"
        
        # Export the data
        success = self.data_collector.export_to_csv(
            file_path=file_path,
            include_pretraining=not args.exclude_pretraining
        )
        
        if success:
            print(f"Data successfully exported to {file_path}")
        else:
            print("Failed to export data.")
    
    def handle_import(self, args: argparse.Namespace) -> None:
        """
        Handle the import command to import workout data.
        
        Args:
            args: Command line arguments
        """
        print("\n=== Importing Data ===")
        
        # Check if the file exists
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        # Import the data
        df = self.data_collector.import_from_csv(
            file_path=args.file,
            is_pretraining=args.pretraining
        )
        
        if not df.empty:
            print(f"Successfully imported {len(df)} records from {args.file}")
        else:
            print("Failed to import data.")