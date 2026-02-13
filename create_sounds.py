"""
Generate clear voice alarm sound for drowsiness detection
"""

import pyttsx3
import os

def create_voice_alarm(text, filename='voice_alarm.wav'):
    """
    Create clear voice alarm with proper TTS settings
    """
    
    # Initialize TTS engine
    engine = pyttsx3.init()
    
    # Set voice properties for MAXIMUM CLARITY
    engine.setProperty('rate', 70)    # Very slow - clearest possible
    engine.setProperty('volume', 1.0)  # Maximum volume
    
    # Select voice
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
    
    # Generate audio file
    engine.save_to_file(text, filename)
    engine.runAndWait()
    
    if os.path.exists(filename):
        size_kb = os.path.getsize(filename) / 1024
        print(f"✓ Saved: {filename}")
        print(f"Size: {size_kb:.1f} KB")
        print(f"Message: '{text}'")
        print(f"Rate: 70 (very slow for maximum clarity)")
    else:
        print(f"✗ Error creating {filename}")

# Generate alarm
print("="*60)
print("GENERATING CLEAR VOICE ALARM")
print("="*60 + "\n")

# Create clear voice alarm - "Stay Alert"
create_voice_alarm('Stay Alert', 'voice_alarm.wav')

print("\n" + "="*60)
print("DONE!")
print("="*60)
print("\nAlarm: Clear voice saying 'Stay Alert'")
print("Plays only once when drowsiness detected")



