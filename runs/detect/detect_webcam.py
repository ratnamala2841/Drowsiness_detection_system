import cv2
import torch
from ultralytics import YOLO
import threading
from pygame import mixer
import time
import os

# Initialize mixer for alarm sound
mixer.init()
try:
    alarm_sound = mixer.Sound('voice_alarm.wav')
except:
    print("Warning: voice_alarm.wav not found. Audio alerts disabled.")
    alarm_sound = None

# Load the trained YOLO model
MODEL_PATH = 'runs/detect/train/weights/best.pt'
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model not found at {MODEL_PATH}")
    exit(1)

model = YOLO(MODEL_PATH)
print(f"Model loaded successfully")
print(f"Model classes: {model.names}")

# Confidence threshold (lowered for better detection)
CONFIDENCE_THRESHOLD = 0.25

# Drowsiness alert settings
ALERT_THRESHOLD = 3  # Number of consecutive drowsy frames to trigger alert
drowsy_counter = 0
is_alerting = False
face_detected_counter = 0

# Class mapping - adjust based on your training
# If class 0 is drowsy: set DROWSY_CLASS_ID = 0
# If class 1 is drowsy: set DROWSY_CLASS_ID = 1
DROWSY_CLASS_ID = 0  # Try 0 first, can be changed to 1 if needed

def play_alarm():
    """Play alarm sound once in a separate thread - wait for it to finish"""
    global is_alerting
    if alarm_sound:
        try:
            alarm_sound.play()  # Play sound once only
            time.sleep(3)  # Wait 3 seconds for voice to finish playing
        except Exception as e:
            print(f"Error playing alarm: {e}")
    is_alerting = False

def main():
    global drowsy_counter, is_alerting, face_detected_counter
    
    # Open webcam (0 is default camera)
    # Try using DirectShow backend to avoid MSMF issues on Windows
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    except:
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open webcam at port 0")
        print("Trying port 1...")
        try:
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        except:
            cap = cv2.VideoCapture(1)
        
        if not cap.isOpened():
            print("Error: Cannot open webcam")
            print("Try these fixes:")
            print("1. Check if camera is connected")
            print("2. Run: python fix_webcam.py")
            print("3. Check Windows Privacy: Settings → Camera")
            return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Wait for camera to initialize
    print("Initializing camera...")
    time.sleep(2)
    
    # Create window
    window_name = 'Drowsiness Detection System - YOLO'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    print("Starting drowsiness detection. Press 'q' to quit...")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Alert threshold: {ALERT_THRESHOLD} consecutive drowsy frames")
    print("Window should open now...")
    
    frame_count = 0
    
    while cap.isOpened():
        success, frame = cap.read()
        
        if not success:
            print("Warning: Failed to read frame, retrying...")
            time.sleep(0.1)
            continue  # Skip this frame and try next one
        
        frame_count += 1
        h, w = frame.shape[:2]
        
        # Flip the frame for selfie view
        frame = cv2.flip(frame, 1)
        
        # Enhance image quality for detection (but keep original for display)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        enhanced = clahe.apply(gray)
        frame_enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        # Perform inference on enhanced frame
        results = model(frame_enhanced, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        # Process results
        has_drowsy = False
        detection_count = 0
        best_detection = None
        best_confidence = 0
        
        if results and len(results) > 0:
            result = results[0]
            
            # Get boxes and class names
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes
                detection_count = len(boxes)
                
                # Find the detection with highest confidence
                for box in boxes:
                    confidence = float(box.conf[0])
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_detection = box
                
                # Process the best detection
                if best_detection is not None:
                    x1, y1, x2, y2 = map(int, best_detection.xyxy[0])
                    confidence = float(best_detection.conf[0])
                    class_id = int(best_detection.cls[0])
                    class_name = str(model.names[class_id])
                    
                    # Debug output
                    if frame_count % 10 == 0:
                        print(f"Best Detection - Class ID: {class_id}, Class Name: '{class_name}', Confidence: {confidence:.2f}")
                    
                    # Determine if drowsy based on class ID
                    is_drowsy = (class_id == DROWSY_CLASS_ID)
                    
                    # Determine color based on class
                    if is_drowsy:
                        color = (0, 0, 255)  # Red for drowsy
                        has_drowsy = True
                    else:
                        color = (0, 255, 0)  # Green for alert
                    
                    # Draw bounding box on original frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    
                    # Put label with confidence
                    label = f'{class_name}: {confidence:.2f}'
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Update face detection counter
        if detection_count > 0:
            face_detected_counter += 1
        else:
            face_detected_counter = 0
        
        # Update drowsiness counter
        if has_drowsy:
            drowsy_counter += 1
            status = "DROWSY"
        else:
            drowsy_counter = max(0, drowsy_counter - 1)  # Gradual decrease
            status = "ALERT"
        
        # Trigger alarm instantly when drowsiness detected (only once per episode)
        if drowsy_counter >= ALERT_THRESHOLD and not is_alerting:
            is_alerting = True
            threading.Thread(target=play_alarm, daemon=True).start()
            # Draw alert message
            cv2.rectangle(frame, (0, 0), (640, 100), (0, 0, 255), -1)
            cv2.putText(frame, '!!! DROWSINESS ALERT !!!', (80, 45),
                      cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 2)
            cv2.putText(frame, f'Drowsy count: {drowsy_counter}', (80, 80),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        # Only reset alert when fully recovered (counter reaches 0)
        elif drowsy_counter == 0:
            is_alerting = False
        
        # Display statistics on frame
        info_y = 30
        cv2.putText(frame, f'Status: {status}', (10, info_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f'Drowsy Frames: {drowsy_counter}/{ALERT_THRESHOLD}', 
                   (10, info_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f'Detections: {detection_count}', 
                   (10, info_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display frame
        try:
            cv2.imshow(window_name, frame)
        except Exception as e:
            print(f"Error displaying frame: {e}")
        
        # Exit on 'q' press or window close
        key = cv2.waitKey(1)
        if key != -1:
            key = key & 0xFF
            if key == ord('q') or key == 27:  # q or ESC
                print("Exiting...")
                break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    if alarm_sound:
        mixer.stop()



if __name__ == '__main__':
    main()

