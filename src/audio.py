import time
from collections import deque

import numpy as np
import sounddevice as sd

# ====== Tunable settings ======
CHECK_WINDOW_SEC = 1.0          # how many seconds to average over
CONSECUTIVE_REQUIRED = 2        # how many checks in a row before we say "sus"
THRESHOLD_FACTOR = 2.0          # threshold = baseline * this factor
# ==============================

# Get a reasonable default samplerate from your input device
try:
    SAMPLERATE = int(sd.query_devices(kind='input')['default_samplerate'])
except Exception:
    SAMPLERATE = 16000  # fallback that works on most systems

BLOCKSIZE = 1024  # audio frames processed per callback (tweak if needed)
WINDOW_LEN = max(1, int(CHECK_WINDOW_SEC * SAMPLERATE / BLOCKSIZE))

amplitudes = deque([0.0] * WINDOW_LEN, maxlen=WINDOW_LEN)
sus_count = 0
AUDIO_CHEAT = False
THRESHOLD = 999999.0  # set after calibration

def rms(x: np.ndarray) -> float:
    """Root-mean-square amplitude, scaled for readability."""
    return float(np.sqrt(np.mean(np.square(x))) * 1000.0)

def calibrate(seconds: int = 3) -> float:
    """Measure ambient noise for a few seconds while you're quiet."""
    print(f"\nCalibrating for {seconds}s... stay quiet.")
    data = sd.rec(int(seconds * SAMPLERATE),
                  samplerate=SAMPLERATE,
                  channels=1,
                  dtype="float32")
    sd.wait()
    base = rms(data[:, 0])
    print(f"Baseline noise: {base:.1f}")
    return base

def audio_callback(indata, frames, time_info, status):
    """Runs automatically for each audio chunk from the mic."""
    global sus_count, AUDIO_CHEAT

    if status:
        # Non-fatal driver notes; we ignore them here
        pass

    amp = rms(indata[:, 0])
    amplitudes.append(amp)
    avg_amp = float(np.mean(amplitudes))

    # Decide if current average is suspicious
    if avg_amp > THRESHOLD:
        sus_count += 1
    else:
        sus_count = 0

    AUDIO_CHEAT = sus_count >= CONSECUTIVE_REQUIRED
    if AUDIO_CHEAT:
        print(f"Sus... avg_amp={avg_amp:.1f}  (threshold={THRESHOLD:.1f})")

def main():
    global THRESHOLD
    input("Press Enter when you're ready to calibrate (be quiet during this)...")
    baseline = calibrate(3)
    THRESHOLD = baseline * THRESHOLD_FACTOR
    print(f"Threshold set to {THRESHOLD:.1f}  (factor {THRESHOLD_FACTOR}× baseline)\n")

    print("Monitoring… Speak or make noise to trigger 'Sus...'. Press Ctrl+C to stop.")
    with sd.InputStream(channels=1,
                        samplerate=SAMPLERATE,
                        blocksize=BLOCKSIZE,
                        callback=audio_callback):
        try:
            while True:
                time.sleep(1)  # keep main thread alive
        except KeyboardInterrupt:
            print("\nStopped.")

if __name__ == "__main__":
    main()
