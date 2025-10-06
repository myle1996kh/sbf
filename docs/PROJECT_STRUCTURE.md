# 🎤 Speech Analytics Dashboard - Project Structure

## 📁 Core Application Files

### 🎯 Main Interface
- **`app.py`** - Main Streamlit dashboard with 4 analysis modes
- **`config.py`** - Configuration and API key management

### 📊 Analysis Modules
- **`audio_analyzer.py`** - Volume & velocity analysis orchestrator
- **`volume_analyzer.py`** - Audio volume level analysis (dBFS)
- **`velocity_analyzer.py`** - Speech speed analysis (WPS/WPM)
- **`pause_word_analyzer.py`** - Pause detection between speech segments
- **`stretch_analyzer.py`** - Word stretch analysis (duration/syllable)

### 🎛️ UI Pages
- **`pause_page.py`** - Pause analysis interface
- **`stretch_page.py`** - Stretch analysis interface
- **`batch_analysis.py`** - Batch processing interface

### 🔧 Utilities
- **`openai_transcriber.py`** - OpenAI Whisper/GPT-4o transcription
- **`volume_scoring.py`** - Volume scoring algorithms
- **`visualizations.py`** - Chart generation utilities

## 📋 Analysis Types

### 🎵 Volume & Velocity
- **Volume**: Audio levels in dBFS, target range analysis
- **Velocity**: Speech speed (WPS/WPM), filled pauses detection
- **Model**: Uses OpenAI Whisper for transcription

### ⏸️ Pause Analysis
- **Detection**: Pauses between speech segments (ignores start/end)
- **Output**: Pause count, duration, timing visualization
- **Method**: Pydub silence detection + word timestamps

### 📏 Stretch Analysis
- **Measurement**: Word duration per syllable ratios
- **Threshold**: Customizable stretch detection (default: 0.38s/syllable)
- **Model**: Whisper-1 (word timestamps) or GPT-4o-transcribe (auto-fallback)

### 📊 Batch Analysis
- **Processing**: Multiple files simultaneously
- **Export**: CSV results, bulk analysis

## 🎨 UI Features

- **Clean Navigation**: 4-mode selector with descriptions
- **Responsive Layout**: Wide layout with collapsible sidebar
- **Dynamic Controls**: Real-time parameter adjustment
- **Visual Feedback**: Progress indicators, status messages
- **Export Options**: CSV downloads, chart generation

## 🔄 Workflow

1. **Select Analysis Type** → Choose from 4 analysis modes
2. **Configure Parameters** → Adjust thresholds and settings
3. **Upload Audio** → Support for MP3, WAV, M4A, FLAC
4. **Run Analysis** → Process with selected algorithms
5. **View Results** → Charts, tables, and metrics
6. **Export Data** → Download CSV reports

## 📦 Dependencies

- **Streamlit** - Web interface
- **OpenAI** - Transcription API
- **Pydub** - Audio processing
- **Matplotlib/Plotly** - Visualizations
- **Pandas** - Data handling
- **NLTK** - Syllable counting

## 🚀 Quick Start

```bash
streamlit run app.py
```

Navigate to analysis type → Upload audio → View results