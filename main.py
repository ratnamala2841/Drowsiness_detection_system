import cv2
import mediapipe as mp
import time
import threading
from pygame import mixer
from utils import calculate_ear, get_head_pose

EYE_THRESH = 0.21
PITCH_THRESH = 0.35 # Threshold for head nodding down
CONSEC_FRAMES = 20

mixer.init()
# Ensure you have an 'alarm.wav' file in your folder
try:
    alarm_sound = mixer.Sound('alarm.wav')
except:
    print("Warning: alarm.wav not found. Audio will not play.")

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, 
    refine_landmarks=True, # Critical for glasses
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

L_EYE = [362, 385, 387, 263, 373, 380]
R_EYE = [33, 160, 158, 133, 153, 144]

cap = cv2.VideoCapture(0)
COUNTER = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.resize(frame, (640, 480))
    h, w, _ = frame.shape

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced_gray = clahe.apply(gray)
    frame_rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)

    results = face_mesh.process(frame_rgb)

    if results.multi_face_landmarks:
        for face_lms in results.multi_face_landmarks:
            landmarks = face_lms.landmark
            
            # 3. EAR calculation (Eyes)
            ear = (calculate_ear(landmarks, L_EYE) + calculate_ear(landmarks, R_EYE)) / 2.0
            
            # 4. HEAD POSE (Pitch for nodding)
            # This handles drowsiness even if eyes are semi-open but head drops
            pitch = get_head_pose(landmarks, w, h)

            # 5. DROWSINESS LOGIC
            if ear < EYE_THRESH or pitch > PITCH_THRESH:
                COUNTER += 1
                if COUNTER >= CONSEC_FRAMES:
                    cv2.putText(frame, "!!! DROWSINESS ALERT !!!", (100, 200),
                                cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 0, 255), 3)
                    if not mixer.get_busy():
                        threading.Thread(target=alarm_sound.play).start()
            else:
                COUNTER = 0

            cv2.putText(frame, f"EAR: {ear:.2f} Pitch: {pitch:.2f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Robust Drowsiness System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()