"""
Fix webcam issues - try different approaches
"""

import cv2
import time

print("="*60)
print("TESTING DIFFERENT CAMERA APPROACHES")
print("="*60)

# Test 1: Simple camera read
print("\n1. Testing direct camera access (port 0)...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("   ✓ Camera opened")
    
    # Try multiple times
    success_count = 0
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            success_count += 1
            print(f"   ✓ Frame {i+1} read successfully")
        else:
            print(f"   ✗ Frame {i+1} failed")
        time.sleep(0.1)
    
    cap.release()
    
    if success_count > 0:
        print(f"   Result: {success_count}/10 frames read successfully")
    else:
        print("   ✗ No frames readable")
else:
    print("   ✗ Cannot open camera at port 0")

# Test 2: Try port 1
print("\n2. Testing camera at port 1...")
cap = cv2.VideoCapture(1)
if cap.isOpened():
    print("   ✓ Camera opened at port 1")
    ret, frame = cap.read()
    if ret:
        print("   ✓ Frame read successfully from port 1")
    cap.release()
else:
    print("   ✗ No camera at port 1")

# Test 3: Add delay before reading
print("\n3. Testing with initialization delay...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print("   Waiting for camera to initialize...")
    time.sleep(2)  # Wait 2 seconds
    ret, frame = cap.read()
    if ret:
        print("   ✓ Frame read successfully with delay")
    cap.release()

print("\n" + "="*60)
print("SOLUTION:")
print("="*60)
print("""
If tests above show frames reading successfully, edit detect_webcam.py:

Option A - Add initialization delay (line after cap.set):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    time.sleep(2)  # ADD THIS LINE

Option B - Use camera port 1 instead of 0:
    cap = cv2.VideoCapture(1)  # Change from 0 to 1

Option C - Use DirectShow backend:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

Option D - Disable MSMF backend:
    Set windows environment variable before running:
    set OPENCV_VIDEOIO_DEBUG=1
""")
print("="*60)
