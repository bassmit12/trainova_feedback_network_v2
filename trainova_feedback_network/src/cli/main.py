#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from typing import List, Optional

from .commands import CommandHandler

def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser for the Trainova CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        prog="trainova",
        description="Trainova Feedback Network CLI - A weight prediction and training tool",
        epilog="Use 'trainova COMMAND --help' for more information about a specific command."
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Pretrain command
    pretrain_parser = subparsers.add_parser(
        "pretrain", 
        help="Pretrain the model with existing or generated data"
    )
    pretrain_parser.add_argument(
        "--generate-mock", 
        action="store_true",
        help="Generate mock data for pretraining"
    )
    pretrain_parser.add_argument(
        "--samples", 
        type=int, 
        default=100,
        help="Number of mock samples to generate (default: 100)"
    )
    pretrain_parser.add_argument(
        "--exercises", 
        type=str,
        help="Comma-separated list of exercises to generate data for"
    )
    pretrain_parser.add_argument(
        "--import-file", 
        type=str,
        help="Import data from a CSV file for pretraining"
    )
    
    # Collect command
    collect_parser = subparsers.add_parser(
        "collect", 
        help="Collect workout data interactively"
    )
    collect_parser.add_argument(
        "--exercise", 
        type=str,
        help="Specify the exercise type"
    )
    collect_parser.add_argument(
        "--pretraining", 
        action="store_true",
        help="Save collected data as pretraining data"
    )
    
    # Interactive training command
    interactive_parser = subparsers.add_parser(
        "interactive", 
        help="Start an interactive training session"
    )
    interactive_parser.add_argument(
        "--exercise", 
        type=str,
        help="Specify the exercise type for the session"
    )
    
    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", 
        help="Make a weight prediction for a specific exercise"
    )
    predict_parser.add_argument(
        "--exercise", 
        type=str,
        help="Specify the exercise type for the prediction"
    )
    predict_parser.add_argument(
        "--debug", 
        action="store_true",
        help="Show detailed debugging information about the prediction process"
    )
    
    # Reset command
    reset_parser = subparsers.add_parser(
        "reset", 
        help="Reset model data"
    )
    reset_parser.add_argument(
        "--type", 
        type=str, 
        choices=["all", "feedback", "weights", "scalers"],
        default="all",
        help="Type of reset to perform (default: all)"
    )
    reset_parser.add_argument(
        "-y", "--yes", 
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    # Export command
    export_parser = subparsers.add_parser(
        "export", 
        help="Export training data to a CSV file"
    )
    export_parser.add_argument(
        "--file", 
        type=str,
        help="File path for the exported data"
    )
    export_parser.add_argument(
        "--exclude-pretraining", 
        action="store_true",
        help="Exclude pretraining data from the export"
    )
    
    # Import command
    import_parser = subparsers.add_parser(
        "import", 
        help="Import workout data from a CSV file"
    )
    import_parser.add_argument(
        "file", 
        type=str,
        help="File path of the CSV file to import"
    )
    import_parser.add_argument(
        "--pretraining", 
        action="store_true",
        help="Save imported data as pretraining data"
    )
    
    return parser

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the Trainova CLI.
    
    Args:
        args: Command-line arguments (uses sys.argv if None)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # If no command is provided, show help and exit
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    # Create command handler
    handler = CommandHandler()
    
    try:
        # Route command to the appropriate handler
        if parsed_args.command == "pretrain":
            handler.handle_pretrain(parsed_args)
        elif parsed_args.command == "collect":
            handler.handle_collect(parsed_args)
        elif parsed_args.command == "interactive":
            handler.handle_interactive_training(parsed_args)
        elif parsed_args.command == "predict":
            handler.handle_predict(parsed_args)
        elif parsed_args.command == "reset":
            handler.handle_reset(parsed_args)
        elif parsed_args.command == "export":
            handler.handle_export(parsed_args)
        elif parsed_args.command == "import":
            handler.handle_import(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            parser.print_help()
            return 1
            
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())