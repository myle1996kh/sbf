import pandas as pd
import nltk
from nltk.corpus import cmudict
from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps
import re
from typing import List, Dict, Any

# Download required NLTK data
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict')

# Load CMU dictionary for syllable counting
try:
    cmu_dict = cmudict.dict()
except:
    cmu_dict = {}

def count_syllables(word: str) -> int:
    """Count syllables in a word using CMU pronunciation dictionary."""
    word = word.lower()
    # Remove punctuation and non-alphabetic characters
    word = re.sub(r'[^a-z]', '', word)

    if not word:
        return 1

    if word in cmu_dict:
        # Count vowel sounds (marked with digits in CMU dict)
        pronunciations = cmu_dict[word]
        # Take the pronunciation with the most syllables
        return max([len([y for y in x if y[-1].isdigit()]) for x in pronunciations])

    # Fallback method for words not in dictionary
    word = word.lower()
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel

    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1

    # Ensure at least 1 syllable
    return max(1, syllable_count)

def clean_word(word: str) -> str:
    """Clean word by removing punctuation and converting to lowercase."""
    return re.sub(r'[^\w]', '', word.lower())

def classify_stretch(stretch_score: float, threshold: float) -> str:
    """Classify word as stretched or normal based on threshold."""
    if stretch_score >= threshold:
        return "Stretched"
    else:
        return "Normal"

def get_stretch_color(stretch_type: str) -> str:
    """Get color for stretch classification."""
    # Stretched = Green, Normal = Red
    return "#4ecdc4" if stretch_type == "Stretched" else "#ff6b6b"

