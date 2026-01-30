import numpy as np
import pandas as pd
import streamlit as st

def generate_mock_eeg(duration_sec=2, sampling_rate=256, is_guilty=False):
    """
    Generates a synthetic EEG signal.
    If is_guilty=True, inserts a P300 spike (a positive deflection around 300ms).
    """
    time = np.linspace(0, duration_sec, duration_sec * sampling_rate)
    
    # 1. Background Brain Noise (random noise)
    noise = np.random.normal(0, 5, len(time))
    
    # 2. Alpha Waves (8-12 Hz - resting state)
    alpha = 5 * np.sin(2 * np.pi * 10 * time)
    
    signal = noise + alpha

    # 3. Insert The "Guilty" Signal (P300)
    # P300 is a positive peak occurring 300-500ms after stimulus
    if is_guilty:
        # Gaussian spike centered at 0.4s (400ms)
        p300_center = 0.4
        p300_width = 0.05
        p300_amplitude = 25  # Significant spike
        p300_wave = p300_amplitude * np.exp(-0.5 * ((time - p300_center) / p300_width)**2)
        signal += p300_wave
        
    return time, signal

def get_stimulus_data():
    """Returns a list of mock stimuli events."""
    return [
        {"id": 1, "type": "Neutral", "text": "A picture of a flower", "guilty_response": False},
        {"id": 2, "type": "Probe", "text": "A picture of the murder weapon (Knife)", "guilty_response": True},
        {"id": 3, "type": "Target", "text": "A picture of the victim's house", "guilty_response": True},
        {"id": 4, "type": "Neutral", "text": "A picture of a car", "guilty_response": False},
    ]