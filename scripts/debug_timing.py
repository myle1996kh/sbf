#!/usr/bin/env python3
"""
Debug script to investigate actual timing in audio files
"""

import os
import librosa
import numpy as np
from openai_transcriber import transcribe_with_openai_timestamps

def analyze_audio_timing(audio_file):
    """Analyze actual audio timing vs transcription timing"""

    print(f"🎯 Debugging Timing Analysis: {audio_file}")
    print("=" * 60)

    # 1. Load audio file to check actual content
    print("📊 1. Loading audio file...")
    try:
        y, sr = librosa.load(audio_file, sr=None)
        duration_seconds = len(y) / sr
        print(f"   Audio file duration: {duration_seconds:.2f} seconds")
        print(f"   Sample rate: {sr} Hz")
        print(f"   Total samples: {len(y)}")
    except Exception as e:
        print(f"   ❌ Error loading audio: {e}")
        return

    # 2. Detect actual speech boundaries using energy
    print("\n📊 2. Detecting speech boundaries using audio energy...")

    # Calculate RMS energy
    frame_length = int(0.025 * sr)  # 25ms frames
    hop_length = int(0.010 * sr)    # 10ms hop
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    # Convert frame indices to time
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

    # Find speech boundaries using energy threshold
    energy_threshold = np.percentile(rms, 20)  # Bottom 20% is likely silence
    speech_frames = rms > energy_threshold

    if np.any(speech_frames):
        speech_start_idx = np.where(speech_frames)[0][0]
        speech_end_idx = np.where(speech_frames)[0][-1]

        actual_speech_start = times[speech_start_idx]
        actual_speech_end = times[speech_end_idx]
        actual_speech_duration = actual_speech_end - actual_speech_start

        print(f"   Energy-based speech start: {actual_speech_start:.3f}s")
        print(f"   Energy-based speech end: {actual_speech_end:.3f}s")
        print(f"   Energy-based speech duration: {actual_speech_duration:.3f}s")
    else:
        print("   ❌ No speech detected using energy method")
        actual_speech_start = 0
        actual_speech_end = duration_seconds
        actual_speech_duration = duration_seconds

    # 3. Get transcription timing
    print("\n📊 3. Getting transcription timing...")
    try:
        words = transcribe_with_openai_timestamps(audio_file)

        if words:
            transcript = " ".join([w["word"] for w in words])
            print(f"   Transcript: '{transcript}'")
            print(f"   Total words: {len(words)}")

            # Show first and last few words with timing
            print(f"\n   📋 First 3 words:")
            for i, word in enumerate(words[:3]):
                print(f"      {i+1}. '{word['word']}': {word['start']:.3f}s - {word['end']:.3f}s (duration: {word['end']-word['start']:.3f}s)")

            print(f"\n   📋 Last 3 words:")
            for i, word in enumerate(words[-3:], len(words)-2):
                print(f"      {i}. '{word['word']}': {word['start']:.3f}s - {word['end']:.3f}s (duration: {word['end']-word['start']:.3f}s)")

            # Transcription timing
            transcription_start = words[0]["start"]
            transcription_end = words[-1]["end"]
            transcription_duration = transcription_end - transcription_start

            print(f"\n   Transcription speech start: {transcription_start:.3f}s")
            print(f"   Transcription speech end: {transcription_end:.3f}s")
            print(f"   Transcription speech duration: {transcription_duration:.3f}s")

        else:
            print("   ❌ No words found in transcription")
            return

    except Exception as e:
        print(f"   ❌ Transcription error: {e}")
        return

    # 4. Compare methods
    print("\n📊 4. Comparison of timing methods:")
    print("-" * 40)
    print(f"{'Method':<25} {'Start':<10} {'End':<10} {'Duration':<12}")
    print("-" * 40)
    print(f"{'Audio file total':<25} {'0.000s':<10} {f'{duration_seconds:.3f}s':<10} {f'{duration_seconds:.3f}s':<12}")
    print(f"{'Energy-based detection':<25} {f'{actual_speech_start:.3f}s':<10} {f'{actual_speech_end:.3f}s':<10} {f'{actual_speech_duration:.3f}s':<12}")
    print(f"{'Transcription timing':<25} {f'{transcription_start:.3f}s':<10} {f'{transcription_end:.3f}s':<10} {f'{transcription_duration:.3f}s':<12}")

    # 5. Analysis
    print(f"\n📊 5. Analysis:")

    silence_at_start = transcription_start - actual_speech_start
    silence_at_end = actual_speech_end - transcription_end

    print(f"   🔍 Silence before first word: {silence_at_start:.3f}s")
    print(f"   🔍 Silence after last word: {silence_at_end:.3f}s")

    if abs(transcription_start) < 0.1:
        print(f"   ⚠️  Transcription starts at {transcription_start:.3f}s - very close to file start!")
        print(f"   💡 This suggests either:")
        print(f"      - No silence at beginning (speaker starts immediately)")
        print(f"      - Transcription model isn't detecting the actual start accurately")

    if silence_at_start > 0.5:
        print(f"   ✅ Significant silence detected at start ({silence_at_start:.3f}s)")
    elif silence_at_start > 0.1:
        print(f"   📝 Small amount of silence at start ({silence_at_start:.3f}s)")
    else:
        print(f"   ⚠️  Little to no silence at start ({silence_at_start:.3f}s)")

    # 6. Recommendations
    print(f"\n📊 6. Recommendations:")
    if abs(transcription_start) < 0.1:
        print(f"   🔍 Check if audio actually starts with speech or if transcription is off")
        print(f"   💡 Consider using energy-based speech detection for more accurate start time")
        print(f"   🎯 Current method may be working correctly if speaker really starts at 0s")
    else:
        print(f"   ✅ Transcription timing looks reasonable")

def test_multiple_files():
    """Test timing on multiple audio files to see patterns"""

    audio_files = ["Stretch 3.mp3"]

    # Look for other audio files
    for file in os.listdir("."):
        if file.lower().endswith(('.mp3', '.wav', '.m4a', '.flac')) and file != "Stretch 3.mp3":
            audio_files.append(file)

    if len(audio_files) > 1:
        print(f"\n🔄 Testing multiple files to see timing patterns...")
        for audio_file in audio_files[:3]:  # Test max 3 files
            if os.path.exists(audio_file):
                print(f"\n" + "="*60)
                analyze_audio_timing(audio_file)
    else:
        print(f"\n💡 Only testing {audio_files[0]} - add more audio files to compare patterns")

if __name__ == "__main__":
    analyze_audio_timing("Stretch 3.mp3")

    test_input = input("\n🤔 Test other audio files for comparison? (y/n): ")
    if test_input.lower() in ['y', 'yes']:
        test_multiple_files()