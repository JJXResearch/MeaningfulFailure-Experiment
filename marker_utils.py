#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LSL + OSC marker utilities for the static problem experiment.
"""

from psychopy import core
from pylsl import StreamInfo, StreamOutlet
from pythonosc import udp_client

# --------------------------------------------------------------
# LSL Marker Stream Setup
# --------------------------------------------------------------
info = StreamInfo(
    name='psychopy_events',
    type='Markers',
    channel_count=1,
    channel_format='string',
    source_id='static_problems_01'
)
outlet = StreamOutlet(info)
lsl_clock = core.MonotonicClock()

# --------------------------------------------------------------
# OSC (for MuseLab / other EEG recorder) Setup
# --------------------------------------------------------------
OSC_IP = "127.0.0.1"   # set up your IP
OSC_PORT = 5000        # port

try:
    osc_client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)
    print(f"OSC client initialized, sending to {OSC_IP}:{OSC_PORT}")
except Exception as e:
    print(f"Could not initialize OSC client: {e}")
    osc_client = None


def send_marker(text: str):
    """
    Send an LSL marker with a timestamp and (optionally) via OSC.
    Logic identical to original script.
    """
    outlet.push_sample([text])
    ts = lsl_clock.getTime()
    print(f"Marker: {text} @ {ts:.3f}s (LSL)")

    # OSC marker (optional, only if osc_client is available)
    if osc_client is not None:
        osc_client.send_message("/psychopy_event", text)
