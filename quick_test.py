"""
Quick Test - Verify the Fast Whisper PTT module works

Run this to test if everything is installed correctly.
"""

print("Fast Whisper PTT - Quick Test")
print("="*60)
print()

# Test 1: Import check
print("[1/4] Checking imports...")
try:
    from fast_whisper_ptt import FastWhisperPTT
    print("  ✓ fast_whisper_ptt module imported")
except ImportError as e:
    print(f"  ✗ ERROR: {e}")
    print("\nRun: pip install -r requirements.txt")
    exit(1)

try:
    import sounddevice
    import soundfile
    import numpy
    from faster_whisper import WhisperModel
    import keyboard
    print("  ✓ All dependencies installed")
except ImportError as e:
    print(f"  ✗ Missing dependency: {e}")
    print("\nRun: pip install -r requirements.txt")
    exit(1)

# Test 2: Model initialization
print("\n[2/4] Initializing whisper model (this may take 5-10 seconds)...")
ptt = FastWhisperPTT()
try:
    if ptt.initialize():
        print("  ✓ Model loaded successfully")
    else:
        print("  ✗ Model initialization failed")
        exit(1)
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    exit(1)

# Test 3: Audio device check
print("\n[3/4] Checking audio devices...")
try:
    devices = sounddevice.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    if input_devices:
        print(f"  ✓ Found {len(input_devices)} input device(s)")
        default = sounddevice.query_devices(kind='input')
        print(f"  ✓ Default mic: {default['name']}")
    else:
        print("  ⚠ WARNING: No input devices found!")
        print("    Make sure you have a microphone connected.")
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Test 4: PTT test
print("\n[4/4] Testing push-to-talk...")
print("\n" + "="*60)
print("READY FOR VOICE TEST!")
print("="*60)
print("\nHold LEFT CTRL and say something (e.g., 'testing one two three')")
print("Release LEFT CTRL when done speaking.")
print("\nWaiting for Left Ctrl press...")

try:
    text = ptt.listen_and_transcribe()
    print("\n" + "="*60)
    if text:
        print(f"SUCCESS! Transcribed text: \"{text}\"")
        print("="*60)
        print("\n✓ All tests passed! Module is working correctly.")
    else:
        print("No speech detected or transcription failed.")
        print("="*60)
        print("\n⚠ Module loaded but transcription didn't work.")
        print("  - Make sure your microphone is working")
        print("  - Try speaking louder/clearer")
        print("  - Check microphone permissions")
except KeyboardInterrupt:
    print("\n\nTest cancelled.")
except Exception as e:
    print(f"\n✗ ERROR during test: {e}")
    exit(1)
