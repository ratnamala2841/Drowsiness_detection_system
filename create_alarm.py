"""
Generate a simple alarm sound (beeping)
Run this once to create alarm.wav
"""

import numpy as np
import wave
import struct

def create_alarm_sound(filename='alarm.wav', duration=2, frequency=1000):
    """
    Create a simple alarm sound (beeping tone)
    
    Args:
        filename: Output file name
        duration: Duration in seconds
        frequency: Frequency in Hz (1000 = 1kHz tone)
    """
    sample_rate = 44100  # CD quality
    num_samples = int(sample_rate * duration)
    
    # Generate sine wave
    t = np.linspace(0, duration, num_samples, False)
    wave_data = np.sin(2 * np.pi * frequency * t)
    
    # Add volume (amplitude) - 0.3 to avoid clipping
    wave_data = (wave_data * 0.3 * 32767).astype(np.int16)
    
    # Write to WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(wave_data.tobytes())
    
    print(f"✓ Created {filename}")
    print(f"  Duration: {duration} seconds")
    print(f"  Frequency: {frequency} Hz")

if __name__ == '__main__':
    # Create alarm sound
    create_alarm_sound('alarm.wav', duration=2, frequency=1000)
    print("\nAlarm sound ready! Place alarm.wav in your project root directory.")
