"""
Fast Whisper PTT (Push-to-Talk) Module
Standalone voice transcription module using faster-whisper

Usage:
    Hold Left Ctrl to record audio → Release to transcribe with faster-whisper
    Transcribed text is returned immediately

This module is completely standalone and can be used in any project.
No dependencies on Oblivion, ChatGPT, or any game-specific code.
"""

import os
import time
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel
from pynput import mouse
import clipboard

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
MAX_RECORD_SECONDS = None  # No limit
PTT_KEY = 'left alt'
MODEL_NAME = 'tiny.en'  # faster-whisper model (tiny.en for speed, medium/large for accuracy)
RECORD_DEVICE = None  # None = default mic, or set to device index/name

class FastWhisperPTT:
    """
    Fast Whisper Push-to-Talk transcription module

    Example usage:
        ptt = FastWhisperPTT()
        ptt.initialize()  # Loads whisper model (do once at startup)

        while True:
            text = ptt.listen_and_transcribe()  # Blocks until user presses/releases ctrl
            if text:
                print(f"You said: {text}")
    """

    def __init__(self, model_name=MODEL_NAME, ptt_key=PTT_KEY, max_seconds=MAX_RECORD_SECONDS):
        self.model_name = model_name
        self.ptt_key = ptt_key
        self.max_seconds = max_seconds
        self.model = None
        self.temp_dir = tempfile.gettempdir()

    def initialize(self):
        """Load the faster-whisper model. Call this once at startup."""
        print(f"Loading faster-whisper model: {self.model_name}...")
        start = time.time()

        # Use CPU for maximum compatibility (can change to 'cuda' if GPU available)
        self.model = WhisperModel(
            self.model_name,
            device='cpu',
            compute_type='int8'  # int8 for CPU, float16 for GPU
        )

        elapsed = time.time() - start
        print(f"✓ Model loaded in {elapsed:.1f}s")
        return True

    def record_audio(self):
        print("🎤 Recording...")
        """
        Record audio while PTT key is held.
        Returns path to recorded WAV file, or None if no audio.
        """
        if self.max_seconds:
            print(f"Hold Left Alt to record (max {self.max_seconds}s)...")
        else:
            print(f"Hold Left Alt to record (no time limit)...")

        # Wait for Left Alt press
        import keyboard
        print("Waiting for Left Alt press...")
        while not keyboard.is_pressed(self.ptt_key):
            time.sleep(0.01)

        print("🎤 Recording...")

        frames = []
        start = time.time()

        def callback(indata, frames_count, time_info, status):
            frames.append(indata.copy())
            # Auto-stop if too long
            if self.max_seconds and time.time() - start > self.max_seconds:
                raise sd.CallbackStop()

        try:
            # Set recording device if specified
            if RECORD_DEVICE is not None:
                try:
                    sd.default.device = RECORD_DEVICE
                except Exception:
                    pass

            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype='int16',
                callback=callback
            ):
                # Record until Left Alt released or timeout
                while keyboard.is_pressed(self.ptt_key) and (self.max_seconds is None or time.time() - start <= self.max_seconds):
                    time.sleep(0.01)

        except Exception as e:
            pass  # CallbackStop will reach here

        if not frames:
            print("⚠ No audio recorded")
            return None

        # Concatenate all audio frames
        audio = np.concatenate(frames, axis=0)
        duration = len(audio) / SAMPLE_RATE
        print(f"✓ Recorded {duration:.1f}s of audio")

        # Save to temporary WAV file
        wav_path = os.path.join(self.temp_dir, f"ptt_recording_{int(time.time())}.wav")
        sf.write(wav_path, audio, SAMPLE_RATE)

        return wav_path

    def transcribe_audio(self, wav_path):
        """
        Transcribe audio file using faster-whisper.
        Returns transcribed text string, or None if failed.
        """
        if not self.model:
            print("⚠ Model not initialized! Call initialize() first.")
            return None

        if not os.path.exists(wav_path):
            print(f"⚠ Audio file not found: {wav_path}")
            return None

        print("🔄 Transcribing...")
        start = time.time()

        try:
            # Run faster-whisper transcription
            segments, info = self.model.transcribe(
                wav_path,
                language='en',  # Force English (remove for auto-detect)
                vad_filter=True,  # Voice activity detection filter
                beam_size=1  # Faster beam search (increase for better accuracy)
            )

            # Collect all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            full_text = " ".join(text_parts).strip()
            elapsed = time.time() - start

            if full_text:
                print(f"✓ Transcribed in {elapsed:.2f}s: \"{full_text}\"")
                return full_text
            else:
                print("⚠ No speech detected")
                return None

        except Exception as e:
            print(f"⚠ Transcription error: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.remove(wav_path)
            except:
                pass

    def listen_and_transcribe(self):
        """
        One-shot PTT: Wait for key press, record, transcribe, return text.
        This is the main function you'll use in your application.

        Returns:
            str: Transcribed text, or None if no speech/error
        """
        wav_path = self.record_audio()
        if not wav_path:
            return None

        text = self.transcribe_audio(wav_path)
        if text:
            clipboard.copy(text)
            print(f"[Clipboard] Transcribed text copied: {text}")
        return text


# Standalone demo/test mode
if __name__ == "__main__":
    print("="*60)
    print("Fast Whisper PTT Module - Standalone Demo")
    print("="*60)
    print()

    # Initialize
    ptt = FastWhisperPTT()
    if not ptt.initialize():
        print("Failed to initialize!")
        exit(1)

    print()
    print("Ready! Hold Left Ctrl to record and transcribe.")
    print("Press Ctrl+C to exit.")
    print()

    try:
        while True:
            text = ptt.listen_and_transcribe()
            if text:
                print(f"\n>>> YOU SAID: {text}\n")
                # Text is now in clipboard
            else:
                print("\n>>> (no speech detected)\n")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nExiting...")
