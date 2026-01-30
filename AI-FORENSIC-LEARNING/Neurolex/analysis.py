import numpy as np

def analyze_signal(time, signal):
    """
    Analyzes the EEG signal to detect P300 features.
    Returns a dictionary of technical findings.
    """
    # Define the P300 window (300ms to 600ms)
    # Assuming 256 Hz sampling rate
    idx_start = int(0.3 * 256)
    idx_end = int(0.6 * 256)
    
    window_data = signal[idx_start:idx_end]
    
    # Feature 1: Max Amplitude in window
    max_amp = np.max(window_data)
    
    # Feature 2: Latency (time of max amp)
    max_idx = np.argmax(window_data)
    latency_ms = (idx_start + max_idx) / 256 * 1000
    
    # Feature 3: Signal-to-Noise Ratio (simplified)
    baseline_noise = np.std(signal[:idx_start])
    snr = max_amp / (baseline_noise + 1e-6) # avoid div by zero
    
    # Determination Logic
    # In real forensic science, >15uV in P300 window is suspicious
    has_experiential_knowledge = max_amp > 15 and snr > 1.5
    
    return {
        "amplitude_uv": round(max_amp, 2),
        "latency_ms": round(latency_ms, 2),
        "snr": round(snr, 2),
        "detection": has_experiential_knowledge
    }