# Audio Analyzer - Volume & Velocity

A Streamlit application that analyzes audio files for volume characteristics and speech velocity using OpenAI's Whisper API.

## Features

- **Volume Analysis**: Measures audio volume in dBFS with target range coverage (-30 to -10 dBFS)
- **Velocity Analysis**: Calculates speech velocity using OpenAI Whisper API transcription
- **Simultaneous Processing**: Analyzes volume and velocity in parallel for efficiency
- **Comprehensive Results**: Detailed metrics, transcription, and explanations

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to `.env`
   - Or enter it directly in the Streamlit interface

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your OpenAI API key in the sidebar
2. Upload an audio file (WAV, MP3, M4A, FLAC)
3. Click "Start Analysis"
4. View results for both volume and velocity analysis

## Output Format

### Volume Analysis
- Min/Max/Average volume (dBFS)
- Volume range
- Coverage percentage in target range (-30 to -10 dBFS)

### Velocity Analysis
- Full transcript with timestamps
- Word counts (total vs clean words)
- Words Per Second (WPS) and Words Per Minute (WPM)
- Speech velocity classification (Slow/Normal/Fast)
- Detected filled pauses

## Volume Scoring System

The application includes a comprehensive scoring system that evaluates audio volume quality on a scale of 0-100 points with letter grades.

### Scoring Components

The total score is calculated using four weighted components:

#### 1. Coverage Score (40% weight)
- **What it measures**: Percentage of audio time within the optimal range (-30 to -10 dBFS)
- **Scoring**:
  - 100% coverage = 100 points
  - Multiplied by 1.2 to boost importance (max 100 points)
  - Example: 70% coverage = 84 points

#### 2. Average Position Score (30% weight)
- **What it measures**: How close the average volume is to the optimal range
- **Optimal range**: -25 to -15 dBFS (best for speech clarity)
- **Scoring**:
  - Within optimal range: 100 points
  - Within normal range (-30 to -10 dBFS): 70-100 points based on distance from optimal center
  - Outside normal range: Penalty based on distance (0-70 points)

#### 3. Range Control Score (20% weight)
- **What it measures**: Volume consistency (smaller range = better)
- **Scoring**:
  - ≤15 dB range: 100 points (very consistent)
  - ≤25 dB range: 85 points (good consistency)
  - ≤35 dB range: 70 points (acceptable)
  - >35 dB range: Penalty based on excess variation

#### 4. Boundary Score (10% weight)
- **What it measures**: Avoids extreme volume levels
- **Penalties**:
  - Volume below -50 dBFS: Too quiet (2 points per dB below -50)
  - Volume above -5 dBFS: Risk of clipping (3 points per dB above -5)

### Grade Rankings

| Score Range | Grade | Status | Meaning |
|-------------|-------|--------|---------|
| 90-100 | A+ Xuất sắc | 🟢 | Excellent volume control, professional quality |
| 80-89 | A Tốt | 🟢 | Good volume control, suitable for most purposes |
| 70-79 | B+ Khá tốt | 🟡 | Decent volume control, minor improvements needed |
| 60-69 | B Trung bình khá | 🟡 | Average volume control, noticeable issues |
| 50-59 | C+ Cần cải thiện | 🟠 | Poor volume control, improvement required |
| 40-49 | C Yếu | 🟠 | Weak volume control, significant issues |
| 0-39 | D Rất yếu | 🔴 | Very poor volume control, major problems |

### Assessment Categories

Based on the average volume level, users receive one of three assessments:

1. **Âm thanh mức nhỏ** (Low Volume): Average < -30 dBFS
   - Often too quiet for comfortable listening
   - Recommendations focus on increasing volume to normal range

2. **Âm thanh mức trung bình** (Normal Volume): -30 to -10 dBFS
   - Ideal range for natural communication
   - Recommendations focus on maintaining consistency

3. **Âm thanh mức lớn** (High Volume): Average > -10 dBFS
   - May be uncomfortably loud or risk clipping
   - Recommendations focus on reducing volume

### Example Recommendations

The system provides personalized feedback based on your audio characteristics:

- **For low volume**: "🔊 Bạn có xu hướng nói với âm thanh nhỏ và thường xuyên ở mức âm thấp. Hãy thử điều chỉnh để đưa âm thanh lên mức trung bình..."

- **For optimal volume**: "🌟 Tuyệt vời! Âm thanh của bạn ở mức trung bình tối ưu và rất dễ nghe. Hãy duy trì mức âm thanh này!"

- **For inconsistent volume**: "🎚️ Mức âm thanh của bạn biến động từ nhỏ đến lớn khá nhiều. Thử tập giữ âm thanh ổn định ở một mức..."

## Technical Details

- Uses pydub for audio processing (50ms frames)
- OpenAI Whisper API for transcription with word timestamps
- Parallel processing for efficiency
- Vietnamese language support for filled pause detection
- Advanced volume scoring with weighted components
- Statistical outlier removal using IQR method for batch analysis