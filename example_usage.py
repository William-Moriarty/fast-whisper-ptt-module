"""
Example: How to use Fast Whisper PTT Module in your own project

This shows several common use cases.
"""

from fast_whisper_ptt import FastWhisperPTT
import time

print("="*60)
print("Fast Whisper PTT - Example Usage")
print("="*60)
print()

# Initialize the PTT system
print("Initializing...")
ptt = FastWhisperPTT(
    model_name='tiny.en',  # Change to 'small', 'medium', or 'large-v2' for better accuracy
    ptt_key='left alt',   # Change to any key you want
    max_seconds=None       # No maximum recording length
)

if not ptt.initialize():
    print("ERROR: Failed to initialize!")
    exit(1)

print()
print("✓ Ready!")
print()

# Example 1: Simple loop - transcribe and print
print("="*60)
print("EXAMPLE 1: Simple transcription loop")
print("="*60)
print("Hold Left Ctrl to speak. Say 'quit' to move to next example.")
print()

while True:
    text = ptt.listen_and_transcribe()
    if text:
        print(f">>> {text}")

        if 'quit' in text.lower():
            print("\nMoving to next example...\n")
            break

time.sleep(1)

# Example 2: Voice commands
print("="*60)
print("EXAMPLE 2: Voice command recognition")
print("="*60)
print("Try saying: 'open file', 'save document', 'close window', or 'quit'")
print()

COMMANDS = {
    'open': ['open file', 'open document', 'open'],
    'save': ['save file', 'save document', 'save'],
    'close': ['close window', 'close', 'exit'],
    'quit': ['quit', 'stop', 'done']
}

while True:
    text = ptt.listen_and_transcribe()
    if not text:
        continue

    text_lower = text.lower()
    print(f"Heard: \"{text}\"")

    # Check for commands
    command_found = False
    for command, phrases in COMMANDS.items():
        for phrase in phrases:
            if phrase in text_lower:
                print(f"  → Executing command: {command.upper()}")
                command_found = True
                break
        if command_found:
            break

    if not command_found:
        print("  → Unknown command")

    # Check for quit
    if 'quit' in text_lower or 'stop' in text_lower or 'done' in text_lower:
        print("\nMoving to next example...\n")
        break

time.sleep(1)

# Example 3: Voice-to-text notes
print("="*60)
print("EXAMPLE 3: Voice notes / dictation")
print("="*60)
print("Speak sentences to build a document. Say 'done' when finished.")
print()

notes = []
print("Start dictating:")

while True:
    text = ptt.listen_and_transcribe()
    if not text:
        continue

    if 'done' in text.lower() or 'finished' in text.lower():
        break

    notes.append(text)
    print(f"  + {text}")

print("\n" + "="*60)
print("FINAL DOCUMENT:")
print("="*60)
print("\n".join(notes))
print("="*60)

print("\nAll examples complete!")
