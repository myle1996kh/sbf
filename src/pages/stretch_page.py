import streamlit as st
import os
import tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.analyzers.stretch_analyzer import analyze_stretch, update_stretch_classification, get_stretch_statistics

def stretch_analysis_page():
    """Streamlit page for stretch analysis with dynamic controls."""

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📏 Stretch Analysis")
        st.markdown("Analyze speech stretch patterns by measuring word duration per syllable")
    with col2:
        st.metric("Analysis Type", "Stretch", help="Measures pronunciation speed at word level")

    # Load API key from environment
    from dotenv import load_dotenv
    load_dotenv()

    # Check API key (only needed for OpenAI method)
    api_key = os.getenv("OPENAI_API_KEY")

    # Sidebar controls
    st.sidebar.header("⚙️ Stretch Analysis Parameters")

    # Method selection
    from src.transcribers.forcealign_transcriber import check_forcealign_availability, install_forcealign_instructions, compare_methods_info

    analysis_method = st.sidebar.selectbox(
        "Analysis Method",
        options=["OpenAI Whisper", "ForceAlign", "Whisper + ForceAlign (Hybrid)", "Deepgram + ForceAlign (Hybrid)"],
        index=0,
        help="Choose the method for word-level timing analysis"
    )

    # Show detailed method comparison
    with st.sidebar.expander("📊 Compare Methods"):
        method_info = compare_methods_info()

        st.markdown("### 🔄 OpenAI Whisper")
        st.markdown("**✅ Pros:**")
        for pro in method_info["openai"]["pros"]:
            st.markdown(f"- {pro}")
        st.markdown("**❌ Cons:**")
        for con in method_info["openai"]["cons"]:
            st.markdown(f"- {con}")
        st.markdown(f"**💡 Best for:** {method_info['openai']['best_for']}")

        st.markdown("---")
        st.markdown("### 🎯 ForceAlign")
        st.markdown("**✅ Pros:**")
        for pro in method_info["forcealign"]["pros"]:
            st.markdown(f"- {pro}")
        st.markdown("**❌ Cons:**")
        for con in method_info["forcealign"]["cons"]:
            st.markdown(f"- {con}")
        st.markdown(f"**💡 Best for:** {method_info['forcealign']['best_for']}")

    # Method-specific controls
    if analysis_method == "OpenAI Whisper":
        # Check API key for OpenAI
        if not api_key:
            st.sidebar.error("❌ OpenAI API Key not found")
            st.sidebar.info("💡 Set OPENAI_API_KEY in .env file")
            st.error("❌ OpenAI API Key required for OpenAI Whisper method. Please set OPENAI_API_KEY in your .env file or switch to ForceAlign method.")
            st.stop()
        else:
            st.sidebar.success("✅ API Key loaded from .env")

        # Model selection for OpenAI
        transcription_model = st.sidebar.selectbox(
            "Transcription Model",
            options=["whisper-1", "gpt-4o-transcribe"],
            index=0,  # Default to whisper-1
            help="whisper-1: Supports word timestamps (required for stretch analysis)\ngpt-4o-transcribe: Better accuracy but no word timestamps"
        )

        # Show model info
        if transcription_model == "gpt-4o-transcribe":
            st.sidebar.warning("⚠️ GPT-4o-transcribe doesn't support word timestamps. Will auto-switch to whisper-1 for stretch analysis.")
        else:
            st.sidebar.success("✅ Whisper-1 supports word timestamps for stretch analysis.")

    elif analysis_method == "Whisper + ForceAlign (Hybrid)":
        # Whisper+ForceAlign hybrid - needs both OpenAI and ForceAlign
        transcription_model = None

        # Check OpenAI API key
        if not api_key:
            st.sidebar.error("❌ OpenAI API Key not found")
            st.sidebar.info("💡 Set OPENAI_API_KEY in .env file")
            st.error("❌ OpenAI API Key required for Whisper+ForceAlign. Please set OPENAI_API_KEY in your .env file.")
            st.stop()
        else:
            st.sidebar.success("✅ OpenAI API Key loaded")

        # Check ForceAlign
        if check_forcealign_availability():
            st.sidebar.success("✅ ForceAlign is available")
        else:
            st.sidebar.error("❌ ForceAlign not installed")
            st.sidebar.markdown(install_forcealign_instructions())
            st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
            st.stop()

        st.sidebar.info("🎯 Best combo: Whisper accuracy + ForceAlign precision!")

    elif analysis_method == "Deepgram + ForceAlign (Hybrid)":
        # Hybrid method - needs both Deepgram and ForceAlign
        transcription_model = None

        # Check Deepgram API key
        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        if not deepgram_key:
            st.sidebar.error("❌ Deepgram API Key not found")
            st.sidebar.info("💡 Set DEEPGRAM_API_KEY in .env file")
            st.error("❌ Deepgram API Key required for hybrid method. Please set DEEPGRAM_API_KEY in your .env file.")
            st.stop()
        else:
            st.sidebar.success("✅ Deepgram API Key loaded")

        # Check ForceAlign availability
        if check_forcealign_availability():
            st.sidebar.success("✅ ForceAlign is available")
        else:
            st.sidebar.error("❌ ForceAlign not installed")
            st.sidebar.markdown(install_forcealign_instructions())
            st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
            st.stop()

        # Check Deepgram SDK
        from src.transcribers.deepgram_transcriber import check_deepgram_availability, install_deepgram_instructions
        if check_deepgram_availability():
            st.sidebar.success("✅ Deepgram SDK is available")
        else:
            st.sidebar.error("❌ Deepgram SDK not installed")
            st.sidebar.markdown(install_deepgram_instructions())
            st.error("❌ Deepgram SDK not available. Please install it with: pip install deepgram-sdk")
            st.stop()

        st.sidebar.info("🎯 Best of both worlds: Deepgram transcription + ForceAlign timing!")

    else:
        # ForceAlign only method
        transcription_model = None  # Not used for ForceAlign

        # Check ForceAlign availability
        if check_forcealign_availability():
            st.sidebar.success("✅ ForceAlign is available")
            st.sidebar.info("💡 No API key required - works offline!")
        else:
            st.sidebar.error("❌ ForceAlign not installed")
            st.sidebar.markdown(install_forcealign_instructions())
            st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
            st.stop()

    # Dynamic threshold control
    stretch_threshold = st.sidebar.slider(
        "Stretch Threshold (sec/syllable)",
        min_value=0.1,
        max_value=1.0,
        value=0.38,
        step=0.05,
        help="Recommended: 0.3-0.4s for normal speech analysis. Words above this threshold are 'Stretched'"
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
        # Check if we need to re-analyze file or just update threshold
        file_changed = ('uploaded_file_name' not in st.session_state or
                       st.session_state['uploaded_file_name'] != uploaded_file.name)

        if file_changed or st.button("🔄 Analyze Speech Stretch", type="primary"):
            with st.spinner("Transcribing and analyzing speech stretch..."):
                try:
                    # Save uploaded file to temporary location
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name

                    # Run stretch analysis with selected method and model
                    if analysis_method == "ForceAlign":
                        method = "forcealign"
                    elif analysis_method == "Deepgram + ForceAlign (Hybrid)":
                        method = "deepgram_forcealign"
                    elif analysis_method == "Whisper + ForceAlign (Hybrid)":
                        method = "whisper_forcealign"
                    else:
                        method = "openai"

                    result = analyze_stretch(temp_path, stretch_threshold=stretch_threshold, model=transcription_model, method=method)

                    # Clean up temp file
                    os.unlink(temp_path)

                    # Store results in session state
                    st.session_state['stretch_result'] = result
                    st.session_state['uploaded_file_name'] = uploaded_file.name
                    st.session_state['original_word_table'] = result['word_table'].copy() if result['success'] else None

                    if result['success']:
                        st.success("✅ Stretch analysis completed!")
                    else:
                        st.error(f"❌ Analysis failed: {result['error']}")

                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")

    # Display results with real-time threshold updates
    if 'stretch_result' in st.session_state and 'original_word_table' in st.session_state:
        result = st.session_state['stretch_result']

        if result['success'] and st.session_state['original_word_table'] is not None:
            # Update classifications with current threshold (real-time)
            current_table = update_stretch_classification(
                st.session_state['original_word_table'],
                stretch_threshold
            )

            # Get updated statistics
            current_stats = get_stretch_statistics(current_table, stretch_threshold)

            # Summary metrics
            st.header("📊 Stretch Analysis Summary")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Words", current_stats['total_words'])

            with col2:
                st.metric("Stretched Words", current_stats['stretched_words'])

            with col3:
                st.metric("Normal Words", current_stats['normal_words'])

            with col4:
                st.metric("Stretch %", f"{current_stats['stretch_percentage']}%")

            # Additional metrics from original analysis
            col5, col6, col7 = st.columns(3)

            with col5:
                st.metric("Avg Stretch Score", f"{result['summary']['avg_stretch_score']} sec/syl")

            with col6:
                st.metric("Max Stretch Score", f"{result['summary']['max_stretch_score']} sec/syl")

            with col7:
                real_start = result['summary'].get('real_start_time', 0)
                real_end = result['summary'].get('real_end_time', 0)
                speech_duration = result['summary']['total_speech_duration']
                st.metric(
                    "Real Speech Duration",
                    f"{speech_duration}s",
                    help=f"From {real_start}s to {real_end}s (excludes silence at start/end)"
                )

            # Current parameters display
            st.subheader("🎛️ Analysis Configuration")
            param_col1, param_col2, param_col3 = st.columns(3)
            with param_col1:
                st.info(f"**Stretch Threshold:** {stretch_threshold} seconds per syllable")
            with param_col2:
                method_used = result['parameters_used'].get('analysis_method', 'openai')
                if method_used == "forcealign":
                    method_display = "🎯 ForceAlign (Free/Offline)"
                elif method_used == "deepgram_forcealign":
                    method_display = "🚀 Deepgram + ForceAlign Hybrid"
                elif method_used == "whisper_forcealign":
                    method_display = "🎯 Whisper + ForceAlign Hybrid"
                else:
                    method_display = "🔄 OpenAI Whisper"
                st.info(f"**Method:** {method_display}")
            with param_col3:
                timing_method = result['parameters_used'].get('timing_method', 'transcription_based')
                if timing_method == "energy_corrected":
                    st.success(f"**Timing:** ⚡ Energy-Corrected")
                else:
                    model_used = result['parameters_used'].get('transcription_model', 'N/A')
                    if model_used != 'N/A':
                        st.info(f"**Model:** {model_used}")
                    else:
                        st.info(f"**Timing:** Transcription-based")

            # Visualization
            st.header("📈 Stretch Score Visualization")

            if len(current_table) > 0:
                # Create interactive plot with Plotly
                fig = go.Figure()

                # Color points based on classification
                # Stretched = Green (#4ecdc4), Normal = Red (#ff6b6b)
                colors = ['#4ecdc4' if x == 'Stretched' else '#ff6b6b' for x in current_table['Classification']]

                fig.add_trace(go.Scatter(
                    x=list(range(len(current_table))),
                    y=current_table['Stretch Score'],
                    mode='markers+lines',
                    marker=dict(color=colors, size=8),
                    text=current_table['Word'],
                    hovertemplate='<b>%{text}</b><br>Stretch Score: %{y}<br>Word #: %{x}<extra></extra>',
                    name='Words'
                ))

                # Add threshold line
                fig.add_hline(
                    y=stretch_threshold,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Stretch Threshold"
                )

                fig.update_layout(
                    title="Stretch Score per Word",
                    xaxis_title="Word Order",
                    yaxis_title="Stretch Score (sec/syllable)",
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)


            # Detailed word table
            st.header("📋 Detailed Word Analysis")

            # Show timing correction info if applied
            timing_method = result['parameters_used'].get('timing_method', 'transcription_based')
            show_corrected_times = True  # Default to True

            if timing_method == "energy_corrected":
                real_start = result['summary'].get('real_start_time', 0)
                transcription_start = 0.0  # First word started at 0.0 in transcription
                time_offset = real_start - transcription_start

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"ℹ️ **Timing Correction Applied:** Real speech starts at {real_start:.3f}s (excludes {time_offset:.3f}s of initial silence).")
                with col2:
                    show_corrected_times = st.checkbox("Show Corrected Times", value=True, help="Add offset to show when words actually occur in real time")

            if len(current_table) > 0:
                # Style the dataframe
                def style_stretch_table(df):
                    def highlight_stretch(row):
                        # Stretched = Green background, Normal = Red background
                        if row['Classification'] == 'Stretched':
                            return ['background-color: #e8f5e8'] * len(row)  # Light green
                        else:
                            return ['background-color: #ffebee'] * len(row)  # Light red

                    return df.style.apply(highlight_stretch, axis=1)

                # Filter options
                filter_option = st.selectbox(
                    "Filter table:",
                    ["All Words", "Stretched Only", "Normal Only"]
                )

                filtered_table = current_table.copy()

                # Apply time correction if requested
                if show_corrected_times and timing_method == "energy_corrected":
                    real_start = result['summary'].get('real_start_time', 0)
                    time_offset = real_start

                    filtered_table = filtered_table.copy()
                    filtered_table['Start'] = filtered_table['Start'] + time_offset
                    filtered_table['End'] = filtered_table['End'] + time_offset

                # Apply filter
                if filter_option == "Stretched Only":
                    filtered_table = filtered_table[filtered_table['Classification'] == 'Stretched']
                elif filter_option == "Normal Only":
                    filtered_table = filtered_table[filtered_table['Classification'] == 'Normal']

                if len(filtered_table) > 0:
                    styled_df = style_stretch_table(filtered_table)
                    st.dataframe(styled_df, use_container_width=True)

                    # Download CSV option
                    csv = filtered_table.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Stretch Analysis CSV",
                        data=csv,
                        file_name=f"stretch_analysis_{uploaded_file.name.split('.')[0]}.csv",
                        mime="text/csv"
                    )
                else:
                    st.info(f"No words match the '{filter_option}' filter.")

            # Full transcript
            st.header("📄 Full Transcript")
            if result['transcript']:
                with st.expander("View Full Transcript"):
                    st.text_area("Transcribed text:", result['transcript'], height=150)

            # Analysis interpretation
            st.header("🎯 Analysis Interpretation")

            stretch_percentage = current_stats['stretch_percentage']

            if stretch_percentage > 40:
                st.warning(f"**High stretch ratio ({stretch_percentage}%)** - Many words are pronounced slowly. This could indicate careful articulation, emphasis, or speech difficulties.")
            elif stretch_percentage > 20:
                st.info(f"**Moderate stretch ratio ({stretch_percentage}%)** - Some words are stretched, which is normal in expressive speech.")
            elif stretch_percentage > 0:
                st.success(f"**Low stretch ratio ({stretch_percentage}%)** - Most words are pronounced at normal speed.")
            else:
                st.success("**No stretched words detected** - All words are within normal pronunciation speed.")

            # Show most stretched words
            if len(current_table) > 0:
                stretched_words = current_table[current_table['Classification'] == 'Stretched']
                if len(stretched_words) > 0:
                    st.subheader("🔍 Most Stretched Words")
                    top_stretched = stretched_words.nlargest(5, 'Stretch Score')[['Word', 'Stretch Score', 'Duration', 'Syllables']]
                    st.dataframe(top_stretched, use_container_width=True)

            # Tips for parameter adjustment
            with st.expander("💡 Research-Based Threshold Guide"):
                st.markdown("""
                **Normal Speech Research:**
                - **Fast speech**: 0.10-0.17s per syllable
                - **Normal speech**: 0.17-0.33s per syllable
                - **Slow speech**: 0.33-0.50s per syllable
                - **Stretched speech**: >0.40s per syllable

                **Recommended Thresholds:**
                - **0.30s**: Sensitive - catches moderately slow words
                - **0.35s**: Balanced - good for general analysis
                - **0.40s**: Conservative - only clearly stretched words
                - **0.50s**: Very conservative - extremely slow words only

                **For Different Purposes:**
                - **Speech therapy**: 0.30-0.35s (catch subtle issues)
                - **Public speaking**: 0.35-0.40s (emphasis detection)
                - **General analysis**: 0.35s (recommended default)
                """)

        else:
            st.error(f"Analysis failed: {result['error']}")

    # Instructions
    st.sidebar.header("📖 How to Use")
    st.sidebar.markdown("""
    **Steps:**
    1. Upload an audio file
    2. Adjust stretch threshold
    3. Click 'Analyze Speech Stretch'
    4. Threshold updates are real-time
    5. Review results and download CSV

    **Understanding Results:**
    - **Red points** = stretched words
    - **Green points** = normal words
    - **Red line** = current threshold
    """)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("📏 Stretch Analyzer v1.0")