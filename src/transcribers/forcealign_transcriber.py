"""
ForceAlign integration for word-level timing without OpenAI API dependency.
Provides an alternative to OpenAI Whisper for stretch analysis.
"""

import tempfile
import os
from typing import List, Dict, Any
import librosa
import soundfile as sf

try:
    from forcealign import ForceAlign
    FORCEALIGN_AVAILABLE = True
except ImportError:
    FORCEALIGN_AVAILABLE = False

def check_forcealign_availability():
    """Check if ForceAlign is available and provide installation instructions."""
    return FORCEALIGN_AVAILABLE

def install_forcealign_instructions():
    """Return installation instructions for ForceAlign."""
    return """
    To use ForceAlign method, please install it:

    pip install forcealign

    Note: ForceAlign requires PyTorch and may need additional dependencies.
    """

def transcribe_with_forcealign_timestamps(audio_path: str, transcript: str = None) -> List[Dict[str, Any]]:
    """
    Get word-level timestamps using ForceAlign.

    Args:
        audio_path (str): Path to audio file
        transcript (str): Optional transcript. If None, ForceAlign will generate one.

    Returns:
        List[Dict]: List of word dictionaries with 'word', 'start', 'end' keys
    """
    if not FORCEALIGN_AVAILABLE:
        raise ImportError("ForceAlign not available. Please install: pip install forcealign")

    try:
        # Convert audio to supported format if needed
        temp_wav_path = None
        if not audio_path.lower().endswith(('.wav', '.mp3')):
            # Convert to WAV using librosa
            y, sr = librosa.load(audio_path, sr=None)
            temp_wav_path = tempfile.NamedTemporaryFile(suffix='.wav', delete=False).name
            sf.write(temp_wav_path, y, sr)
            audio_path_for_alignment = temp_wav_path
        else:
            audio_path_for_alignment = audio_path

        # Perform forced alignment using correct API
        if transcript:
            # Use provided transcript (e.g., from Deepgram)
            print(f"🎯 Using provided transcript: '{transcript}'")
            align = ForceAlign(audio_file=audio_path_for_alignment, transcript=transcript)
        else:
            # Let ForceAlign generate transcript automatically using Wav2Vec2
            print("🔄 Generating transcript with ForceAlign's built-in ASR...")
            align = ForceAlign(audio_file=audio_path_for_alignment)

        # Run inference to get word alignments
        words = align.inference()

        # Clean up temp file if created
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.unlink(temp_wav_path)

        # Convert to expected format
        word_timestamps = []
        for word in words:
            word_timestamps.append({
                "word": word.word,
                "start": word.time_start,
                "end": word.time_end
            })

        return word_timestamps

    except Exception as e:
        # Clean up temp file if created and error occurred
        if temp_wav_path and os.path.exists(temp_wav_path):
            os.unlink(temp_wav_path)
        raise Exception(f"ForceAlign transcription failed: {str(e)}")

def get_forcealign_transcript(audio_path: str) -> str:
    """
    Get full transcript using ForceAlign.

    Args:
        audio_path (str): Path to audio file

    Returns:
        str: Full transcript text
    """
    if not FORCEALIGN_AVAILABLE:
        raise ImportError("ForceAlign not available. Please install: pip install forcealign")

    try:
        # Use ForceAlign to generate transcript
        align = ForceAlign(audio_file=audio_path)
        words = align.inference()

        # Get the raw transcript from the align object or construct from words
        if hasattr(align, 'raw_text') and align.raw_text:
            transcript = align.raw_text
        else:
            # Fallback: construct from word list
            transcript = " ".join([word.word for word in words])

        return transcript

    except Exception as e:
        raise Exception(f"ForceAlign transcript generation failed: {str(e)}")

def compare_methods_info():
    """Return comparison information between OpenAI and ForceAlign methods."""
    return {
        "openai": {
            "name": "OpenAI Whisper",
            "pros": [
                "High accuracy transcription",
                "Supports multiple languages",
                "Good with noisy audio",
                "Handles various accents well"
            ],
            "cons": [
                "Requires API key and internet",
                "Usage costs money",
                "Depends on external service",
                "May have rate limits"
            ],
            "best_for": "High accuracy transcription with various languages and accents"
        },
        "forcealign": {
            "name": "ForceAlign",
            "pros": [
                "Works offline (no API needed)",
                "Free to use",
                "Fast processing",
                "Precise word alignment",
                "Good for speech research"
            ],
            "cons": [
                "English only",
                "Requires clear audio",
                "May struggle with accents",
                "Needs additional installation"
            ],
            "best_for": "English speech analysis with clear audio, offline processing"
        }
    }