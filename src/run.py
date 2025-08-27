# run.py

import numpy as np
import sounddevice as sd
import state   # import shared state variables

# --- Step 1: RMS Calculation ---
def calculate_rms(indata):
    """Calculate Root Mean Square (RMS) amplitude (volume)."""
    return np.sqrt(np.mean(indata**2)) * 1000


# --- Step 2: Callback Function ---
def print_sound(indata, outdata, frames, time, status):
    """Runs automatically when microphone provides new audio data."""
    rms_amplitude = calculate_rms(indata)

    # Update amplitude buffer
    state.AMPLITUDE_LIST.append(rms_amplitude)
    state.AMPLITUDE_LIST.pop(0)

    state.count += 1

    # Once we’ve collected enough frames → check loudness
    if state.count >= state.FRAMES_COUNT:
        avg_amp = sum(state.AMPLITUDE_LIST) / state.FRAMES_COUNT
        state.SOUND_AMPLITUDE = avg_amp

        if avg_amp > state.SOUND_AMPLITUDE_THRESHOLD:
            state.SUS_COUNT += 1
        else:
            state.SUS_COUNT = 0
            state.AUDIO_CHEAT = 0

        # If consecutive suspicious detections → flag cheating
        if state.SUS_COUNT >= 2:
            state.AUDIO_CHEAT = 1
            print("⚠️ Suspicious sound detected! (Possible talking/cheating)")


# --- Step 3: Sound Stream ---
def sound():
    """Open continuous audio stream from microphone."""
    with sd.Stream(callback=print_sound):
        print("🎤 Listening for suspicious sounds... (Ctrl+C to stop)")
        sd.sleep(-1)


# --- Main Execution ---
if __name__ == "__main__":
    sound()