def analyze_stretch(file_path: str, stretch_threshold: float = 0.3, model: str = None, method: str = "openai") -> Dict[str, Any]:
    """Analyze speech stretch using word-level timestamps and syllable counting."""
    try:
        # Get word-level timestamps using selected method
        if method == "forcealign":
            from src.transcribers.forcealign_transcriber import transcribe_with_forcealign_timestamps
            words_data = transcribe_with_forcealign_timestamps(file_path)
        elif method == "whisper_forcealign":
            from src.transcribers.deepgram_transcriber import whisper_forcealign_hybrid_timestamps
            hybrid_result = whisper_forcealign_hybrid_timestamps(file_path)
            if hybrid_result["success"]:
                words_data = hybrid_result["word_timestamps"]
            else:
                return {
                    "success": False,
                    "error": hybrid_result["error"]
                }
        elif method == "deepgram_forcealign":
            from src.transcribers.deepgram_transcriber import hybrid_deepgram_forcealign_timestamps
            hybrid_result = hybrid_deepgram_forcealign_timestamps(file_path)
            if hybrid_result["success"]:
                words_data = hybrid_result["word_timestamps"]
            else:
                return {
                    "success": False,
                    "error": hybrid_result["error"]
                }
        else:
            # Default to OpenAI method
            words_data = transcribe_with_openai_timestamps(file_path, model=model)

        if not words_data:
            return {
                "success": False,
                "error": f"Failed to get word timestamps from {method} transcription"
            }

        # Filter out filled pauses and non-alphabetic words (like velocity analyzer)
        from config import FILLED_PAUSES
        clean_words_data = [w for w in words_data if w["word"] not in FILLED_PAUSES and w["word"].isalpha()]

        # Use energy-based speech detection for more accurate timing
        from src.analyzers.speech_boundary_detector import analyze_timing_accuracy

        timing_analysis = analyze_timing_accuracy(file_path, words_data)

        if timing_analysis["success"] and timing_analysis["recommendation"]["use_corrected_timing"]:
            # Use corrected timing based on energy analysis
            corrected = timing_analysis["analysis"]["corrected_timing"]
            real_start_time = corrected["start"]
            real_end_time = corrected["end"]
            real_speech_duration = corrected["duration"]
            timing_method = "energy_corrected"

            print(f"🎯 Using energy-corrected timing: {real_start_time:.3f}s - {real_end_time:.3f}s ({real_speech_duration:.3f}s)")
        else:
            # Fallback to transcription timing (like velocity analyzer)
            if clean_words_data:
                real_start_time = clean_words_data[0]["start"]  # First real word start
                real_end_time = clean_words_data[-1]["end"]     # Last real word end
                real_speech_duration = real_end_time - real_start_time
                timing_method = "transcription_based"
            else:
                real_start_time = 0.0
                real_end_time = 0.0
                real_speech_duration = 0.0
                timing_method = "fallback"

            print(f"🎯 Using transcription timing: {real_start_time:.3f}s - {real_end_time:.3f}s ({real_speech_duration:.3f}s)")

        # Process each word (including filled pauses for completeness)
        processed_words = []
        total_syllables = 0

        for i, word_info in enumerate(words_data):
            word = word_info["word"]
            start = word_info["start"]
            end = word_info["end"]
            duration = end - start

            # Clean word for syllable counting
            clean_word_text = clean_word(word)
            syllables = count_syllables(clean_word_text)

            # Calculate stretch score (duration per syllable)
            stretch_score = duration / syllables if syllables > 0 else 0

            # Classify as stretched or normal
            stretch_type = classify_stretch(stretch_score, stretch_threshold)

            processed_words.append({
                "Word #": i + 1,
                "Word": word,
                "Start": round(start, 2),
                "End": round(end, 2),
                "Duration": round(duration, 2),
                "Syllables": syllables,
                "Stretch Score": round(stretch_score, 3),
                "Classification": stretch_type
            })

            total_syllables += syllables

        # Create DataFrame
        df = pd.DataFrame(processed_words)

        # Calculate summary statistics
        if len(df) > 0:
            stretched_words = df[df["Classification"] == "Stretched"]
            normal_words = df[df["Classification"] == "Normal"]

            avg_stretch = df["Stretch Score"].mean()
            max_stretch = df["Stretch Score"].max()
            min_stretch = df["Stretch Score"].min()

            summary = {
                "total_words": len(df),
                "stretched_words": len(stretched_words),
                "normal_words": len(normal_words),
                "stretch_percentage": round((len(stretched_words) / len(df)) * 100, 1),
                "avg_stretch_score": round(avg_stretch, 3),
                "max_stretch_score": round(max_stretch, 3),
                "min_stretch_score": round(min_stretch, 3),
                "total_speech_duration": round(real_speech_duration, 2),  # Use real speech duration
                "real_start_time": round(real_start_time, 2),              # Add real start time
                "real_end_time": round(real_end_time, 2),                  # Add real end time
                "total_syllables": total_syllables,
                "overall_stretch": round(real_speech_duration / total_syllables, 3) if total_syllables > 0 else 0
            }

            # Get full transcript
            transcript = " ".join([word["Word"] for word in processed_words])

        else:
            summary = {
                "total_words": 0,
                "stretched_words": 0,
                "normal_words": 0,
                "stretch_percentage": 0,
                "avg_stretch_score": 0,
                "max_stretch_score": 0,
                "min_stretch_score": 0,
                "total_speech_duration": 0,
                "total_syllables": 0,
                "overall_stretch": 0
            }
            transcript = ""

        return {
            "success": True,
            "word_table": df,
            "summary": summary,
            "transcript": transcript,
            "parameters_used": {
                "stretch_threshold": stretch_threshold,
                "analysis_method": method,
                "transcription_model": model if method == "openai" else "N/A",
                "timing_method": timing_method
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def update_stretch_classification(df: pd.DataFrame, new_threshold: float) -> pd.DataFrame:
    """Update stretch classification with new threshold without re-analyzing audio."""
    if df is None or len(df) == 0:
        return df

    # Update classification column
    df_copy = df.copy()
    df_copy["Classification"] = df_copy["Stretch Score"].apply(
        lambda x: classify_stretch(x, new_threshold)
    )

    return df_copy

def get_stretch_statistics(df: pd.DataFrame, threshold: float) -> Dict[str, Any]:
    """Calculate stretch statistics for given threshold."""
    if df is None or len(df) == 0:
        return {
            "total_words": 0,
            "stretched_words": 0,
            "normal_words": 0,
            "stretch_percentage": 0
        }

    # Update classifications with current threshold
    updated_df = update_stretch_classification(df, threshold)

    stretched_count = len(updated_df[updated_df["Classification"] == "Stretched"])
    total_count = len(updated_df)

    return {
        "total_words": total_count,
        "stretched_words": stretched_count,
        "normal_words": total_count - stretched_count,
        "stretch_percentage": round((stretched_count / total_count) * 100, 1) if total_count > 0 else 0
    }