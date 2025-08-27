# state.py

# --- Global Variables ---
SOUND_AMPLITUDE = 0     # Stores latest calculated average amplitude
AUDIO_CHEAT = 0         # Flag: 1 when suspicious sound detected

# --- Configurable Parameters ---
CALLBACKS_PER_SECOND = 38   # How many audio callbacks per second
SUS_FINDING_FREQUENCY = 2   # How many times per second we check suspicion
SOUND_AMPLITUDE_THRESHOLD = 20  # Threshold for "suspicious" loudness

# --- Derived Parameters ---
FRAMES_COUNT = CALLBACKS_PER_SECOND // SUS_FINDING_FREQUENCY

# --- Buffers & Counters ---
AMPLITUDE_LIST = [0] * FRAMES_COUNT
SUS_COUNT = 0
count = 0
