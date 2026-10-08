# baseline_letter_math_utils.py
# -*- coding: utf-8 -*-

"""
Baseline Letter–Math module (final spec + feedback after recalls)

Input Excel (math.xlsx) headers:
  - Question : image path to show (e.g., Math_Stimuli/Slide14.jpg)
  - Answer   : correct answer (numeric or string)
  - Letters  : letter shown before the math

Experiment structure:
  - Instruction screen (space to start)
  - Random, no-repetition sampling of N trials (default N=10)
  - Each trial:
      Segment A video ("task"): Letter (10s) + Math (<=40s, Enter allowed, no timer) + Recall(s)
          - Recall single-letter: asked every trial (letter correctness ignored for feedback)
          - After trial 5: sequence recall for letters 1–5 (input)
          - After trial 10: sequence recall for letters 6–10 (input)
      Segment B video ("feedback"): feedback screen(s) + NASA
          - After recall_single: show math correctness feedback (show correct answer if wrong)
          - After seq recall (trial 5/10): show sequence correctness feedback (show correct sequence if wrong)
          - Then run NASA (per trial)

Scoring:
  - Math correctness: numeric tolerant OR string exact
  - Sequence recall: ignores spaces, case-insensitive
  - Letter recall: recorded but not used in feedback

All key events:
  - send_marker(...) and lsl_clock.getTime() are used for alignment
"""

import os
import random
import numpy as np
from psychopy import core, event, data, visual


# =========================
# Helpers
# =========================
def _normalize_seq(s: str) -> str:
    """Ignore spaces and case for sequence comparison."""
    if s is None:
        return ""
    return "".join(str(s).strip().lower().split())


def _safe_float_equal(a, b, eps=1e-6) -> bool:
    """Numeric equality with tolerance; returns False if casting fails."""
    try:
        return abs(float(a) - float(b)) < eps
    except Exception:
        return False


def _is_image_path(p: str) -> bool:
    if not isinstance(p, str):
        return False
    pl = p.strip().lower()
    return pl.endswith(".png") or pl.endswith(".jpg") or pl.endswith(".jpeg") or pl.endswith(".bmp") or pl.endswith(".tif") or pl.endswith(".tiff")


def _resolve_image_path(img_path: str, base_dir: str | None) -> str:
    """
    Make image path robust:
      - If img_path is absolute and exists, use it.
      - Else, if base_dir is provided, join(base_dir, img_path).
      - Else, return img_path as-is.
    """
    if not isinstance(img_path, str):
        return str(img_path)

    p = img_path.strip()
    if os.path.isabs(p) and os.path.exists(p):
        return p

    if base_dir is not None:
        joined = os.path.join(base_dir, p)
        if os.path.exists(joined):
            return joined

    return p


def _update_text_with_keys(text: str, keys) -> str:
    """Apply PsychoPy event.getKeys outputs to a text buffer."""
    for k in keys:
        if k == "backspace":
            text = text[:-1]
        elif k == "space":
            text += " "
        elif k == "period":
            text += "."
        elif k == "comma":
            text += ","
        elif k == "minus":
            text += "-"
        elif k.startswith("num_") and k[-1].isdigit():
            text += k[-1]
        elif len(k) == 1:
            text += k
        # ignore other keys; return handled outside
    return text


