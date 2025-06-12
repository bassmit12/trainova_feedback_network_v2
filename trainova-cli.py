#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Add the main package directory to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, "trainova_feedback_network"))

from src.cli.main import main

if __name__ == "__main__":
    sys.exit(main())