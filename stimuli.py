#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create all PsychoPy stimulus objects (texts, images, sliders, etc.).
"""

from psychopy import visual
from psychopy.visual import TextBox2


def create_all_stimuli(win):
    """
    Create all stimuli and return them in a dict.
    The parameters are identical to the original script.
    """



    # Rest fixation
    rest_fix = visual.TextStim(win, text="+", height=0.12, color="white", pos=(0, 0))

    # WM letter text
    wm_letter_text = visual.TextStim(win, text="", height=0.2, color="white", pos=(0, 0))

    # WM recall prompt
    wm_recall_prompt = visual.TextStim(
        win, text="Now type the letter sequence you remember, then press ENTER.",
        height=0.04, color="white", pos=(0, 0.2), wrapWidth=1.2
    )

    # # add into stims dict:
    # stims["rest_fix"] = rest_fix
    # stims["wm_letter_text"] = wm_letter_text
    # stims["wm_recall_prompt"] = wm_recall_prompt


    # Instructions
    instr = visual.TextStim(
        win,
        text=(
            "You will see several static problems.\n\n"
            "For each problem:\n"
            "  • Solve it.\n"
            "  • Type your answer.\n"
            "  • Press ENTER to submit.\n\n"
            "Press SPACE to start."
        ),
        height=0.03,
        wrapWidth=0.9
    )

    img_stim = visual.ImageStim(
        win,
        size=(0.9, 0.5),
        pos=(0, 0.15)
    )

    prompt_text = visual.TextStim(
        win,
        text="Type your answer and press ENTER:",
        pos=(0, -0.15),
        height=0.035
    )

    feedback_text = visual.TextStim(
        win,
        text="",
        pos=(0, 0),
        height=0.045,
        color="yellow"
    )

    # answer_box = visual.TextStim(
    #     win,
    #     text="",
    #     pos=(0, 0),
    #     height=0.06,
    #     wrapWidth=0.9,
    #     color="white"
    # )


    answer_box = TextBox2(
        win,
        text="",
        pos=(0, -0.25),
        letterHeight=0.05,
        size=(1.2, 0.3),   
        color="white",
        borderColor=None,
        alignment='center'
    )


    timer_text = visual.TextStim(
        win,
        text="",
        pos=(0, 0.45),
        height=0.035,
        color="white"
    )

    # ---------- Justification ----------
    justification_prompt = visual.TextStim(
        win,
        text="Please insert your justification and press ENTER:",
        pos=(0, 0.3),
        height=0.035,
        wrapWidth=0.9,
        color="white"
    )

    # justification_box = visual.TextStim(
    #     win,
    #     text="",
    #     pos=(0, -0.15),
    #     height=0.05,
    #     wrapWidth=1.2,
    #     color="white"
    # )
    
    justification_box = TextBox2(
        win,
        text="",
        pos=(0, -0.1),
        letterHeight=0.05,
        size=(1.2, 0.3),   
        color="white",
        borderColor=None
    )

    # ---------- NASA-TLX ----------
    # Top instruction (optional, can keep it short)
    nasa_instr = visual.TextStim(
        win,
        name="nasa_instr",
        text="Please rate this task from 0 (Very Low) to 20 (Very High):",
        font="Open Sans",
        pos=(0, 0.45),
        height=0.03,
        wrapWidth=1.2,
        ori=0.0,
        color="yellow",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )





    ticks = list(range(0, 21))                     
    labels = [str(i) if i % 2 == 0 else "" for i in ticks] 


    # Mental demand
    mental_text = visual.TextStim(
        win=win,
        name="md_text",
        text="How mentally demanding was this task?",
        font="Open Sans",
        pos=(0, 0.32),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )

    mental_slider = visual.Slider(
        win=win,
        name="mental_demand",
        startValue=10,
        size=(0.9, 0.02),
        pos=(0, 0.24),
        units=win.units,
        ticks=ticks,
        labels=labels,
        granularity=1,                    
        style="rating",
        styleTweaks=("triangleMarker",),   
        labelColor="white",
        markerColor="white",
        lineColor="white",
        colorSpace="rgb",
        font="Open Sans",
        labelHeight=0.02,
        flip=False,
        ori=0.0,
        readOnly=False,
    )


    # Performance
    performance_text = visual.TextStim(
        win=win,
        name="p_text",
        text="How successful were you in accomplishing the task?",
        font="Open Sans",
        pos=(0, 0.11),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )
    performance_slider = visual.Slider(
        win=win,
        name="performance",
        startValue=10,
        size=(0.9, 0.02),
        pos=(0, 0.03),
        units=win.units,
        ticks=ticks,
        labels=labels,
        granularity=1,
        style="rating",
        styleTweaks=("triangleMarker",),
        opacity=None,
        labelColor="white",
        markerColor="white",
        lineColor="white",
        colorSpace="rgb",
        font="Open Sans",
        labelHeight=0.02,
        flip=False,
        ori=0.0,
        readOnly=False,
    )

    # Effort
    effort_text = visual.TextStim(
        win=win,
        name="e_text",
        text="How hard did you have to work to accomplish your performance?",
        font="Open Sans",
        pos=(0, -0.10),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )
    effort_slider = visual.Slider(
        win=win,
        name="effort",
        startValue=10,
        size=(0.9, 0.02),
        pos=(0, -0.18),
        units=win.units,
        ticks=ticks,
        labels=labels,
        granularity=1,
        style="rating",
        styleTweaks=("triangleMarker",),
        opacity=None,
        labelColor="white",
        markerColor="white",
        lineColor="white",
        colorSpace="rgb",
        font="Open Sans",
        labelHeight=0.02,
        flip=False,
        ori=0.0,
        readOnly=False,
    )

    # Frustration
    frustration_text = visual.TextStim(
        win=win,
        name="f_text",
        text="How frustrated, irritated, or stressed did you feel during the task?",
        font="Open Sans",
        pos=(0, -0.31),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )
    frustration_slider = visual.Slider(
        win=win,
        name="frustration",
        startValue=10,
        size=(0.9, 0.02),
        pos=(0, -0.39),
        units=win.units,
         ticks=ticks,
        labels=labels,
        granularity=1,
        style="rating",
        styleTweaks=("triangleMarker",),
        opacity=None,
        labelColor="white",
        markerColor="white",
        lineColor="white",
        colorSpace="rgb",
        font="Open Sans",
        labelHeight=0.02,
        flip=False,
        ori=0.0,
        readOnly=False,
    )

    # “Press spacebar when finished”
    nasa_continue_text = visual.TextStim(
        win=win,
        name="nasa_proceed",
        text="[ press spacebar when you are finished ]",
        font="Open Sans",
        pos=(0, -0.47),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="yellow",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
    )


    # End screen text (created here for convenience)

    end_text = visual.TextStim(
        win,
        text="You have completed all problems.\n\nThank you.",
        height=0.04
    )

    return {
        "instr": instr,
        "img_stim": img_stim,
        "prompt_text": prompt_text,
        "feedback_text": feedback_text,
        "answer_box": answer_box,
        "timer_text": timer_text,
        "justification_prompt": justification_prompt,
        "justification_box": justification_box,
        "nasa_instr": nasa_instr,
        "mental_text": mental_text,
        "performance_text": performance_text,
        "effort_text": effort_text,
        "frustration_text": frustration_text,
        "mental_slider": mental_slider,
        "performance_slider": performance_slider,
        "effort_slider": effort_slider,
        "frustration_slider": frustration_slider,
        "nasa_continue_text": nasa_continue_text,
        "end_text": end_text,
        "rest_fix": rest_fix,
        "wm_letter_text": wm_letter_text,
        "wm_recall_prompt": wm_recall_prompt,
    }
