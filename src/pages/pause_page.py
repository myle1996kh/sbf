import streamlit as st
import os
import tempfile
import pandas as pd
import base64
from src.analyzers.pause_word_analyzer import analyze_pause_with_words

def pause_analysis_page():
    """Streamlit page for pause analysis with dynamic controls."""

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⏸️ Pause Analysis")
        st.markdown("Detect and analyze pauses that occur between speech segments")
    with col2:
        st.metric("Analysis Type", "Pause", help="Detects silence gaps between speech")

    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()

    # Sidebar controls
    st.sidebar.header("⚙️ Pause Detection Parameters")

    # Dynamic threshold controls
    silence_db = st.sidebar.slider(
        "Silence Threshold (dB)",
        min_value=-60.0,
        max_value=-20.0,
        value=-38.0,
        step=1.0,
        help="Audio below this level is considered silence"
    )

    min_pause_sec = st.sidebar.slider(
        "Minimum Pause Duration (seconds)",
        min_value=0.05,
        max_value=2.0,
        value=0.5,
        step=0.05,
        help="Minimum duration for a segment to be classified as a pause"
    )

    # File upload
    st.header("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac'],
        help="Supported formats: WAV, MP3, M4A, FLAC"
    )

    # Analysis section
    if uploaded_file:
        # Check if we need to re-analyze or just update thresholds
        file_changed = ('uploaded_file_name' not in st.session_state or
                       st.session_state['uploaded_file_name'] != uploaded_file.name)

        params_changed = ('prev_silence_db' not in st.session_state or
                         'prev_min_pause_sec' not in st.session_state or
                         st.session_state['prev_silence_db'] != silence_db or
                         st.session_state['prev_min_pause_sec'] != min_pause_sec)

        if file_changed or params_changed or st.button("🔄 Analyze Pauses", type="primary"):
            with st.spinner("Analyzing pauses..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name

                    # Run pause analysis with current parameters
                    result = analyze_pause_with_words(temp_path, silence_db=silence_db, min_pause_sec=min_pause_sec)

                    # Clean up temp file
                    os.unlink(temp_path)

                    # Store results and parameters in session state
                    st.session_state['pause_result'] = result
                    st.session_state['uploaded_file_name'] = uploaded_file.name
                    st.session_state['prev_silence_db'] = silence_db
                    st.session_state['prev_min_pause_sec'] = min_pause_sec

                    if result['success']:
                        st.success("✅ Pause analysis completed!")
                    else:
                        st.error(f"❌ Analysis failed: {result['error']}")

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

    # Display results
    if 'pause_result' in st.session_state:
        result = st.session_state['pause_result']

        if result['success']:
            # Summary metrics
            st.header("📊 Pause Analysis Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Pauses", result['summary']['total_pauses'])

            with col2:
                st.metric("Audio Duration", f"{result['summary']['audio_duration']}s")

            # Current parameters display
            st.subheader("🎛️ Current Parameters")
            param_col1, param_col2 = st.columns(2)
            with param_col1:
                st.info(f"**Silence Threshold:** {result['parameters_used']['silence_threshold_db']} dB")
            with param_col2:
                st.info(f"**Min Pause Duration:** {result['parameters_used']['min_pause_duration_sec']} sec")

            # Waveform visualization
            st.header("📈 Audio Waveform with Pauses")
            if result['plot_image']:
                st.image(f"data:image/png;base64,{result['plot_image']}", use_container_width=True)


            # Full transcript
            st.header("📄 Full Transcript")
            if result['transcript']:
                with st.expander("View Full Transcript"):
                    st.text_area("Transcribed text:", result['transcript'], height=100)

            # Analysis interpretation
            st.header("🎯 Analysis Interpretation")

            total_words = result['summary']['total_words']
            words_with_pauses = result['summary']['words_with_pauses']
            pause_ratio = (words_with_pauses / total_words) * 100 if total_words > 0 else 0

            if words_with_pauses == 0:
                st.info("**No pauses detected around words** - Speech appears fluent without hesitations.")
            elif pause_ratio > 30:
                st.warning(f"**High pause frequency ({pause_ratio:.1f}% of words)** - Many words have pauses before/after them. May indicate hesitation or careful articulation.")
            elif pause_ratio > 15:
                st.info(f"**Moderate pause frequency ({pause_ratio:.1f}% of words)** - Some words have pauses, which is normal in conversational speech.")
            else:
                st.success(f"**Low pause frequency ({pause_ratio:.1f}% of words)** - Few words have pauses, indicating fluent speech.")

            # Tips for parameter adjustment
            with st.expander("💡 Tips for Parameter Adjustment"):
                st.markdown("""
                **Silence Threshold (dB):**
                - **Higher values** (closer to 0): Only very quiet segments are detected as pauses
                - **Lower values** (more negative): More segments are detected as pauses
                - Typical range: -40 to -30 dB for clean recordings

                **Minimum Pause Duration:**
                - **Shorter durations** (0.05-0.1s): Detect brief hesitations and micro-pauses
                - **Longer durations** (0.2-0.5s): Focus on significant pauses only
                - Consider your analysis goals: natural speech patterns vs. deliberate pauses
                """)

        else:
            st.error(f"Analysis failed: {result['error']}")

    # Instructions
    st.sidebar.header("📖 How to Use")
    st.sidebar.markdown("""
    **Steps:**
    1. Upload an audio file
    2. Adjust pause detection parameters
    3. Click 'Analyze Pauses' or change parameters to auto-update
    4. Review results and download CSV

    **Understanding Results:**
    - **Top plot**: Audio waveform with red pause overlays
    - **Bottom plot**: Word timeline showing pause locations
    - **Pink rows** in table = words with pauses
    - **Green rows** in table = words without pauses
    - **Shows**: Exact pause duration before/after each word
    """)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("⏸️ Pause Analyzer v1.0")