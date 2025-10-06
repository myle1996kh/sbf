import os
import pandas as pd
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.silence import detect_silence
from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps
import numpy as np
from typing import Dict, List, Tuple
import io
import base64

def detect_pauses_between_words(
    file_path: str,
    silence_thresh_db: float = -40.0,
    min_pause_ms: float = 100.0,
) -> Dict:
    """Detect pauses and get word timestamps to show pauses between specific words."""

    # Step 1: Get word-level timestamps using OpenAI Whisper
    print("🎤 Getting word timestamps from Whisper...")
    words_data = transcribe_with_openai_timestamps(file_path)

    if not words_data:
        return {"success": False, "error": "Failed to get word timestamps"}

    # Step 2: Detect pauses using pydub
    print("⏸️ Detecting pauses with pydub...")
    audio = AudioSegment.from_file(file_path)

    # Detect all silence
    all_silent_ranges = detect_silence(
        audio,
        min_silence_len=int(min_pause_ms),
        silence_thresh=int(silence_thresh_db)
    )

    # Remove first and last silence (beginning/end)
    if len(all_silent_ranges) > 2:
        internal_pauses = all_silent_ranges[1:-1]
    elif len(all_silent_ranges) == 2:
        internal_pauses = []  # Only beginning and end silence
    else:
        internal_pauses = all_silent_ranges  # Keep any single silence in middle

    # Convert pause intervals from ms to seconds
    pause_intervals = []
    for start_ms, end_ms in internal_pauses:
        pause_intervals.append((start_ms / 1000.0, end_ms / 1000.0))

    # Step 3: Match pauses with words
    print("🔍 Matching pauses with words...")
    word_pause_data = []

    for i, word_info in enumerate(words_data):
        word = word_info["word"]
        word_start = word_info["start"]
        word_end = word_info["end"]

        # Check for pause BEFORE this word
        pause_before = None
        if i > 0:  # Not the first word
            prev_word_end = words_data[i-1]["end"]
            # Find any pause that overlaps with gap before this word
            for pause_start, pause_end in pause_intervals:
                # Check if pause is between previous word end and current word start
                if (pause_start >= prev_word_end - 0.1 and
                    pause_end <= word_start + 0.1):
                    pause_duration = pause_end - pause_start
                    pause_before = {
                        "start": pause_start,
                        "end": pause_end,
                        "duration": round(pause_duration, 2)
                    }
                    break

        # Check for pause AFTER this word
        pause_after = None
        if i < len(words_data) - 1:  # Not the last word
            next_word_start = words_data[i+1]["start"]
            # Find any pause that overlaps with gap after this word
            for pause_start, pause_end in pause_intervals:
                # Check if pause is between current word end and next word start
                if (pause_start >= word_end - 0.1 and
                    pause_end <= next_word_start + 0.1):
                    pause_duration = pause_end - pause_start
                    pause_after = {
                        "start": pause_start,
                        "end": pause_end,
                        "duration": round(pause_duration, 2)
                    }
                    break

        word_pause_data.append({
            "Word #": i + 1,
            "Word": word,
            "Word Start": round(word_start, 2),
            "Word End": round(word_end, 2),
            "Pause Before": f"{pause_before['duration']}s" if pause_before else "-",
            "Pause After": f"{pause_after['duration']}s" if pause_after else "-",
            "Has Pause": "Yes" if (pause_before or pause_after) else "No"
        })

    return {
        "success": True,
        "word_pause_table": word_pause_data,
        "pause_intervals": pause_intervals,
        "total_words": len(words_data),
        "total_pauses": len(pause_intervals),
        "audio_duration": len(audio) / 1000.0
    }

def create_pause_word_plot(words_data: List, pause_intervals: List, file_path: str) -> str:
    """Create a timeline plot showing words and pauses."""

    # Load audio for waveform
    audio = AudioSegment.from_file(file_path)
    audio_data = np.array(audio.get_array_of_samples())
    if audio.channels == 2:
        audio_data = audio_data.reshape((-1, 2)).mean(axis=1)

    # Normalize audio data
    if len(audio_data) > 0:
        audio_data = audio_data.astype(np.float32) / np.max(np.abs(audio_data))

    duration = len(audio) / 1000.0
    t = np.linspace(0, duration, num=len(audio_data))

    # Match the original pause_waveform.png format exactly
    fig, ax = plt.subplots(figsize=(12, 4))

    # Plot waveform exactly like original
    ax.plot(t, audio_data, linewidth=0.8, color='blue')
    ax.set_xlim(0, duration)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Audio Waveform")
    ax.set_title("Rhythm Analysis Timeline - Pauses Detected")

    # Add pause overlays exactly like original
    for idx, (pause_start, pause_end) in enumerate(pause_intervals):
        ax.axvspan(pause_start, pause_end, alpha=0.2, color="red")
        # Add pause labels exactly like original format
        ax.text(pause_start, ax.get_ylim()[1]*0.9, f"Pause {idx+1}\n{pause_end-pause_start:.1f}s",
                fontsize=8, color="red", verticalalignment="top",
                bbox=dict(facecolor="white", alpha=0.6, edgecolor="red"))

    plt.tight_layout()

    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)

    return img_base64

def analyze_pause_with_words(file_path: str, silence_db: float = -40.0, min_pause_sec: float = 0.10):
    """Main function to analyze pauses and show which words they occur around."""

    try:
        # Convert to milliseconds for pydub
        min_pause_ms = min_pause_sec * 1000

        # Detect pauses and match with words
        result = detect_pauses_between_words(file_path, silence_db, min_pause_ms)

        if not result["success"]:
            return result

        # Create DataFrame
        df = pd.DataFrame(result["word_pause_table"])

        # Create visualization
        plot_img = create_pause_word_plot(result["word_pause_table"],
                                        result["pause_intervals"],
                                        file_path)

        # Summary statistics
        words_with_pauses = len([w for w in result["word_pause_table"] if w["Has Pause"] == "Yes"])

        # Get full transcript
        transcript = " ".join([w["Word"] for w in result["word_pause_table"]])

        return {
            "success": True,
            "word_pause_table": df,
            "plot_image": plot_img,
            "transcript": transcript,
            "summary": {
                "total_words": result["total_words"],
                "total_pauses": result["total_pauses"],
                "words_with_pauses": words_with_pauses,
                "audio_duration": round(result["audio_duration"], 2)
            },
            "parameters_used": {
                "silence_threshold_db": silence_db,
                "min_pause_duration_sec": min_pause_sec
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Example usage
if __name__ == "__main__":
    # Test the analyzer
    result = analyze_pause_with_words("your_audio_file.mp3")

    if result["success"]:
        print("✅ Analysis Complete!")
        print(f"📊 {result['summary']['total_pauses']} pauses found")
        print(f"🎤 {result['summary']['words_with_pauses']}/{result['summary']['total_words']} words have pauses")
        print("\n📋 Word-Pause Table:")
        print(result["word_pause_table"].to_string(index=False))
    else:
        print(f"❌ Error: {result['error']}")