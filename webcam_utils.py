#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Webcam recording helpers for the static problem experiment.
"""

import cv2
import threading

# --------------------------------------------------------------
# Webcam recording globals
# --------------------------------------------------------------
webcam_cap = None
webcam_out = None
webcam_recording = False
webcam_thread = None


def webcam_record_loop():
    """
    Background loop that continuously grabs frames from the webcam
    and writes them to the video file while `webcam_recording` is True.
    """
    global webcam_cap, webcam_out, webcam_recording

    while webcam_recording:
        if webcam_cap is None:
            break
        ret, frame = webcam_cap.read()
        if not ret:
            break
        # If you want to mirror the image, uncomment:
        # frame = cv2.flip(frame, 1)
        webcam_out.write(frame)

    print("Webcam recording loop stopped.")


def start_webcam_recording(video_filename: str):
    """
    Initialize the webcam and video writer, then start a background thread
    that continuously records frames until stop_webcam_recording() is called.
    """
    global webcam_cap, webcam_out, webcam_recording, webcam_thread

    # Open default camera (index 0)
    webcam_cap = cv2.VideoCapture(0)
    if not webcam_cap.isOpened():
        print("WARNING: Could not open webcam. No video will be recorded.")
        webcam_cap = None
        return

    # Get frame size from camera
    frame_width = int(webcam_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(webcam_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define codec and create VideoWriter for MP4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    webcam_out = cv2.VideoWriter(
        video_filename,
        fourcc,
        30.0,  # FPS
        (frame_width, frame_height)
    )

    if not webcam_out.isOpened():
        print("WARNING: Could not open VideoWriter. No video will be recorded.")
        webcam_out = None
        webcam_cap.release()
        webcam_cap = None
        return

    webcam_recording = True
    webcam_thread = threading.Thread(target=webcam_record_loop, daemon=True)
    webcam_thread.start()
    print(f"Webcam recording started. Saving to {video_filename}")


def stop_webcam_recording():
    """
    Stop the background recording loop and release camera and writer.
    Safe to call multiple times; if nothing is recording, it does nothing.
    """
    global webcam_cap, webcam_out, webcam_recording, webcam_thread

    if not webcam_recording and webcam_cap is None and webcam_out is None:
        return  # Nothing to stop

    webcam_recording = False

    # Wait for the background thread to finish (if it exists)
    if webcam_thread is not None:
        webcam_thread.join(timeout=2.0)

    # Release camera
    if webcam_cap is not None:
        webcam_cap.release()
        webcam_cap = None

    # Release video writer
    if webcam_out is not None:
        webcam_out.release()
        webcam_out = None

    print("Webcam recording stopped and resources released.")
