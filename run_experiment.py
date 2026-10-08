#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PsychoPy static problem experiment (modular version):

  - Question configuration from Excel
  - Per-participant data folder
  - One Excel/CSV file per participant (all trials in one file)
  - Webcam recording split by stage (here: one MP4 per trial)
  - LSL marker stream for event logging
  - No EEG functionality
"""

from psychopy import visual, core, event, gui, data
from psychopy.hardware import keyboard
import numpy as np
import os
from datetime import datetime

from config import DATA_ROOT, feedback_time, default_time_limit
from question_utils import load_question_pools, build_trials
from webcam_utils import start_webcam_recording, stop_webcam_recording
from marker_utils import send_marker, lsl_clock
from stimuli import create_all_stimuli

from rest_utils import run_rest_baseline
from letter_math_utils import run_baseline_letter_math


NASA_INTERVAL = 300.0  # Triggers every 5 minutes (unit: seconds)

# --------------------------------------------------------------
# Load question configuration & build trials
# --------------------------------------------------------------
levels_df, questions_by_level = load_question_pools()
trials = build_trials(levels_df, questions_by_level)

# --------------------------------------------------------------
# Basic PsychoPy experiment setup
# --------------------------------------------------------------
expName1 = "MathProblems"
expName = "StaticProblems"
expInfo = {"participant": ""}
dlg = gui.DlgFromDict(expInfo, title=expName)
if not dlg.OK:
    core.quit()

expInfo["date"] = data.getDateStr()

# Root data directory
if not os.path.isdir(DATA_ROOT):
    os.mkdir(DATA_ROOT)

# Per-participant folder inside data/
participant_id = str(expInfo["participant"]).strip()
if participant_id == "":
    participant_id = "unknown_participant"

participant_dir = os.path.join(DATA_ROOT, participant_id)
if not os.path.isdir(participant_dir):
    os.mkdir(participant_dir)

# Base filename for all data files for this participant
filename = os.path.join(
    participant_dir,
    f"{expName}_{expInfo['date']}"
)

filename1 = os.path.join(
    participant_dir,
    f"{expName1}_{expInfo['date']}"
)



# --- StaticProblems handler ---
thisExp = data.ExperimentHandler(
    name=expName,  # "StaticProblems"
    extraInfo=expInfo,
    savePickle=True,
    saveWideText=True,
    dataFileName=filename
)

# --- MathProblems handler ---
thisExp_math = data.ExperimentHandler(
    name=expName1,  # "MathProblems"
    extraInfo=expInfo,
    savePickle=True,
    saveWideText=True,
    dataFileName=filename1
)

# Create PsychoPy window
win = visual.Window(
    size=[1920, 1080],   # [1920, 1080],[1600, 900]
    fullscr=False,       #  if true, full screen showings
    color="black",
    units="height",
    allowStencil=True   # Let the cropping of TextBox2/scroll take effect
)

defaultKeyboard = keyboard.Keyboard()

# --------------------------------------------------------------
# Create all stimuli
# --------------------------------------------------------------
stims = create_all_stimuli(win)
instr = stims["instr"]
img_stim = stims["img_stim"]
prompt_text = stims["prompt_text"]
feedback_text = stims["feedback_text"]
answer_box = stims["answer_box"]
timer_text = stims["timer_text"]
justification_prompt = stims["justification_prompt"]
justification_box = stims["justification_box"]
nasa_instr = stims["nasa_instr"]
mental_text = stims["mental_text"]
performance_text = stims["performance_text"]
effort_text = stims["effort_text"]
frustration_text = stims["frustration_text"]
mental_slider = stims["mental_slider"]
performance_slider = stims["performance_slider"]
effort_slider = stims["effort_slider"]
frustration_slider = stims["frustration_slider"]
nasa_continue_text = stims["nasa_continue_text"]
end_text = stims["end_text"]

# --------------------------------------------------------------
# Helper: one NASA-TLX routine (single page)
# --------------------------------------------------------------
def run_nasa_once(win, level, trial_label, stims, defaultKeyboard, thisExp):
    """
    Display a page of NASA-TLX, wait for all four sliders to have ratings and press space.
    Will send the onset/submit/offset marker and return the score and duration.
    """

    nasa_instr         = stims["nasa_instr"]
    mental_text        = stims["mental_text"]
    performance_text   = stims["performance_text"]
    effort_text        = stims["effort_text"]
    frustration_text   = stims["frustration_text"]
    mental_slider      = stims["mental_slider"]
    performance_slider = stims["performance_slider"]
    effort_slider      = stims["effort_slider"]
    frustration_slider = stims["frustration_slider"]
    nasa_continue_text = stims["nasa_continue_text"]

    # Reset sliders
    mental_slider.reset()
    performance_slider.reset()
    effort_slider.reset()
    frustration_slider.reset()

    # Onset marker & time
    nasa_display_event = lsl_clock.getTime()
    send_marker(f"NASA_onset_{level}_{trial_label}")

    nasa_clock = core.Clock()

    while True:
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            thisExp.abort()
            thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
            thisExp.saveAsPickle(thisExp.dataFileName)

            core.quit()

        nasa_instr.draw()
        mental_text.draw()
        performance_text.draw()
        effort_text.draw()
        frustration_text.draw()

        mental_slider.draw()
        performance_slider.draw()
        effort_slider.draw()
        frustration_slider.draw()

        sliders = [mental_slider, performance_slider, effort_slider, frustration_slider]
        all_answered = all(s.getRating() is not None for s in sliders)

        if all_answered:
            nasa_continue_text.draw()
            keys = event.getKeys()
            if "space" in keys:
                nasa_submit_event = lsl_clock.getTime()
                send_marker(f"NASA_submit_{level}_{trial_label}")
                break

        win.flip()

    send_marker(f"NASA_offset_{level}_{trial_label}")
    nasa_duration = nasa_clock.getTime()

    return {
        "nasa_display_event": nasa_display_event,
        "nasa_mental":        mental_slider.getRating(),
        "nasa_performance":   performance_slider.getRating(),
        "nasa_effort":        effort_slider.getRating(),
        "nasa_frustration":   frustration_slider.getRating(),
        "nasa_duration":      nasa_duration,
    }



# ---- Rest  ----
# rest_out = run_rest_baseline(
#     win=win,
#     duration_sec=180.0,
#     stims=stims,
#     participant_dir=participant_dir,
#     expName=expName,
#     date_str=expInfo["date"],
#     send_marker=send_marker,
#     lsl_clock=lsl_clock,
#     start_webcam_recording=start_webcam_recording,
#     stop_webcam_recording=stop_webcam_recording,
#     defaultKeyboard=defaultKeyboard,
#     thisExp=thisExp,
#     session_tag="rest",
#     prompt_title="Rest for 3 min",
#     prompt_hint="[press space to start]"
# )

# thisExp.addData("phase", "rest")
# for k, v in rest_out.items():
#     thisExp.addData(k, v)
# thisExp.nextEntry()



wm_out = run_baseline_letter_math(
    win=win,
    stims=stims,
    defaultKeyboard=defaultKeyboard,
    thisExp=thisExp_math,
    participant_dir=participant_dir,
    expName=expName1,
    date_str=expInfo["date"],
    send_marker=send_marker,
    lsl_clock=lsl_clock,
    run_nasa_once=run_nasa_once,
    math_xlsx_path="math_questions/math_questions.xlsx",
    n_trials=1,
    letter_sec=5.0,
    math_sec=30.0,
    block_tag="Letter–Math",
    record_webcam=True, # True is record vedio
    start_webcam_recording=start_webcam_recording,
    stop_webcam_recording=stop_webcam_recording,
    instruction_text="Remember the letter and solve the math problems.",
    prompt_title="Letter–Math (10 trials)",
    prompt_hint="[press space to start]",
)

win.flip()

# --------------------------------------------------------------
# Instruction Screen (no recording here, only main trials)
# --------------------------------------------------------------
instr.draw()
win.flip()
send_marker("instructions_on")
event.waitKeys(keyList=["space"])
send_marker("instructions_off")


# --------------------------------------------------------------
# Main Trial Loop
# --------------------------------------------------------------
for trial_index, trial in enumerate(trials, start=1):
    # Update date to have ms-level timestamp per trial (same as original)
    expInfo["date"] = datetime.now().strftime("%Y-%m-%d_%Hh%M.%S.%f")[:-3]
    level = trial["level"]
    image_path = trial["image"]
    correct_answer = trial["answer"]
    TIME_LIMIT = float(trial.get("time_limit", default_time_limit))

    # Enable "NASA every 5 minutes" only for Open_ended questions
    nasa_block_idx = 1
    next_nasa_time = NASA_INTERVAL

    display_event = np.nan
    answer_event = np.nan    # time when answer is submitted (first key typed)
    feedback_event = np.nan  # time when correctness feedback is computed

    justification_str = ""
    justification_event = np.nan

    print(
        f"[Trial {trial_index}] level={level}, image={image_path}, "
        f"answer={correct_answer}, time_limit={TIME_LIMIT}s"
    )

    # ----------------------------------------------------------
    # Start webcam recording for this trial (one or multiple segments)
    # ----------------------------------------------------------
    trial_label = f"trial{trial_index:03d}"
    video_segment_idx = 1
    webcam_video_path = os.path.join(
        participant_dir,
        f"{expName}_{expInfo['date']}_{trial_label}_seg{video_segment_idx}.mp4"
    )
    start_webcam_recording(webcam_video_path)

    # Set the problem image to display
    img_stim.image = image_path

    # Reset participant input
    answer_str = ""

    # Start trial timing
    send_marker(f"trial_onset_{level}_{trial_label}")
    trial_clock = core.Clock()
    nasa_cumulative = 0.0   # Accumulate the time spent by all NASA (seconds)
    # Record display event time (when trial starts showing)
    send_marker(f"display_onset_{level}_{trial_label}")
    display_event = lsl_clock.getTime()
    rt = None        # Reaction time
    timeout = False  # Whether time limit was exceeded
    periodic_nasa_data = {}

    # ------------------------------
    # Trial Input Loop
    # ------------------------------
    while True:
        wall_elapsed = trial_clock.getTime()
        elapsed = wall_elapsed - nasa_cumulative  # Effective answering time = total time - NASA accumulated time
        #  Periodic NASA only for Open_ended, before the answer is submitted
        if (
            level == "Open_ended"
            and rt is None
            and elapsed >= next_nasa_time
        ):

            nasa_start_wall = trial_clock.getTime()

            # 1) Close current video segment
            stop_webcam_recording()

            # 2) Block-level marker for EEG / MuseLab
            send_marker(f"NASA_periodic_block{nasa_block_idx}_onset_{level}_{trial_label}")

            # 3) Run one NASA page
            block_id = nasa_block_idx
            nasa_results_block = run_nasa_once(
                win=win,
                level=level,
                trial_label=f"{trial_label}_block{block_id}",
                stims=stims,
                defaultKeyboard=defaultKeyboard,
                thisExp=thisExp,
            )

            # 4) Log this block's NASA to current trial (separate columns)
            periodic_nasa_data[f"nasa_block{block_id}_mental"]        = nasa_results_block["nasa_mental"]
            periodic_nasa_data[f"nasa_block{block_id}_performance"]   = nasa_results_block["nasa_performance"]
            periodic_nasa_data[f"nasa_block{block_id}_effort"]        = nasa_results_block["nasa_effort"]
            periodic_nasa_data[f"nasa_block{block_id}_frustration"]   = nasa_results_block["nasa_frustration"]
            periodic_nasa_data[f"nasa_block{block_id}_duration"]      = nasa_results_block["nasa_duration"]


            send_marker(f"NASA_periodic_block{block_id}_offset_{level}_{trial_label}")


            # Measure the actual wall clock time occupied by NASA
            nasa_end_wall = trial_clock.getTime()
            nasa_spent = nasa_end_wall - nasa_start_wall
            nasa_cumulative += nasa_spent   

            # 5) Prepare next interval and next video segment
            nasa_block_idx += 1
            next_nasa_time += NASA_INTERVAL

            video_segment_idx += 1
            webcam_video_path = os.path.join(
                participant_dir,
                f"{expName}_{expInfo['date']}_{trial_label}_seg{video_segment_idx}.mp4"
            )
            start_webcam_recording(webcam_video_path)

            # Continue solving the same Open_ended question
            continue

        # Check time limit
        if elapsed >= TIME_LIMIT:
            timeout = True
            send_marker(f"timeout_{level}_{trial_label}")
            break

        # Handle escape to quit the experiment
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            thisExp.abort()
            thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
            thisExp.saveAsPickle(thisExp.dataFileName)

            stop_webcam_recording()
            core.quit()

        # Handle typed keys (per frame)
        keys = event.getKeys()
        for k in keys:

            # --- Record answer_event when user starts typing ---
            if np.isnan(answer_event):
                if (len(k) == 1) or k in ["space", "period", "comma", "minus"] or k.startswith("num_"):
                    answer_event = lsl_clock.getTime()

            # Submit answer: ENTER
            if k == "return":
                if len(answer_str) > 0:
                    rt = elapsed
                    send_marker(f"response_submitted_{level}_{trial_label}")
                    break

            # Delete last character
            elif k == "backspace":
                answer_str = answer_str[:-1]

            # Space character
            elif k == "space":
                answer_str += " "

            # Common punctuation
            elif k == "period":
                answer_str += "."
            elif k == "comma":
                answer_str += ","
            elif k == "minus":
                answer_str += "-"

            # Numeric keypad input (num_0 ... num_9)
            elif k.startswith("num_") and k[-1].isdigit():
                answer_str += k[-1]

            # Any single printable character
            elif len(k) == 1:
                answer_str += k

        # If RT is set, participant submitted an answer
        if rt is not None:
            break

        # Draw all visual stimuli for this frame
        img_stim.draw()
        prompt_text.draw()

        # Remaining time display
        time_left = max(0.0, TIME_LIMIT - elapsed)
        timer_text.text = f"Time left: {int(time_left)}s"
        timer_text.draw()

        # Show current typed answer
        answer_box.text = answer_str
        answer_box.draw()

        # Present the frame
        win.flip()

    # ----------------------------------------------------------
    # Justification (only for Open_ended level)
    # ----------------------------------------------------------
    if level == "Open_ended":
        justification_str = ""
        justification_box.text = ""
        send_marker(f"justification_onset_{level}_{trial_label}")
        justification_clock = core.Clock()

        while True:
            if defaultKeyboard.getKeys(keyList=["escape"]):
                send_marker("experiment_abort")
                thisExp.abort()
                thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
                thisExp.saveAsPickle(thisExp.dataFileName)

                stop_webcam_recording()
                core.quit()

            keys = event.getKeys()
            done_just = False

            for k in keys:
                if np.isnan(justification_event):
                    if (len(k) == 1) or k in ["space", "period", "comma", "minus"] or k.startswith("num_"):
                        justification_event = lsl_clock.getTime()
                        send_marker(f"justification_typing_start_{level}_{trial_label}")

                if k == "return":
                    send_marker(f"justification_submitted_{level}_{trial_label}")
                    done_just = True
                    break

                elif k == "backspace":
                    justification_str = justification_str[:-1]

                elif k == "space":
                    justification_str += " "

                elif k == "period":
                    justification_str += "."
                elif k == "comma":
                    justification_str += ","
                elif k == "minus":
                    justification_str += "-"

                elif k.startswith("num_") and k[-1].isdigit():
                    justification_str += k[-1]

                elif len(k) == 1:
                    justification_str += k

            if done_just:
                break

            justification_prompt.draw()
            justification_box.text = justification_str
            justification_box.draw()
            win.flip()
    else:
        pass

    # Stop webcam recording for question-answer phase (last segment)
    stop_webcam_recording()

    # ----------------------------------------------------------
    # Evaluate correctness
    # ----------------------------------------------------------
    typed = answer_str.strip()

    if rt is None:  # No response or timed out
        rt = np.nan
        is_correct = False
        fb_msg = "Time out or no response."
    else:
        # Try numeric comparison first
        try:
            typed_f = float(typed)
            correct_f = float(correct_answer)
            is_correct = abs(typed_f - correct_f) < 1e-6
        except ValueError:
            # Fall back to string comparison
            is_correct = (typed == correct_answer)

        fb_msg = "Correct!" if is_correct else f"Incorrect.\nCorrect answer: {correct_answer}"

    feedback_text.text = fb_msg
    send_marker(f"feedback_ready_{level}_{trial_label}")
    feedback_event = lsl_clock.getTime()

    # ----------------------------------------------------------
    # Log trial data (all trials go to the SAME CSV file)
    # ----------------------------------------------------------
    thisExp.addData("trial_index", trial_index)
    thisExp.addData("trial_label", trial_label)
    thisExp.addData("level", level)
    thisExp.addData("image", image_path)
    thisExp.addData("time_limit", TIME_LIMIT)
    thisExp.addData("correct_answer", correct_answer)
    thisExp.addData("typed_answer", typed)
    thisExp.addData("rt", rt)
    thisExp.addData("is_correct", int(is_correct))

    # Justification
    thisExp.addData("justification_text", justification_str)
    thisExp.addData("justification_event", justification_event)

    # Event timestamps (monotonic clock)
    thisExp.addData("display_event", display_event)
    thisExp.addData("answer_event", answer_event)
    thisExp.addData("feedback_event", feedback_event)

    # ----------------------------------------------------------
    # Start webcam recording for feedback phase
    # ----------------------------------------------------------
    trial_label = f"trial{trial_index:03d}"
    webcam_video_path = os.path.join(
        participant_dir,
        f"{expName}_{expInfo['date']}_{trial_label}_feedback.mp4"
    )
    start_webcam_recording(webcam_video_path)

    # ----------------------------------------------------------
    # Show feedback for 4 seconds
    # ----------------------------------------------------------
    send_marker(f"feedback_{level}_{trial_label}_{'correct' if is_correct else 'incorrect'}")

    fb_clock = core.Clock()
    while fb_clock.getTime() < feedback_time:
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            thisExp.abort()
            thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
            thisExp.saveAsPickle(thisExp.dataFileName)

            stop_webcam_recording()
            core.quit()
        feedback_text.draw()
        win.flip()

    # ----------------------------------------------------------
    # Stop webcam recording for this trial (feedback)
    # ----------------------------------------------------------
    stop_webcam_recording()

    # ----------------------------------------------------------
    # NASA-TLX questionnaire AFTER feedback (final NASA)
    # ----------------------------------------------------------
    nasa_results_final = run_nasa_once(
        win=win,
        level=level,
        trial_label=trial_label,
        stims=stims,
        defaultKeyboard=defaultKeyboard,
        thisExp=thisExp,
    )

    thisExp.addData("nasa_display_event", nasa_results_final["nasa_display_event"])
    thisExp.addData("nasa_mental",        nasa_results_final["nasa_mental"])
    thisExp.addData("nasa_performance",   nasa_results_final["nasa_performance"])
    thisExp.addData("nasa_effort",        nasa_results_final["nasa_effort"])
    thisExp.addData("nasa_frustration",   nasa_results_final["nasa_frustration"])
    thisExp.addData("nasa_duration",      nasa_results_final["nasa_duration"])

    # Write periodic NASA
    for key, value in periodic_nasa_data.items():
        thisExp.addData(key, value)
    # Finalize this trial row
    thisExp.nextEntry()

# --------------------------------------------------------------
# End Screen
# --------------------------------------------------------------
send_marker("experiment_end")
win.flip()
end_text.draw()
win.flip()
core.wait(3.0)

# Final save of experiment data (ONE CSV per participant)
thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
thisExp.saveAsPickle(thisExp.dataFileName)

thisExp.abort()

# Extra safety: ensure webcam is stopped
stop_webcam_recording()

win.close()
core.quit()
