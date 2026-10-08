# rest_utils.py
# -*- coding: utf-8 -*-

from psychopy import core, event, visual

def run_rest_baseline(
    win,
    duration_sec,
    stims,
    participant_dir,
    expName,
    date_str,
    send_marker,
    lsl_clock,
    start_webcam_recording,
    stop_webcam_recording,
    defaultKeyboard,
    thisExp=None,
    session_tag="rest",
    prompt_title="Rest for 3 min",
    prompt_hint="[press space to start]"
):
    """
    Rest baseline with a prompt screen:
      Stage A: show prompt and wait for SPACE
      Stage B: record webcam + send markers + show fixation for duration_sec seconds

    Returns:
      dict with prompt_onset/offset, rest_onset/offset timestamps and video path.
    """

    # --- Stimuli: prompt page ---
    # Prefer to reuse your stims dict. If not present, create them locally.
    rest_prompt_title = stims.get("rest_prompt_title", None)
    rest_prompt_hint  = stims.get("rest_prompt_hint", None)
    rest_fix          = stims.get("rest_fix", None)

    if rest_prompt_title is None:
        rest_prompt_title = visual.TextStim(
            win, text=prompt_title, height=0.06, color="white", pos=(0, 0.05)
        )
    else:
        rest_prompt_title.text = prompt_title

    if rest_prompt_hint is None:
        rest_prompt_hint = visual.TextStim(
            win, text=prompt_hint, height=0.04, color="white", pos=(0, -0.35)
        )
    else:
        rest_prompt_hint.text = prompt_hint

    if rest_fix is None:
        rest_fix = visual.TextStim(
            win, text="+", height=0.12, color="white", pos=(0, 0)
        )

    # ----------------------------
    # Stage A: Prompt screen
    # ----------------------------
    send_marker(f"{session_tag}_prompt_onset")
    prompt_onset_ts = lsl_clock.getTime()

    while True:
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            if thisExp is not None:
                thisExp.abort()
            core.quit()

        # Use event.getKeys for SPACE (consistent with your main script)
        keys = event.getKeys()
        if "space" in keys:
            break

        rest_prompt_title.draw()
        rest_prompt_hint.draw()
        win.flip()

    send_marker(f"{session_tag}_prompt_offset")
    prompt_offset_ts = lsl_clock.getTime()

    # ----------------------------
    # Stage B: Real rest (fixation)
    # ----------------------------
    rest_label = f"{session_tag}"
    video_path = f"{participant_dir}/{expName}_{date_str}_{rest_label}.mp4"

    # Start recording and send rest onset marker AFTER space
    start_webcam_recording(video_path)

    send_marker(f"{rest_label}_onset")
    rest_onset_ts = lsl_clock.getTime()

    timer = core.Clock()
    while timer.getTime() < float(duration_sec):
        if defaultKeyboard.getKeys(keyList=["escape"]):
            send_marker("experiment_abort")
            if thisExp is not None:
                thisExp.abort()
            stop_webcam_recording()
            core.quit()

        rest_fix.draw()
        win.flip()

    send_marker(f"{rest_label}_offset")
    rest_offset_ts = lsl_clock.getTime()

    stop_webcam_recording()

    return {
        "rest_prompt_onset_ts": prompt_onset_ts,
        "rest_prompt_offset_ts": prompt_offset_ts,
        "rest_video_path": video_path,
        "rest_onset_ts": rest_onset_ts,
        "rest_offset_ts": rest_offset_ts,
        "rest_duration_sec": float(duration_sec),
    }
