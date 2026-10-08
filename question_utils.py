#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utilities for loading question configuration and building trial list.
"""

import random
import pandas as pd

from config import LEVEL_FILE, QUESTION_FILE


def infer_level_from_filename(fname: str) -> str:
    """
    Infer the question level based on patterns in the image filename.
    Expected patterns:
        - "open_"            -> "Open_ended"
        - "close_easy_"      -> "Closed_ended_easy"
        - "close_moderate_"  -> "Closed_ended_moderate"
    """
    f = fname.lower()
    if "open_" in f:
        return "Open_ended"
    elif "close_easy_" in f:
        return "Closed_ended_easy"
    elif "close_moderate_" in f:
        return "Closed_ended_moderate"
    else:
        raise ValueError(f"Cannot infer level from filename: {fname}")


def load_question_pools():
    """
    Load levels_df and question dataframe with inferred levels,
    and group questions by level.
    Returns:
        levels_df, questions_by_level (dict[level_name -> DataFrame])
    """
    levels_df = pd.read_excel(LEVEL_FILE)    # must have: level, n_trials
    q_df = pd.read_excel(QUESTION_FILE)      # must have: Prompts, Answers, TimeLimit (optional)

    # Add a "level" column to questions based on the filename
    q_df["level"] = q_df["Prompts"].apply(infer_level_from_filename)

    # Group questions by level into separate pools
    questions_by_level = {}
    for level_name, sub in q_df.groupby("level"):
        questions_by_level[level_name] = sub.reset_index(drop=True)

    return levels_df, questions_by_level


def build_trials(levels_df, questions_by_level):
    """
    Build the full trial list according to ques_trials.xlsx.
    Each trial is a dict with keys:
        - level
        - image
        - answer
        - time_limit
    The logic is identical to the original script.
    """
    trials = []

    for _, row in levels_df.iterrows():
        level_name = row["level"]
        n_trials = int(row["n_trials"])

        if level_name not in questions_by_level:
            raise ValueError(
                f"Level '{level_name}' in {LEVEL_FILE} has no matching entries in {QUESTION_FILE}."
            )

        pool = questions_by_level[level_name]
        if n_trials > len(pool):
            raise ValueError(
                f"Requested {n_trials} trials for {level_name}, but only {len(pool)} questions available."
            )

        # Randomly sample questions within each level
        chosen_rows = pool.sample(n_trials, replace=False)
        for _, crow in chosen_rows.iterrows():
            # Get per-question time limit; default = 60s if missing
            try:
                tlimit = float(crow.get("TimeLimit", 60.0))
            except Exception:
                tlimit = 60.0

            trials.append({
                "level": level_name,
                "image": crow["Prompts"],
                "answer": str(crow["Answers"]).strip(),
                "time_limit": tlimit
            })

    # Shuffle all selected trials to randomize order across levels
    random.shuffle(trials)
    return trials
