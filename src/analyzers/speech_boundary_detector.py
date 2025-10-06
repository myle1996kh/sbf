"""
Speech boundary detection using audio energy analysis.
More accurate than relying on transcription timestamps alone.
"""

import librosa
import numpy as np
from typing import Tuple, Dict, Any

def detect_speech_boundaries(audio_path: str,
                           energy_percentile: float = 20,
                           min_speech_duration: float = 0.1) -> Dict[str, Any]:
    """
    Detect actual speech boundaries using audio energy analysis.

    Args:
        audio_path (str): Path to audio file
        energy_percentile (float): Percentile threshold for speech detection (default: 20)
        min_speech_duration (float): Minimum duration for speech segments (default: 0.1s)

    Returns:
        Dict containing speech start, end, duration, and confidence metrics
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        duration_seconds = len(y) / sr

        # Calculate RMS energy in small frames
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)    # 10ms hop
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

        # Convert frame indices to time
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        # Find speech boundaries using energy threshold
        energy_threshold = np.percentile(rms, energy_percentile)
        speech_frames = rms > energy_threshold

        if np.any(speech_frames):
            # Find continuous speech segments
            speech_indices = np.where(speech_frames)[0]

            # Get first and last speech frames
            speech_start_idx = speech_indices[0]
            speech_end_idx = speech_indices[-1]

            speech_start_time = times[speech_start_idx]
            speech_end_time = times[speech_end_idx]
            speech_duration = speech_end_time - speech_start_time

            # Calculate confidence metrics
            speech_ratio = np.sum(speech_frames) / len(speech_frames)
            avg_speech_energy = np.mean(rms[speech_frames])
            avg_silence_energy = np.mean(rms[~speech_frames]) if np.any(~speech_frames) else 0
            energy_contrast = avg_speech_energy / (avg_silence_energy + 1e-10)

            return {
                "success": True,
                "speech_start": float(speech_start_time),
                "speech_end": float(speech_end_time),
                "speech_duration": float(speech_duration),
                "total_duration": float(duration_seconds),
                "silence_before": float(speech_start_time),
                "silence_after": float(duration_seconds - speech_end_time),
                "confidence_metrics": {
                    "speech_ratio": float(speech_ratio),
                    "energy_contrast": float(energy_contrast),
                    "energy_threshold": float(energy_threshold),
                    "avg_speech_energy": float(avg_speech_energy)
                }
            }
        else:
            return {
                "success": False,
                "error": "No speech detected in audio file",
                "total_duration": float(duration_seconds)
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Speech boundary detection failed: {str(e)}"
        }

def get_corrected_speech_timing(transcription_words: list,
                               speech_boundaries: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combine transcription word timing with accurate speech boundaries.

    Args:
        transcription_words: List of word dictionaries with 'word', 'start', 'end'
        speech_boundaries: Result from detect_speech_boundaries()

    Returns:
        Dict with corrected timing information
    """
    if not speech_boundaries["success"] or not transcription_words:
        return {
            "success": False,
            "error": "Invalid input data"
        }

    # Get transcription timing
    transcription_start = transcription_words[0]["start"]
    transcription_end = transcription_words[-1]["end"]
    transcription_duration = transcription_end - transcription_start

    # Get actual speech timing
    actual_start = speech_boundaries["speech_start"]
    actual_end = speech_boundaries["speech_end"]
    actual_duration = speech_boundaries["speech_duration"]

    # Calculate correction factors
    start_offset = actual_start - transcription_start

    # Use the more conservative (shorter) duration to be safe
    corrected_duration = min(actual_duration, transcription_duration)
    corrected_start = max(actual_start, transcription_start)
    corrected_end = corrected_start + corrected_duration

    return {
        "success": True,
        "original_timing": {
            "start": transcription_start,
            "end": transcription_end,
            "duration": transcription_duration
        },
        "energy_based_timing": {
            "start": actual_start,
            "end": actual_end,
            "duration": actual_duration
        },
        "corrected_timing": {
            "start": corrected_start,
            "end": corrected_end,
            "duration": corrected_duration
        },
        "corrections": {
            "start_offset": start_offset,
            "silence_before_speech": speech_boundaries["silence_before"],
            "silence_after_speech": speech_boundaries["silence_after"]
        },
        "confidence": speech_boundaries["confidence_metrics"]
    }

def analyze_timing_accuracy(audio_path: str, transcription_words: list) -> Dict[str, Any]:
    """
    Comprehensive timing analysis comparing transcription vs energy-based detection.
    """
    # Get speech boundaries
    boundaries = detect_speech_boundaries(audio_path)

    if not boundaries["success"]:
        return boundaries

    # Get corrected timing
    corrected = get_corrected_speech_timing(transcription_words, boundaries)

    if not corrected["success"]:
        return corrected

    # Analyze accuracy
    start_diff = abs(corrected["original_timing"]["start"] - corrected["energy_based_timing"]["start"])
    end_diff = abs(corrected["original_timing"]["end"] - corrected["energy_based_timing"]["end"])

    # Determine if correction is needed
    needs_correction = start_diff > 0.1 or end_diff > 0.1

    return {
        "success": True,
        "analysis": corrected,
        "accuracy_assessment": {
            "start_difference": start_diff,
            "end_difference": end_diff,
            "needs_correction": needs_correction,
            "correction_significance": "significant" if start_diff > 0.5 else "minor"
        },
        "recommendation": {
            "use_corrected_timing": needs_correction,
            "reason": f"Transcription start differs by {start_diff:.3f}s from energy-based detection"
        }
    }