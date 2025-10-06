import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Audio processing settings
FRAME_MS = 50
TARGET_SAMPLE_RATE = 16000

# Volume analysis thresholds (dBFS)
VOLUME_TARGET_MIN = -30
VOLUME_TARGET_MAX = -10

# Velocity analysis thresholds (WPS)
VELOCITY_SLOW_THRESHOLD = 2.0
VELOCITY_FAST_THRESHOLD = 3.5

# Filled pauses (Vietnamese)
FILLED_PAUSES = ["uh", "um", "erm", "ah", "uhm", "mmm", "huh", "ờ", "à"]