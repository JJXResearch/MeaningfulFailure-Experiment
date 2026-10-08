#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Global configuration and paths for the static problem experiment.
"""

import os

# --------------------------------------------------------------
# Customize setting
# --------------------------------------------------------------
feedback_time = 4.0
default_time_limit = 120.0

# --------------------------------------------------------------
# Paths and working directory
# --------------------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THIS_DIR)

# Excel files
LEVEL_FILE = "questions/ques_trials.xlsx"   # Columns: level, n_trials
QUESTION_FILE = "questions/questions.xlsx"  # Columns: Prompts, Answers, TimeLimit (optional)

# Root data directory
DATA_ROOT = os.path.join(THIS_DIR, "data")
