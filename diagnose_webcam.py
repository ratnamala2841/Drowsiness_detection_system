"""
Diagnose webcam issues
Run this to find out what's wrong with your camera
"""

import cv2
import subprocess

print("="*60)
print("WEBCAM DIAGNOSTICS")
print("="*60)

# Test different camera ports
print("\n1. Testing camera ports...")
for camera_id in range(5):
    cap = cv2.VideoCapture(camera_id)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"   ✓ Camera found at port {camera_id}")
            print(f"     Resolution: {frame.shape[1]}x{frame.shape[0]}")
            cap.release()
        else:
            cap.release()
    else:
        if camera_id == 0:
            print(f"   ✗ No camera found at port {camera_id}")

# Check if pygame mixer is available
print("\n2. Checking audio support...")
try:
    from pygame import mixer
    mixer.init()
    print("   ✓ Pygame mixer is available")
except ImportError:
    print("   ✗ Pygame not installed - run: pip install pygame")

# Check OpenCV version
print("\n3. Checking OpenCV...")
print(f"   OpenCV version: {cv2.__version__}")

# Check if YOLO is available
print("\n4. Checking YOLO...")
try:
    from ultralytics import YOLO
    print("   ✓ Ultralytics YOLO is installed")
except ImportError:
    print("   ✗ Ultralytics not installed - run: pip install ultralytics")

# Check if model exists
import os
model_path = 'runs/detect/train/weights/best.pt'
print(f"\n5. Checking model file...")
if os.path.exists(model_path):
    size_mb = os.path.getsize(model_path) / (1024*1024)
    print(f"   ✓ Model found at {model_path}")
    print(f"     Size: {size_mb:.1f} MB")
else:
    print(f"   ✗ Model not found at {model_path}")

# Check if alarm.wav exists
print(f"\n6. Checking alarm sound...")
if os.path.exists('alarm.wav'):
    size_kb = os.path.getsize('alarm.wav') / 1024
    print(f"   ✓ Alarm found: alarm.wav ({size_kb:.1f} KB)")
else:
    print(f"   ✗ Alarm not found - run: python create_alarm.py")

print("\n" + "="*60)
print("SOLUTIONS:")
print("="*60)

# Find camera issues
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("\n⚠ CAMERA NOT FOUND")
    print("\nTry these fixes:")
    print("1. Check if webcam is connected and working")
    print("2. Try using camera port 1 instead of 0:")
    print("   Edit detect_webcam.py line ~52:")
    print("   Change: cap = cv2.VideoCapture(0)")
    print("   To:     cap = cv2.VideoCapture(1)")
    print("\n3. Check Device Manager:")
    print("   Windows Key → Device Manager → Cameras")
    print("   Make sure your camera is listed and enabled")
    print("\n4. Check Windows Privacy settings:")
    print("   Settings → Privacy & Security → Camera")
    print("   Allow apps to access your camera")
    print("\n5. Restart your computer")
else:
    cap.release()
    print("\n✓ Camera is working - other issue might be in detection")

print("="*60)