def _collect_text_until_enter(
    win,
    defaultKeyboard,
    prompt_stim,
    answer_box,
    send_marker,
    lsl_clock,
    marker_prefix,
    allow_empty=False,
):
    """
    Collect typed input until ENTER is pressed.

    Markers emitted:
      - {marker_prefix}_onset
      - {marker_prefix}_typing_start   (first printable key)
      - {marker_prefix}_submit         (on Enter)
      - {marker_prefix}_offset

    Returns:
      typed_text, first_key_ts, submit_ts, ts_dict
      If abort (ESC): returns (None, None, None, None)
    """
    typed = ""
    first_key_ts = np.nan
    submit_ts = np.nan

    send_marker(f"{marker_prefix}_onset")
    onset_ts = lsl_clock.getTime()

    while True:
        if defaultKeyboard.getKeys(keyList=["escape"]):
            return None, None, None, None

        keys = event.getKeys()

        # typing start
        if np.isnan(first_key_ts):
            for k in keys:
                if (len(k) == 1) or k in ["space", "period", "comma", "minus"] or k.startswith("num_"):
                    first_key_ts = lsl_clock.getTime()
                    send_marker(f"{marker_prefix}_typing_start")
                    break

        # submit
        if "return" in keys:
            if allow_empty or len(typed.strip()) > 0:
                submit_ts = lsl_clock.getTime()
                send_marker(f"{marker_prefix}_submit")
                break

        typed = _update_text_with_keys(typed, keys)

        if prompt_stim is not None:
            prompt_stim.draw()
        if answer_box is not None:
            answer_box.text = typed
            answer_box.draw()
        win.flip()

    send_marker(f"{marker_prefix}_offset")
    offset_ts = lsl_clock.getTime()

    return typed, first_key_ts, submit_ts, {"onset_ts": onset_ts, "offset_ts": offset_ts}


def _show_feedback_screen(
    win,
    defaultKeyboard,
    send_marker,
    lsl_clock,
    feedback_text_stim,
    msg: str,
    feedback_sec: float,
    marker_prefix: str,
):
    """
    Show a feedback message for feedback_sec seconds.
    Emits:
      - {marker_prefix}_onset
      - {marker_prefix}_offset
    Returns:
      onset_ts, offset_ts
    """
    if feedback_text_stim is None:
        feedback_text_stim = visual.TextStim(win, text="", height=0.06, color="white", pos=(0, 0), wrapWidth=1.3)

    feedback_text_stim.text = msg

    send_marker(f"{marker_prefix}_onset")
    onset_ts = lsl_clock.getTime()

    fb_clock = core.Clock()
    while fb_clock.getTime() < float(feedback_sec):
        if defaultKeyboard.getKeys(keyList=["escape"]):
            return None, None

        feedback_text_stim.draw()
        win.flip()

    send_marker(f"{marker_prefix}_offset")
    offset_ts = lsl_clock.getTime()
    return onset_ts, offset_ts


