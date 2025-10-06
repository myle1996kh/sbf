"""
Deepgram integration for high-quality transcription.
Can be combined with ForceAlign for precise word timing.
"""

import os
import tempfile
from typing import Dict, Any

try:
    from deepgram import DeepgramClient, PrerecordedOptions, FileSource
    DEEPGRAM_AVAILABLE = True
except ImportError:
    DEEPGRAM_AVAILABLE = False

def check_deepgram_availability():
    """Check if Deepgram SDK is available."""
    return DEEPGRAM_AVAILABLE

def install_deepgram_instructions():
    """Return installation instructions for Deepgram."""
    return """
    To use Deepgram, please install the SDK:

    pip install deepgram-sdk

    Then set your API key in .env file:
    DEEPGRAM_API_KEY=your_key_here
    """

def transcribe_with_deepgram(audio_path: str) -> Dict[str, Any]:
    """
    Get high-quality transcript using Deepgram.

    Args:
        audio_path (str): Path to audio file

    Returns:
        Dict: Contains 'success', 'transcript', and optionally 'error'
    """
    if not DEEPGRAM_AVAILABLE:
        return {
            "success": False,
            "error": "Deepgram SDK not available. Please install: pip install deepgram-sdk"
        }

    # Check API key
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "DEEPGRAM_API_KEY not found in environment variables"
        }

    try:
        # Initialize Deepgram client
        deepgram = DeepgramClient(api_key)

        # Read audio file
        with open(audio_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # Configure transcription options
        options = PrerecordedOptions(
            model="nova-2",  # Latest and most accurate model
            smart_format=True,  # Automatic formatting
            punctuate=True,  # Add punctuation
            paragraphs=False,  # Keep as single paragraph
            utterances=False,  # Don't split by speaker
            language="en-US",  # English
        )

        # Transcribe
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)

        # Extract transcript
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

        if transcript.strip():
            return {
                "success": True,
                "transcript": transcript.strip()
            }
        else:
            return {
                "success": False,
                "error": "No speech detected in audio"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Deepgram transcription failed: {str(e)}"
        }

def hybrid_deepgram_forcealign_timestamps(audio_path: str) -> Dict[str, Any]:
    """
    Hybrid approach: Use Deepgram for transcription, ForceAlign for word timing.

    Args:
        audio_path (str): Path to audio file

    Returns:
        Dict: Contains word timestamps and transcript
    """
    try:
        # Step 1: Get high-quality transcript from Deepgram
        print("🔄 Getting transcript from Deepgram...")
        deepgram_result = transcribe_with_deepgram(audio_path)

        if not deepgram_result["success"]:
            return {
                "success": False,
                "error": f"Deepgram transcription failed: {deepgram_result['error']}"
            }

        transcript = deepgram_result["transcript"]
        print(f"✅ Deepgram transcript: '{transcript}'")

        # Step 2: Use ForceAlign for precise word timing with Deepgram transcript
        print("🔄 Getting word timing from ForceAlign...")
        from src.transcribers.forcealign_transcriber import transcribe_with_forcealign_timestamps

        # Use ForceAlign with the Deepgram transcript
        word_timestamps = transcribe_with_forcealign_timestamps(audio_path, transcript)

        return {
            "success": True,
            "word_timestamps": word_timestamps,
            "transcript": transcript,
            "method": "deepgram_forcealign_hybrid"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Hybrid transcription failed: {str(e)}"
        }

def whisper_forcealign_hybrid_timestamps(audio_path: str) -> Dict[str, Any]:
    """
    Hybrid approach: Use OpenAI Whisper for transcription, ForceAlign for word timing.

    Args:
        audio_path (str): Path to audio file

    Returns:
        Dict: Contains word timestamps and transcript
    """
    try:
        # Step 1: Get high-quality transcript from OpenAI Whisper
        print("🔄 Getting transcript from OpenAI Whisper...")
        from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps

        # Get transcript using Whisper (we'll use transcript, not the timestamps)
        whisper_words = transcribe_with_openai_timestamps(audio_path)

        if not whisper_words:
            return {
                "success": False,
                "error": "Failed to get transcript from OpenAI Whisper"
            }

        # Extract transcript text
        transcript = " ".join([w["word"] for w in whisper_words])
        print(f"✅ Whisper transcript: '{transcript}'")

        # Step 2: Use ForceAlign for precise word timing with Whisper transcript
        print("🔄 Getting word timing from ForceAlign...")
        from src.transcribers.forcealign_transcriber import transcribe_with_forcealign_timestamps

        # Use ForceAlign with the Whisper transcript
        word_timestamps = transcribe_with_forcealign_timestamps(audio_path, transcript)

        return {
            "success": True,
            "word_timestamps": word_timestamps,
            "transcript": transcript,
            "method": "whisper_forcealign_hybrid"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Whisper+ForceAlign hybrid failed: {str(e)}"
        }

def compare_transcription_methods():
    """Compare different transcription approaches."""
    return {
        "openai_whisper": {
            "pros": ["High accuracy", "Multiple languages", "Good with noise"],
            "cons": ["Requires API key", "Costs money", "Needs internet"],
            "use_case": "General purpose, multilingual"
        },
        "forcealign_only": {
            "pros": ["Free", "Offline", "Fast"],
            "cons": ["English only", "Lower accuracy", "Needs clear audio"],
            "use_case": "Quick English analysis, offline work"
        },
        "deepgram_only": {
            "pros": ["High accuracy", "Fast API", "Good formatting"],
            "cons": ["Requires API key", "Costs money", "No word timestamps"],
            "use_case": "High-quality transcription only"
        },
        "whisper_forcealign_hybrid": {
            "pros": ["Whisper's best accuracy", "ForceAlign precise timing", "Industry standard combo"],
            "cons": ["Requires OpenAI API key", "English only for alignment", "Two-step process"],
            "use_case": "Maximum Whisper accuracy + precise ForceAlign timing"
        },
        "deepgram_forcealign_hybrid": {
            "pros": ["Fast Deepgram API", "Precise timing", "Good formatting"],
            "cons": ["Requires Deepgram API key", "English only for alignment"],
            "use_case": "Faster/cheaper API + precise timing"
        }
    }