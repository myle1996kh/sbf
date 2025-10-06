import openai
import requests
import json
from config import OPENAI_API_KEY

# Model configuration - easy to switch
# NOTE: gpt-4o-transcribe currently does NOT support word-level timestamps
# Use whisper-1 for stretch analysis that requires word timestamps
TRANSCRIPTION_MODEL = "gpt-4o-transcribe"  # Options: "whisper-1", "gpt-4o-transcribe"

def transcribe_with_openai_timestamps(file_path, model=None):
    """
    Transcribe audio using OpenAI API with word timestamps
    Returns list of words with start/end times

    Args:
        file_path: Path to audio file
        model: Model to use ("whisper-1" or "gpt-4o-transcribe"). If None, uses TRANSCRIPTION_MODEL
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")

    # Use provided model or default
    selected_model = model or TRANSCRIPTION_MODEL
    print(f"Using transcription model: {selected_model}")

    # Check if model supports word timestamps
    if selected_model == "gpt-4o-transcribe":
        print("WARNING: gpt-4o-transcribe does not support word-level timestamps!")
        print("Automatically switching to whisper-1 for word timestamp support...")
        selected_model = "whisper-1"

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        with open(file_path, 'rb') as audio_file:
            # Create transcription request with timestamp support
            transcription_params = {
                "model": selected_model,
                "file": audio_file,
                "response_format": "verbose_json",
                "language": "en"
            }

            # Add word timestamps only for supported models
            if selected_model == "whisper-1":
                transcription_params["timestamp_granularities"] = ["word"]
                print("Added word-level timestamp support")

            print(f"Transcription parameters: {transcription_params}")
            response = client.audio.transcriptions.create(**transcription_params)

        words = []

        # Debug: Print response structure
        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")
        if hasattr(response, '__dict__'):
            print(f"Response dict: {response.__dict__}")

        # Try multiple ways to access words
        word_list = None

        # Method 1: Direct words attribute
        if hasattr(response, 'words') and response.words:
            word_list = response.words
            print("Found words in response.words")

        # Method 2: Check if response is a dict
        elif isinstance(response, dict) and 'words' in response:
            word_list = response['words']
            print("Found words in response['words']")

        # Method 3: Convert response to dict if needed
        elif hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
            if 'words' in response_dict:
                word_list = response_dict['words']
                print("Found words in response.model_dump()['words']")

        # Method 4: Fallback to segments
        elif hasattr(response, 'segments') and response.segments:
            print("Trying fallback to segments")
            for segment in response.segments:
                if hasattr(segment, 'words') and segment.words:
                    word_list = segment.words
                    break

        # Process word list if found
        if word_list:
            print(f"Processing {len(word_list)} words")
            for word_data in word_list:
                # Handle both dict and object formats
                if isinstance(word_data, dict):
                    word_text = word_data.get('word', '')
                    start_time = word_data.get('start', 0)
                    end_time = word_data.get('end', 0)
                else:
                    word_text = getattr(word_data, 'word', '')
                    start_time = getattr(word_data, 'start', 0)
                    end_time = getattr(word_data, 'end', 0)

                words.append({
                    "word": word_text.lower().strip(),
                    "start": start_time,
                    "end": end_time
                })
        else:
            print("No words found in response")

        return words

    except Exception as e:
        print(f"Error transcribing with {selected_model}: {e}")

        # Auto-fallback to whisper-1 if gpt-4o-transcribe fails
        if selected_model == "gpt-4o-transcribe":
            print("Falling back to whisper-1...")
            try:
                return transcribe_with_openai_timestamps(file_path, model="whisper-1")
            except Exception as fallback_error:
                print(f"Fallback to whisper-1 also failed: {fallback_error}")

        return []

def switch_to_whisper():
    """Helper function to switch to whisper-1 model"""
    global TRANSCRIPTION_MODEL
    TRANSCRIPTION_MODEL = "whisper-1"
    print("Switched to whisper-1 model")

def switch_to_gpt4o():
    """Helper function to switch to gpt-4o-transcribe model"""
    global TRANSCRIPTION_MODEL
    TRANSCRIPTION_MODEL = "gpt-4o-transcribe"
    print("Switched to gpt-4o-transcribe model")

def get_current_model():
    """Get current transcription model"""
    return TRANSCRIPTION_MODEL

def transcribe_with_gpt4o(file_path):
    """
    Test function to transcribe with gpt-4o-transcribe (no word timestamps)
    Returns transcript text and basic info
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        with open(file_path, 'rb') as audio_file:
            print("Testing gpt-4o-transcribe model...")
            response = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                response_format="verbose_json",
                language="en"
            )

        print(f"Response type: {type(response)}")
        print(f"Response attributes: {dir(response)}")

        # Extract basic info
        result = {
            "model": "gpt-4o-transcribe",
            "text": "",
            "language": "",
            "duration": 0,
            "has_words": False,
            "has_segments": False
        }

        # Try different ways to access the response
        if hasattr(response, 'text'):
            result["text"] = response.text
            print(f"Found text: {response.text[:100]}...")

        if hasattr(response, 'language'):
            result["language"] = response.language
            print(f"Detected language: {response.language}")

        if hasattr(response, 'duration'):
            result["duration"] = response.duration
            print(f"Duration: {response.duration}s")

        # Check for word-level data (should be None for gpt-4o-transcribe)
        if hasattr(response, 'words') and response.words:
            result["has_words"] = True
            print(f"Found {len(response.words)} words with timestamps")
        else:
            print("No word-level timestamps (expected for gpt-4o-transcribe)")

        # Check for segments
        if hasattr(response, 'segments') and response.segments:
            result["has_segments"] = True
            print(f"Found {len(response.segments)} segments")

        # Convert to dict if possible for full inspection
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
            print(f"Full response structure: {response_dict}")

        return result

    except Exception as e:
        print(f"Error testing gpt-4o-transcribe: {e}")
        return {"error": str(e)}