"""
Test script to determine which class is drowsy
Run this to see what the model detects and help you identify the correct class
"""

import cv2
from ultralytics import YOLO
import os

MODEL_PATH = 'runs/detect/train/weights/best.pt'
model = YOLO(MODEL_PATH)

print(f"Model loaded successfully")
print(f"Model classes: {model.names}")
print("\n" + "="*60)
print("INSTRUCTIONS:")
print("="*60)
print("1. Run this script")
print("2. It will analyze a few frames from your webcam")
print("3. Look at the console output to see which class has highest confidence")
print("4. Class with consistent HIGH confidence = your DROWSY state")
print("5. Update DROWSY_CLASS_ID in detect_webcam.py accordingly")
print("="*60 + "\n")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open webcam")
    exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Analyzing 30 frames... Look at the camera and simulate drowsiness!\n")

frame_count = 0
class_0_confidences = []
class_1_confidences = []

while frame_count < 30:
    success, frame = cap.read()
    if not success:
        break
    
    frame_count += 1
    
    # Enhance image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    enhanced = clahe.apply(gray)
    frame_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    
    # Run inference
    results = model(frame_rgb, conf=0.25, verbose=False)
    
    if results and len(results) > 0:
        result = results[0]
        if hasattr(result, 'boxes') and result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                
                if class_id == 0:
                    class_0_confidences.append(confidence)
                else:
                    class_1_confidences.append(confidence)
                
                print(f"Frame {frame_count}: Class {class_id} ('{class_name}') - Confidence: {confidence:.3f}")

cap.release()

print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
if class_0_confidences:
    avg_0 = sum(class_0_confidences) / len(class_0_confidences)
    print(f"Class 0 - Average Confidence: {avg_0:.3f} (detections: {len(class_0_confidences)})")
else:
    print(f"Class 0 - No detections")

if class_1_confidences:
    avg_1 = sum(class_1_confidences) / len(class_1_confidences)
    print(f"Class 1 - Average Confidence: {avg_1:.3f} (detections: {len(class_1_confidences)})")
else:
    print(f"Class 1 - No detections")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
if class_0_confidences and class_1_confidences:
    avg_0 = sum(class_0_confidences) / len(class_0_confidences)
    avg_1 = sum(class_1_confidences) / len(class_1_confidences)
    
    if avg_0 > avg_1:
        print("✓ Set DROWSY_CLASS_ID = 0 in detect_webcam.py")
        print(f"  (Class 0 has higher avg confidence: {avg_0:.3f} vs {avg_1:.3f})")
    else:
        print("✓ Set DROWSY_CLASS_ID = 1 in detect_webcam.py")
        print(f"  (Class 1 has higher avg confidence: {avg_1:.3f} vs {avg_0:.3f})")
elif class_0_confidences:
    print("✓ Set DROWSY_CLASS_ID = 0 in detect_webcam.py")
    print("  (Only class 0 detected)")
elif class_1_confidences:
    print("✓ Set DROWSY_CLASS_ID = 1 in detect_webcam.py")
    print("  (Only class 1 detected)")
else:
    print("✗ No detections found!")
    print("  Check your model or camera")

print("="*60)
