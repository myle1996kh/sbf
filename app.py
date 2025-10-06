import streamlit as st
import os
import tempfile
from src.audio_analyzer import analyze_audio_file, display_results
import pandas as pd
from src.pages.batch_analysis import batch_analyze_page

# Page configuration
st.set_page_config(
    page_title="Speech Analytics Dashboard",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API key from .env file
from dotenv import load_dotenv
load_dotenv()

# Header
st.title("🎤 Speech Analytics Dashboard")
st.markdown("Comprehensive speech analysis toolkit for volume, velocity, pauses, and stretch patterns")

# Navigation
st.sidebar.title("📊 Analysis Tools")
page = st.sidebar.selectbox(
    "Choose Analysis Type",
    ["Volume & Velocity", "Pause Analysis", "Stretch Analysis", "Batch Analysis"],
    help="Select the type of speech analysis you want to perform"
)

if page == "Batch Analysis":
    batch_analyze_page()
elif page == "Pause Analysis":
    from src.pages.pause_page import pause_analysis_page
    pause_analysis_page()
elif page == "Stretch Analysis":
    from src.pages.stretch_page import stretch_analysis_page
    stretch_analysis_page()
else:  # Volume & Velocity
    # Volume & Velocity analysis
    st.header("🎵 Volume & Velocity Analysis")
    st.markdown("Analyze audio volume characteristics and speech velocity patterns")

    # API Key input (only for single file analysis)
    st.sidebar.header("🔑 Configuration")

    # Try to get API key from environment first
    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        api_key = env_api_key
        st.sidebar.success("✅ API Key loaded from .env")
    else:
        api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.sidebar.success("✅ API Key set!")
        else:
            st.sidebar.warning("⚠️ Please enter your OpenAI API Key")

    # File upload section (only for single file analysis)
    st.header("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac'],
        help="Supported formats: WAV, MP3, M4A, FLAC"
    )

    # Analysis section
    if uploaded_file and api_key:
        st.header("🔄 Analysis")

        if st.button("Start Analysis", type="primary"):
            with st.spinner("Analyzing audio file..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name

                    # Run analysis
                    result = analyze_audio_file(temp_path)

                    # Clean up temp file
                    os.unlink(temp_path)

                    # Store result in session state
                    st.session_state['analysis_result'] = result
                    st.success("✅ Analysis completed!")

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

    # Display results if available (only for single file analysis)
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']

        st.header("📊 Analysis Results")

        # Create columns for results
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔊 Volume Analysis")
            volume = result['volume_analysis']

            if 'error' in volume:
                st.error(f"Error: {volume['error']}")
            else:
                # Volume metrics
                volume_metrics = {
                    "Metric": ["Min Volume", "Max Volume", "Avg Volume", "Volume Range", "Target Coverage"],
                    "Value": [
                        f"{volume['volume_min']} dBFS",
                        f"{volume['volume_max']} dBFS",
                        f"{volume['volume_avg']} dBFS",
                        f"{volume['volume_range']} dBFS",
                        f"{volume['coverage_vs_target']}%"
                    ]
                }
                volume_df = pd.DataFrame(volume_metrics)
                st.dataframe(volume_df, use_container_width=True)

                # Volume status
                if volume['coverage_vs_target'] >= 70:
                    st.success("✅ Good volume coverage in target range (-30 to -10 dBFS)")
                elif volume['coverage_vs_target'] >= 40:
                    st.warning("⚠️ Moderate volume coverage")
                else:
                    st.error("❌ Poor volume coverage in target range")

        with col2:
            st.subheader("🏃 Velocity Analysis")
            velocity = result['velocity_analysis']

            if 'error' in velocity:
                st.error(f"Error: {velocity['error']}")
            else:
                # Velocity metrics
                velocity_metrics = {
                    "Metric": ["Total Words", "Clean Words", "Duration", "WPS", "WPM", "Level"],
                    "Value": [
                        str(velocity['word_count_total']),
                        str(velocity['word_count_clean']),
                        f"{velocity['duration_spoken']}s",
                        f"{velocity['wps']} words/sec",
                        f"{velocity['wpm']} words/min",
                        velocity['velocity_level']
                    ]
                }
                velocity_df = pd.DataFrame(velocity_metrics)
                st.dataframe(velocity_df, use_container_width=True)

                # Velocity status
                if velocity['velocity_level'] == "Normal":
                    st.success("✅ Normal speech velocity (2.0-3.5 WPS)")
                elif velocity['velocity_level'] == "Slow":
                    st.info("ℹ️ Slow speech velocity (<2.0 WPS)")
                else:
                    st.warning("⚠️ Fast speech velocity (>3.5 WPS)")

        # Detailed information
        st.subheader("📝 Detailed Information")

        # Transcript
        if 'velocity_analysis' in result and 'transcript' in result['velocity_analysis']:
            with st.expander("📄 Transcript"):
                st.text_area("Transcribed text:", result['velocity_analysis']['transcript'], height=100)

        # Filled pauses
        if 'velocity_analysis' in result and 'filled_pauses' in result['velocity_analysis']:
            filled_pauses = result['velocity_analysis']['filled_pauses']
            if filled_pauses:
                with st.expander("🗣️ Filled Pauses"):
                    st.write(f"Detected filled pauses: {', '.join(filled_pauses)}")
                    st.write(f"Total count: {len(filled_pauses)}")

        # Technical details
        with st.expander("🔍 Technical Details"):
            velocity = result['velocity_analysis']
            if 'detailed_explanation' in velocity:
                st.write("**Time Calculation:**")
                st.write(velocity['detailed_explanation']['time_calculation'])
                st.write("**Word Calculation:**")
                st.write(velocity['detailed_explanation']['word_calculation'])
                st.write("**Velocity Calculation:**")
                st.write(velocity['detailed_explanation']['velocity_calculation'])

    # Global sidebar info
    st.sidebar.markdown("---")
    st.sidebar.header("📖 Analysis Types")
    st.sidebar.markdown("""
    **🎵 Volume & Velocity**
    - Audio volume levels (dBFS)
    - Speech speed (WPS/WPM)
    - Uses OpenAI Whisper

    **⏸️ Pause Analysis**
    - Detects pauses between speech
    - Shows pause timing & duration
    - Ignores beginning/end silence

    **📏 Stretch Analysis**
    - Word duration per syllable
    - Identifies stretched pronunciation
    - Customizable thresholds

    **📊 Batch Analysis**
    - Process multiple files
    - Bulk analysis & export
    """)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🎤 Speech Analytics v2.0")