# =========================
# Main baseline function
# =========================
def run_baseline_letter_math(
    win,
    stims,
    defaultKeyboard,
    thisExp,
    participant_dir,
    expName,
    date_str,
    send_marker,
    lsl_clock,
    run_nasa_once,
    math_xlsx_path,
    n_trials=10,
    letter_sec=10.0,
    math_sec=40.0,
    block_tag="baseline",
    # Webcam segmentation (your requirement):
    record_webcam=True,
    start_webcam_recording=None,
    stop_webcam_recording=None,
    # Path handling:
    image_base_dir=None,
    # Feedback display duration:
    feedback_sec=4.0,
    mathfilename=None,
    instruction_text="Remember the letter and solve the math problems.",
    prompt_title="Letter–Math (10 trials)",
    prompt_hint="[press space to start]",
):
    """
    Executes the baseline block and logs rows to thisExp.

    Webcam segmentation per trial:
      - Segment A (task): Letter + Math + Recall(s)
      - Segment B (feedback): feedback screen(s) + NASA
    """

    # ---- Webcam parameter check ----
    if record_webcam:
        if start_webcam_recording is None or stop_webcam_recording is None:
            raise ValueError("record_webcam=True requires start_webcam_recording and stop_webcam_recording")

    # ---- Get / create stimuli ----
    img_stim = stims.get("img_stim", None)
    answer_box = stims.get("answer_box", None)

    # Instruction stimuli

    # instr_stim = stims.get("baseline_instr", None)
    # if instr_stim is None:
    #     instr_stim = visual.TextStim(win, text=instruction_text, height=0.05, color="white", pos=(0, 0.05), wrapWidth=1.2)
    # else:
    #     instr_stim.text = instruction_text

    # press_space_stim = stims.get("baseline_press_space", None)
    # if press_space_stim is None:
    #     press_space_stim = visual.TextStim(win, text="[press space to start]", height=0.04, color="white", pos=(0, -0.35))

    # Prompt-style instruction page (title + subtitle + hint)

    baseline_title_stim = stims.get("baseline_title", None)
    if baseline_title_stim is None:
        baseline_title_stim = visual.TextStim(
            win, text=prompt_title, height=0.08, color="white", pos=(0, 0.05), wrapWidth=1.4
        )
    else:
        baseline_title_stim.text = prompt_title

    baseline_subtitle_stim = stims.get("baseline_subtitle", None)
    if baseline_subtitle_stim is None:
        baseline_subtitle_stim = visual.TextStim(
            win, text=instruction_text, height=0.045, color="white", pos=(0, -0.10), wrapWidth=1.3
        )
    else:
        baseline_subtitle_stim.text = instruction_text

    baseline_hint_stim = stims.get("baseline_hint", None)
    if baseline_hint_stim is None:
        baseline_hint_stim = visual.TextStim(
            win, text=prompt_hint, height=0.04, color="white", pos=(0, -0.35)
        )
    else:
        baseline_hint_stim.text = prompt_hint


    # Letter display stim
    letter_stim = stims.get("baseline_letter", None)
    if letter_stim is None:
        letter_stim = visual.TextStim(win, text="", height=0.18, color="white", pos=(0, 0))

    # Math title (optional)
    math_title_stim = stims.get("baseline_math_title", None)
    if math_title_stim is None:
        math_title_stim = visual.TextStim(win, text="Solve the math problem:", height=0.05, color="white", pos=(0, 0.38))

    # Feedback text stim (reuse your main feedback_text if provided)
    feedback_text_stim = stims.get("feedback_text", None)
    if feedback_text_stim is None:
        feedback_text_stim = visual.TextStim(win, text="", height=0.06, color="white", pos=(0, 0), wrapWidth=1.3)

    # Recall prompts
    recall_single_prompt = stims.get("baseline_recall_single_prompt", None)
    if recall_single_prompt is None:
        recall_single_prompt = visual.TextStim(
            win,
            text="What letter did you see before math?",
            height=0.05,
            color="white",
            pos=(0, 0.2),
            wrapWidth=1.2,
        )

    recall_seq_prompt = stims.get("baseline_recall_seq_prompt", None)
    if recall_seq_prompt is None:
        recall_seq_prompt = visual.TextStim(
            win,
            text="Type the letters in order, then press ENTER.",
            height=0.05,
            color="white",
            pos=(0, 0.2),
            wrapWidth=1.2,
        )

    # ---- Load and sample trials (random, no repetition) ----
    rows = data.importConditions(math_xlsx_path)
    if len(rows) < n_trials:
        raise ValueError(f"{math_xlsx_path} has only {len(rows)} rows, but n_trials={n_trials}.")

    sampled = random.sample(rows, n_trials)
    random.shuffle(sampled)

    # ---- Instruction page ----
    send_marker(f"{block_tag}_instr_onset")
    instr_onset_ts = lsl_clock.getTime()

    while True:
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            thisExp.abort()
            core.quit()

        baseline_title_stim.draw()
        baseline_subtitle_stim.draw()
        baseline_hint_stim.draw()
        win.flip()

        if "space" in event.getKeys():
            break

    send_marker(f"{block_tag}_instr_offset")
    instr_offset_ts = lsl_clock.getTime()


    send_marker(f"{block_tag}_instr_offset")
    instr_offset_ts = lsl_clock.getTime()

    # ---- Block onset ----
    send_marker(f"{block_tag}_onset")
    block_onset_ts = lsl_clock.getTime()

    presented_letters = []

    # ---- Main trials ----
    for i, tr in enumerate(sampled, start=1):
        trial_tag = f"{block_tag}_t{i:02d}"

        q_img_raw = str(tr.get("Question", "")).strip()
        ans = str(tr.get("Answer", "")).strip()
        letter = str(tr.get("Letters", "")).strip()

        presented_letters.append(letter)

        # ==========================
        # Segment A video: Letter + Math + Recall(s) INPUT ONLY
        # ==========================
        task_video_path = None
        if record_webcam:
            task_video_path = os.path.join(participant_dir, f"{expName}_{date_str}_{trial_tag}_task.mp4")
            start_webcam_recording(task_video_path)
            send_marker(f"{trial_tag}_task_video_onset")

        # 1) Letter
        send_marker(f"{trial_tag}_letter_onset")
        letter_onset_ts = lsl_clock.getTime()

        letter_stim.text = letter
        t_letter = core.Clock()
        while t_letter.getTime() < float(letter_sec):
            if defaultKeyboard.getKeys(keyList=["escape"]):
                send_marker("experiment_abort")
                if record_webcam:
                    stop_webcam_recording()
                thisExp.abort()
                core.quit()

            letter_stim.draw()
            win.flip()

        send_marker(f"{trial_tag}_letter_offset")
        letter_offset_ts = lsl_clock.getTime()

        # 2) Math (<= 40s, Enter submits, no countdown)
        send_marker(f"{trial_tag}_math_onset")
        math_onset_ts = lsl_clock.getTime()

        q_img = _resolve_image_path(q_img_raw, image_base_dir)

        typed_math = ""
        first_math_key_ts = np.nan
        math_submit_ts = np.nan
        submitted = False

        t_math = core.Clock()
        while t_math.getTime() < float(math_sec):
            if defaultKeyboard.getKeys(keyList=["escape"]):
                send_marker("experiment_abort")
                if record_webcam:
                    stop_webcam_recording()
                thisExp.abort()
                core.quit()

            keys = event.getKeys()

            # typing start marker
            if np.isnan(first_math_key_ts):
                for k in keys:
                    if (len(k) == 1) or k in ["space", "period", "comma", "minus"] or k.startswith("num_"):
                        first_math_key_ts = lsl_clock.getTime()
                        send_marker(f"{trial_tag}_math_typing_start")
                        break

            # Enter submits early
            if "return" in keys:
                math_submit_ts = lsl_clock.getTime()
                send_marker(f"{trial_tag}_math_submit")
                submitted = True
                break

            typed_math = _update_text_with_keys(typed_math, keys)

            # draw math screen
            math_title_stim.draw()

            if img_stim is not None and _is_image_path(q_img):
                img_stim.image = q_img
                img_stim.draw()
            else:
                visual.TextStim(
                    win,
                    text=str(q_img_raw),
                    height=0.05,
                    color="white",
                    pos=(0, 0.15),
                    wrapWidth=1.4,
                ).draw()

            if answer_box is not None:
                answer_box.text = typed_math
                answer_box.draw()

            win.flip()

        send_marker(f"{trial_tag}_math_offset")
        math_offset_ts = lsl_clock.getTime()

        typed_math_clean = typed_math.strip()
        math_correct = _safe_float_equal(typed_math_clean, ans) or (typed_math_clean == ans)

        # 3) Recall single letter (every trial) - correctness not used for feedback
        recall_single_typed, recall_single_first_key_ts, recall_single_submit_ts, recall_single_ts = _collect_text_until_enter(
            win=win,
            defaultKeyboard=defaultKeyboard,
            prompt_stim=recall_single_prompt,
            answer_box=answer_box,
            send_marker=send_marker,
            lsl_clock=lsl_clock,
            marker_prefix=f"{trial_tag}_recall_single",
            allow_empty=False,
        )
        if recall_single_typed is None:
            send_marker("experiment_abort")
            if record_webcam:
                stop_webcam_recording()
            thisExp.abort()
            core.quit()

        recall_single_clean = str(recall_single_typed).strip().lower()
        letter_clean = str(letter).strip().lower()
        recall_single_correct = (recall_single_clean == letter_clean)

        # 4) Sequence recall input after trial 5 and 10 (input belongs to Segment A)
        seq_event = None  # store sequence recall metadata if happens
        if i in [5, 10]:
            if i == 5:
                seq_letters = presented_letters[0:5]
                seq_tag = f"{block_tag}_seqrecall_01_05"
                recall_seq_prompt.text = "Type the letters you saw in trials 1–5 in order, then press ENTER."
            else:
                seq_letters = presented_letters[5:10]
                seq_tag = f"{block_tag}_seqrecall_06_10"
                recall_seq_prompt.text = "Type the letters you saw in trials 6–10 in order, then press ENTER."

            correct_seq = "".join([str(x).strip() for x in seq_letters])
            correct_norm = _normalize_seq(correct_seq)

            typed_seq, seq_first_key_ts, seq_submit_ts, seq_ts = _collect_text_until_enter(
                win=win,
                defaultKeyboard=defaultKeyboard,
                prompt_stim=recall_seq_prompt,
                answer_box=answer_box,
                send_marker=send_marker,
                lsl_clock=lsl_clock,
                marker_prefix=seq_tag,
                allow_empty=False,
            )
            if typed_seq is None:
                send_marker("experiment_abort")
                if record_webcam:
                    stop_webcam_recording()
                thisExp.abort()
                core.quit()

            typed_norm = _normalize_seq(typed_seq)
            seq_is_correct = int(typed_norm == correct_norm)

            # Store for feedback + logging
            seq_event = {
                "seq_tag": seq_tag,
                "correct_seq": correct_seq,
                "typed_seq": str(typed_seq),
                "seq_is_correct": seq_is_correct,
                "seq_ts": seq_ts,
                "seq_first_key_ts": seq_first_key_ts,
                "seq_submit_ts": seq_submit_ts,
            }

        # End Segment A video (input portion ends here)
        if record_webcam:
            send_marker(f"{trial_tag}_task_video_offset")
            stop_webcam_recording()

        # ==========================
        # Segment B video: FEEDBACK 
        # ==========================
        feedback_video_path = None
        if record_webcam:
            feedback_video_path = os.path.join(participant_dir, f"{expName}_{date_str}_{trial_tag}_feedback.mp4")
            start_webcam_recording(feedback_video_path)
            send_marker(f"{trial_tag}_feedback_video_onset")



        # ---- Combined feedback page: math answer + (optional) sequence ----
        lines = []

        # Math feedback
        if math_correct:
            lines.append("Math: Correct!")
        else:
            lines.append(f"Math: Incorrect. Correct answer: {ans}")

        # Sequence feedback (only after trial 5/10)
        seq_is_correct = None
        if seq_event is not None:
            seq_is_correct = bool(seq_event["seq_is_correct"])
            if seq_is_correct:
                lines.append("Sequence: Correct!")
            else:
                lines.append(f"Sequence: Incorrect. Correct sequence: {seq_event['correct_seq']}")

        fb_msg = "\n".join(lines)

        fb_on, fb_off = _show_feedback_screen(
            win=win,
            defaultKeyboard=defaultKeyboard,
            send_marker=send_marker,
            lsl_clock=lsl_clock,
            feedback_text_stim=feedback_text_stim,
            msg=fb_msg,
            feedback_sec=feedback_sec,
            marker_prefix=f"{trial_tag}_combined_feedback",
        )
        if fb_on is None:
            send_marker("experiment_abort")
            if record_webcam:
                stop_webcam_recording()
            thisExp.abort()
            core.quit()


        if record_webcam:
            send_marker(f"{trial_tag}_feedback_video_offset")
            stop_webcam_recording()

        # ---- NASA (per trial) ----
        nasa_results = run_nasa_once(
            win=win,
            level="Baseline",
            trial_label=trial_tag,
            stims=stims,
            defaultKeyboard=defaultKeyboard,
            thisExp=thisExp,
        )


        # ==========================
        # Logging rows
        # ==========================

        # (A) Log sequence recall row (if happened) — now includes feedback timestamps
        if seq_event is not None:
            thisExp.addData("phase", "baseline_seq_recall")
            # thisExp.addData("baseline_block", block_tag)
            thisExp.addData("baseline_trial_index", i)
            thisExp.addData("seq_recall_tag", seq_event["seq_tag"])
            thisExp.addData("seq_correct_letters", seq_event["correct_seq"])
            thisExp.addData("seq_typed", seq_event["typed_seq"])
            thisExp.addData("seq_is_correct", seq_event["seq_is_correct"])

            thisExp.addData("seq_onset_ts", seq_event["seq_ts"]["onset_ts"])
            thisExp.addData("seq_offset_ts", seq_event["seq_ts"]["offset_ts"])
            thisExp.addData("seq_first_key_ts", seq_event["seq_first_key_ts"])
            thisExp.addData("seq_submit_ts", seq_event["seq_submit_ts"])

            # thisExp.addData("seq_feedback_onset_ts", seq_fb_on)
            # thisExp.addData("seq_feedback_offset_ts", seq_fb_off)

            thisExp.addData("task_video_path", task_video_path)
            thisExp.addData("feedback_video_path", feedback_video_path)
            thisExp.nextEntry()

        # (B) Log main trial row
        thisExp.addData("phase", "baseline_trial")
        thisExp.addData("baseline_block", block_tag)
        thisExp.addData("baseline_trial_index", i)

        thisExp.addData("question_img", q_img_raw)
        thisExp.addData("question_img_resolved", q_img)
        thisExp.addData("answer", ans)
        thisExp.addData("typed_math", typed_math_clean)
        thisExp.addData("math_is_correct", int(math_correct))
        thisExp.addData("math_enter_submitted", int(submitted))

        thisExp.addData("letter", letter)

        # letter recall (recorded, not used for feedback)
        thisExp.addData("recall_single_typed", recall_single_clean)
        thisExp.addData("recall_single_is_correct", int(recall_single_correct))

        # timestamps (task)
        thisExp.addData("letter_onset_ts", letter_onset_ts)
        thisExp.addData("letter_offset_ts", letter_offset_ts)
        thisExp.addData("math_onset_ts", math_onset_ts)
        thisExp.addData("math_offset_ts", math_offset_ts)
        thisExp.addData("math_first_key_ts", first_math_key_ts)
        thisExp.addData("math_submit_ts", math_submit_ts)

        thisExp.addData("recall_single_onset_ts", recall_single_ts["onset_ts"])
        thisExp.addData("recall_single_offset_ts", recall_single_ts["offset_ts"])
        thisExp.addData("recall_single_first_key_ts", recall_single_first_key_ts)
        thisExp.addData("recall_single_submit_ts", recall_single_submit_ts)

        # feedback timestamps (math feedback after recall_single)
        # thisExp.addData("math_feedback_onset_ts", fb1_on)
        # thisExp.addData("math_feedback_offset_ts", fb1_off)


        thisExp.addData("feedback_onset_ts", fb_on)
        thisExp.addData("feedback_offset_ts", fb_off)

        # video paths
        thisExp.addData("task_video_path", task_video_path)
        thisExp.addData("feedback_video_path", feedback_video_path)

        # NASA fields
        for k, v in nasa_results.items():
            thisExp.addData(k, v)

        thisExp.nextEntry()

    # ---- Block offset ----
    send_marker(f"{block_tag}_offset")
    block_offset_ts = lsl_clock.getTime()

    # # ---- Summary row ----
    # thisExp.addData("phase", "baseline_summary")
    # thisExp.addData("baseline_block", block_tag)
    # thisExp.addData("baseline_instr_onset_ts", instr_onset_ts)
    # thisExp.addData("baseline_instr_offset_ts", instr_offset_ts)
    # thisExp.addData("baseline_onset_ts", block_onset_ts)
    # thisExp.addData("baseline_offset_ts", block_offset_ts)
    # thisExp.addData("baseline_trials", n_trials)
    # thisExp.addData("baseline_letters_presented", "".join([str(x).strip() for x in presented_letters]))
    # thisExp.nextEntry()

    thisExp.saveAsWideText(thisExp.dataFileName + ".csv")
    thisExp.saveAsPickle(thisExp.dataFileName)
    # thisExp.abort()



    # return {
    #     "baseline_trials": n_trials,
    #     "baseline_letters_presented": presented_letters,
    #     "baseline_onset_ts": block_onset_ts,
    #     "baseline_offset_ts": block_offset_ts,
    # }
