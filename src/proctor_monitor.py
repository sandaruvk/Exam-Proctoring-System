# proctor_monitor.py
# Monitors both suspicious audio and head movements

import threading
import numpy as np
import sounddevice as sd
import cv2
import mediapipe as mp
import math
import time

# -----------------------
# Shared state variables
# -----------------------
class State:
    SOUND_AMPLITUDE = 0
    AUDIO_CHEAT = 0
    AMPLITUDE_LIST = []
    SUS_COUNT = 0
    COUNT = 0

    HEAD_SUS_COUNT = 0
    HEAD_CHEAT = 0

# Initialize state
state = State()

# Audio parameters
CALLBACKS_PER_SECOND = 38
SUS_FINDING_FREQUENCY = 2
SOUND_AMPLITUDE_THRESHOLD = 20
FRAMES_COUNT = CALLBACKS_PER_SECOND // SUS_FINDING_FREQUENCY
state.AMPLITUDE_LIST = [0] * FRAMES_COUNT

# Head pose parameters
HEAD_TURN_THRESHOLD = 15  # degrees
SUS_LOOK_COUNT_THRESHOLD = 2

# -----------------------
# Audio monitoring
# -----------------------
def calculate_rms(indata):
    """Calculate RMS amplitude of the audio."""
    return np.sqrt(np.mean(indata**2)) * 1000

def audio_callback(indata, outdata, frames, time_info, status):
    rms_amplitude = calculate_rms(indata)

    # Update amplitude buffer
    state.AMPLITUDE_LIST.append(rms_amplitude)
    state.AMPLITUDE_LIST.pop(0)

    state.COUNT += 1

    if state.COUNT >= FRAMES_COUNT:
        avg_amp = sum(state.AMPLITUDE_LIST) / FRAMES_COUNT
        state.SOUND_AMPLITUDE = avg_amp

        if avg_amp > SOUND_AMPLITUDE_THRESHOLD:
            state.SUS_COUNT += 1
        else:
            state.SUS_COUNT = 0
            state.AUDIO_CHEAT = 0

        if state.SUS_COUNT >= 2:
            state.AUDIO_CHEAT = 1
            print("⚠️ Suspicious sound detected!")

def audio_monitor():
    """Continuous audio monitoring."""
    with sd.Stream(callback=audio_callback):
        print("🎤 Listening for suspicious sounds...")
        while True:
            time.sleep(0.1)

# -----------------------
# Head pose monitoring
# -----------------------
mp_face_mesh = mp.solutions.face_mesh

def get_head_yaw(landmarks, img_w, img_h):
    left_eye = landmarks[33]
    right_eye = landmarks[263]
    dx = right_eye.x - left_eye.x
    dy = right_eye.y - left_eye.y
    yaw = math.degrees(math.atan2(dy, dx))
    return yaw

def check_head_pose(frame, face_landmarks):
    img_h, img_w = frame.shape[:2]

    if not face_landmarks:
        state.HEAD_SUS_COUNT = 0
        state.HEAD_CHEAT = 0
        return frame

    yaw = get_head_yaw(face_landmarks[0].landmark, img_w, img_h)

    if abs(yaw) > HEAD_TURN_THRESHOLD:
        state.HEAD_SUS_COUNT += 1
    else:
        state.HEAD_SUS_COUNT = 0
        state.HEAD_CHEAT = 0

    if state.HEAD_SUS_COUNT >= SUS_LOOK_COUNT_THRESHOLD:
        state.HEAD_CHEAT = 1
        cv2.putText(frame, "⚠️ Suspicious Head Movement!", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        print("⚠️ Suspicious head movement detected!")

    return frame

def head_pose_monitor():
    cap = cv2.VideoCapture(0)
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        print("📹 Monitoring head pose...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            frame = check_head_pose(frame, results.multi_face_landmarks)
            cv2.imshow('Proctor Monitor', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# Main: run both threads with combined alerts
if __name__ == "__main__":
    audio_thread = threading.Thread(target=audio_monitor, daemon=True)
    head_thread = threading.Thread(target=head_pose_monitor, daemon=True)

    audio_thread.start()
    head_thread.start()

    try:
        while True:
            time.sleep(0.5)
            
            # Combined alert
            if state.AUDIO_CHEAT or state.HEAD_CHEAT:
                print("🚨 ALERT: Possible cheating detected!")
                
    except KeyboardInterrupt:
        print("🛑 Monitoring stopped.")
