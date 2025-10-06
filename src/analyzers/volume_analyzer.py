from pydub import AudioSegment
import numpy as np
import os
from config import FRAME_MS, TARGET_SAMPLE_RATE, VOLUME_TARGET_MIN, VOLUME_TARGET_MAX

# Add ffmpeg to PATH if needed
ffmpeg_path = r"C:\Users\gensh\OneDrive\Máy tính\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin"
if ffmpeg_path not in os.environ.get("PATH", ""):
    os.environ["PATH"] += f";{ffmpeg_path}"

def analyze_volume(file_path):
    """
    Analyze volume characteristics of audio file
    Returns volume metrics including min/max/avg and target coverage
    """
    try:
        # Load and normalize audio
        sound = AudioSegment.from_file(file_path)
        sound = sound.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)

        frame_len = FRAME_MS
        num_frames = len(sound) // frame_len
        all_dbfs = []

        # Process each frame
        for i in range(num_frames):
            frame = sound[i * frame_len:(i + 1) * frame_len]
            rms = frame.rms
            if rms > 0:
                dbfs = 20 * np.log10(rms / 32768)
                all_dbfs.append(dbfs)

        if not all_dbfs:
            return {
                "volume_min": -100.0,
                "volume_max": -100.0,
                "volume_avg": -100.0,
                "volume_range": 0.0,
                "frame_values": [],
                "coverage_vs_target": 0.0,
                "error": "No audio frames detected"
            }

        all_dbfs = np.array(all_dbfs)
        volume_min = float(np.min(all_dbfs))
        volume_max = float(np.max(all_dbfs))
        volume_avg = float(np.mean(all_dbfs))
        volume_range = volume_max - volume_min

        # Calculate coverage in target range
        in_target = np.logical_and(all_dbfs >= VOLUME_TARGET_MIN, all_dbfs <= VOLUME_TARGET_MAX)
        coverage = float(np.sum(in_target)) / len(all_dbfs) * 100

        return {
            "volume_min": round(volume_min, 2),
            "volume_max": round(volume_max, 2),
            "volume_avg": round(volume_avg, 2),
            "volume_range": round(volume_range, 2),
            "frame_values": [round(v, 2) for v in all_dbfs.tolist()],
            "coverage_vs_target": round(coverage, 2)
        }

    except Exception as e:
        return {
            "error": f"Volume analysis failed: {str(e)}"
        }