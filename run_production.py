#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Production server runner for Trainova Feedback Network.
Optimized for running in Docker containers.
"""

import os
import sys
from waitress import serve

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the production server using waitress"""
    # Import Flask app
    from trainova_feedback_network.src.api.main import app
    
    # Define host and port
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 5009))
    
    print(f"Starting Trainova Feedback Network API on http://{host}:{port}")
    print("Running in production mode with waitress")
    
    # Use waitress as a production WSGI server
    serve(app, host=host, port=port, threads=4)

if __name__ == "__main__":
    main()