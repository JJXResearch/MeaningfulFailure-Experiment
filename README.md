# MeaningfulFailure-Experiment

A **PsychoPy-based experimental task platform** for research on problem solving and productive failure in engineering education. The application presents cognitive and engineering problem-solving tasks, records behavioral responses and subjective workload, captures webcam video, and broadcasts experimental event markers to support alignment with physiological recordings acquired by external systems.

> **Scope:** This repository contains experimental task presentation and data-logging software. It does **not** independently record EEG or heart-rate signals, perform physiological signal analysis, or establish whether a complete productive-failure instructional intervention has taken place.

## Features

- **Configurable statics problems:** Randomized image-based questions at three levels (`Closed_ended_easy`, `Closed_ended_moderate`, and `Open_ended`), with answers and time limits loaded from Excel.
- **Behavioral measures:** Typed responses, response times, correctness, and written justifications within the task flow.
- **Letter–Math task:** Letter memorization and math problem solving, with response and recall stages and associated feedback.
- **Workload ratings:** Four NASA-TLX-style ratings—mental demand, performance, effort, and frustration—collected within the experiment. This is **not** the complete six-dimension NASA-TLX instrument.
- **Event markers:** Experimental events are published through Lab Streaming Layer (LSL), with an additional OSC output for compatible external recording software.
- **Webcam recording:** Task-stage video capture through OpenCV.
- **Optional resting baseline:** A fixation/rest procedure is implemented but currently commented out in the main script.

## Experimental workflow

The current `run_experiment.py` configuration:

1. Loads the question pools and trial counts from Excel files and creates a randomized statics trial sequence.
2. Prompts for a participant identifier and creates an output folder.
3. Runs the **Letter–Math** module (currently configured for **one trial**, despite a ten-trial prompt string).
4. Presents the statics-task instructions and runs the selected problems, including answer entry, feedback, and workload prompts.
5. Saves participant-level experiment records and associated videos in `data/`.

The resting baseline is implemented in `rest_utils.py` but **disabled** in the current entry script. To use it, review and enable the corresponding code block in `run_experiment.py`.

For open-ended statics problems, the script contains logic for an additional workload prompt at five-minute intervals, excluding the questionnaire time from effective answer time.

## Repository structure

```text
.
├── run_experiment.py       # Main experiment entry point
├── config.py               # File paths and experiment defaults
├── question_utils.py       # Question loading, sampling, and trial construction
├── letter_math_utils.py    # Letter–Math task
├── rest_utils.py           # Optional resting baseline
├── stimuli.py              # PsychoPy visual elements
├── marker_utils.py         # LSL and OSC event markers
├── webcam_utils.py         # Webcam video recording
├── questions/              # Statics question and trial configuration spreadsheets
├── Static_problem/         # Statics problem images
├── math_questions/         # Letter–Math spreadsheets and supporting material
├── Math_Stimuli/           # Math-task image stimuli
└── data/                   # Generated participant records (do not publish)
```

## Requirements

- Python environment compatible with **PsychoPy** (use a PsychoPy-supported Python version)
- A graphical desktop environment and keyboard
- A webcam for optional video recording
- The experiment's Excel workbooks and image stimuli

Python packages used by the code include:

```text
psychopy
numpy
pandas
openpyxl
opencv-python
pylsl
python-osc
```

**Note:** These are code-level dependencies, not a tested or pinned environment specification. PsychoPy and pylsl may require platform-specific installation steps. An external EEG or heart-rate acquisition application/device is needed for physiological recordings; this program only emits synchronization markers.

## Getting started

1. Clone or download the repository and enter its root directory.
2. Create an appropriate Python/PsychoPy environment and install the dependencies above.
3. Verify the paths and workbook contents in `config.py`:
   - `questions/ques_trials.xlsx`: `level`, `n_trials`
   - `questions/questions.xlsx`: `Prompts`, `Answers`, optional `TimeLimit`
4. Ensure question image paths in the spreadsheet resolve to existing files.
5. Review the experimental settings in `run_experiment.py`, particularly `n_trials=1` for the Letter–Math task, webcam capture, and the disabled resting baseline.
6. If using external acquisition software, configure the LSL/OSC receiving setup. OSC is currently directed to `127.0.0.1:5000` in `marker_utils.py`.
7. Start the application from the project root:

   ```powershell
   python run_experiment.py
   ```

Test the entire workflow with **synthetic participant identifiers** before collecting research data. Hardware integration, timing precision, and cross-device synchronization should be validated on the actual laboratory setup.

## Recorded outputs

The experiment organizes output under `data/<participant_id>/`. Depending on which phases are enabled, outputs include PsychoPy experiment data files and stage-based MP4 video recordings. Logged task variables include responses, accuracy, reaction time, and workload ratings; event names are emitted over the LSL marker stream and optionally OSC.

**Important distinction:** An LSL marker stream is not an EEG recording. Physiological signals and their timestamps must be captured separately by a compatible acquisition system. The present webcam utility does not provide independent per-frame synchronization timestamps.

## Research data and privacy

This project is designed for research involving human participants. **Do not commit identifiable participant records, webcam videos, physiological data, consent forms, or other restricted study materials to a public repository.** Check stimulus copyright and institutional/IRB permissions before distributing study materials. Use a participant-safe demonstration dataset only when sharing is authorized.

A suggested `.gitignore` entry is:

```gitignore
data/
__pycache__/
*.pyc
.venv/
venv/
.env
.idea/
```

## Research context

The software supports investigation of problem-solving performance, subjective workload, and event-aligned physiological responses in an educational setting. The specific instructional conditions and claims about *productive failure* should be described and evaluated in the associated study protocol and publications, rather than inferred from the program alone.

## Project status

Research prototype. Several workflow settings are currently experiment-specific, including the single Letter–Math trial and optional resting baseline. No automated hardware integration or timing-validation results are provided in this repository.

## License and citation

No license is specified here. If you intend others to reuse or adapt this software, add an appropriate `LICENSE` file. Citation details can be added after a related publication or software release is available.
