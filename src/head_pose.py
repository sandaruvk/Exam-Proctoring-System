# head_pose.py
# Detects head pose to identify suspicious behavior (looking away)

import cv2
import mediapipe as mp
import math
import state  # import shared state variables

mp_face_mesh = mp.solutions.face_mesh

# Thresholds
HEAD_TURN_THRESHOLD = 15  # Degrees (yaw) to consider "looking away"
SUS_LOOK_COUNT_THRESHOLD = 2  # Number of consecutive frames to flag

# Shared state
state.HEAD_SUS_COUNT = 0
state.HEAD_CHEAT = 0

# Helper functions
def get_head_pose(landmarks, img_w, img_h):
    """
    Estimate head yaw (left/right rotation) using facial landmarks.
    Returns yaw in degrees.
    """
    # Key points for yaw estimation: left & right eye outer corners
    left_eye = landmarks[33]   # Approx left eye outer corner
    right_eye = landmarks[263]  # Approx right eye outer corner

    dx = right_eye.x - left_eye.x
    dy = right_eye.y - left_eye.y

    # Yaw angle (negative = looking left, positive = looking right)
    yaw = math.degrees(math.atan2(dy, dx))
    return yaw

def check_head_pose(frame, face_landmarks):
    img_h, img_w = frame.shape[:2]

    if not face_landmarks:
        state.HEAD_SUS_COUNT = 0
        state.HEAD_CHEAT = 0
        return frame

    yaw = get_head_pose(face_landmarks[0].landmark, img_w, img_h)
    
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
    """Open webcam stream and monitor head pose."""
    cap = cv2.VideoCapture(0)
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:

        print("📹 Monitoring head pose... (Press 'q' to quit)")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            frame = check_head_pose(frame, results.multi_face_landmarks)

            cv2.imshow('Head Pose Monitor', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    head_pose_monitor()
