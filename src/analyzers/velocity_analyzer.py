from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps
from config import FILLED_PAUSES, VELOCITY_SLOW_THRESHOLD, VELOCITY_FAST_THRESHOLD

def analyze_velocity(file_path):
    """
    Analyze speech velocity using OpenAI Whisper API
    Returns velocity metrics including WPS, WPM, and classification
    """
    print(f"🎙️ Velocity Analysis: Using OpenAI Whisper API for transcription")

    try:
        # Transcribe using OpenAI API
        words = transcribe_with_openai_timestamps(file_path)

        # Debug: Print transcript and timing info
        if words:
            transcript = " ".join([w["word"] for w in words])
            print(f"📝 Transcript: {transcript}")
            print(f"⏱️ Total words detected: {len(words)}")
            if len(words) > 0:
                print(f"⏱️ First word: '{words[0]['word']}' at {words[0]['start']:.2f}s - {words[0]['end']:.2f}s")
                if len(words) > 1:
                    print(f"⏱️ Last word: '{words[-1]['word']}' at {words[-1]['start']:.2f}s - {words[-1]['end']:.2f}s")
            print(f"⏱️ Audio file: {file_path}")
        else:
            print("⚠️ No words detected in transcription")

        if not words:
            return {
                "transcript": "",
                "filled_pauses": [],
                "word_count_total": 0,
                "word_count_clean": 0,
                "duration_spoken": 0.0,
                "real_start_time": 0.0,
                "real_end_time": 0.0,
                "wps": 0.0,
                "wpm": 0.0,
                "velocity_level": "Unknown",
                "detailed_explanation": {
                    "time_calculation": "No words detected in audio",
                    "word_calculation": "Total words: 0 | Valid words: 0",
                    "velocity_calculation": "Cannot calculate velocity"
                }
            }

        clean_words = [w for w in words if w["word"] not in FILLED_PAUSES and w["word"].isalpha()]

        # Debug: Show filled pauses vs clean words
        filled_pauses = [w["word"] for w in words if w["word"] in FILLED_PAUSES]
        print(f"🔍 Filled pauses found: {filled_pauses}")
        print(f"🔍 Clean words count: {len(clean_words)} out of {len(words)} total words")

        if not clean_words:
            return {
                "transcript": " ".join([w["word"] for w in words]),
                "filled_pauses": [w["word"] for w in words if w["word"] in FILLED_PAUSES],
                "word_count_total": len(words),
                "word_count_clean": 0,
                "duration_spoken": 0.0,
                "real_start_time": words[0]["start"] if words else 0.0,
                "real_end_time": words[-1]["end"] if words else 0.0,
                "wps": 0.0,
                "wpm": 0.0,
                "velocity_level": "All filled pauses",
                "detailed_explanation": {
                    "time_calculation": f"Time from {round(words[0]['start'], 2)} to {round(words[-1]['end'], 2)} seconds" if words else "Unknown",
                    "word_calculation": f"Total words: {len(words)} (all filled pauses) | Valid words: 0",
                    "velocity_calculation": "Cannot calculate velocity - no valid words"
                }
            }

        real_start = clean_words[0]["start"]
        real_end = clean_words[-1]["end"]
        duration_spoken = real_end - real_start

        # Debug: Show timing calculation details
        print(f"⏱️ Timing calculation:")
        print(f"   First clean word: '{clean_words[0]['word']}' starts at {real_start:.3f}s")
        print(f"   Last clean word: '{clean_words[-1]['word']}' ends at {real_end:.3f}s")
        print(f"   Duration spoken: {duration_spoken:.3f}s")
        print(f"   Words in duration: {len(clean_words)} words")

        word_count = len(clean_words)
        wps = word_count / duration_spoken if duration_spoken > 0 else 0

        print(f"   Calculated WPS: {wps:.3f} words/second")
        print(f"   Calculated WPM: {wps * 60:.1f} words/minute")

        if wps < VELOCITY_SLOW_THRESHOLD:
            level = "Slow"
        elif wps > VELOCITY_FAST_THRESHOLD:
            level = "Fast"
        else:
            level = "Normal"

        return {
            "transcript": " ".join([w["word"] for w in words]),
            "filled_pauses": [w["word"] for w in words if w["word"] in FILLED_PAUSES],
            "word_count_total": len(words),
            "word_count_clean": word_count,
            "duration_spoken": round(duration_spoken, 2),
            "real_start_time": round(real_start, 2),
            "real_end_time": round(real_end, 2),
            "wps": round(wps, 2),
            "wpm": round(wps * 60, 2),
            "velocity_level": level,
            "detailed_explanation": {
                "time_calculation": f"Actual time: from {round(real_start, 2)}s to {round(real_end, 2)}s = {round(duration_spoken, 2)}s",
                "word_calculation": f"Total words: {len(words)} (including filled pauses) | Valid words: {word_count}",
                "velocity_calculation": f"Velocity = {word_count} words ÷ {round(duration_spoken, 2)}s = {round(wps, 2)} words/sec = {round(wps * 60, 2)} words/min"
            }
        }

    except Exception as e:
        return {
            "error": f"Velocity analysis failed: {str(e)}"
        }