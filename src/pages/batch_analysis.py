import streamlit as st
import os
import tempfile
import pandas as pd
from src.audio_analyzer import analyze_audio_file
from src.analyzers.pause_word_analyzer import analyze_pause_with_words
from src.analyzers.stretch_analyzer import analyze_stretch
import concurrent.futures
from threading import Lock
from src.utils.volume_scoring import calculate_volume_score, create_results_table_data
import numpy as np
import plotly.graph_objects as go
from src.utils.visualizations import (
    plot_volume_histogram_individual,
    plot_velocity_gauge,
    plot_velocity_metrics_table,
    create_volume_summary_chart,
    create_combined_metrics_overview
)

# Thread-safe counter for progress
progress_lock = Lock()

def batch_analyze_page():
    st.title("📊 Batch Audio Analysis")
    st.markdown("Upload multiple audio files and choose your analysis type")

    # Analysis type selection
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Volume & Velocity", "Pause Analysis", "Stretch Analysis"],
        help="Choose which type of analysis to run on your batch of files"
    )

    # Load API key from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # API Key check (conditional based on analysis type)
    api_key = os.getenv("OPENAI_API_KEY")

    # Check if API key is needed for current analysis type
    needs_api_key = analysis_type in ["Volume & Velocity", "Pause Analysis"]

    if analysis_type == "Stretch Analysis":
        # For stretch analysis, API key depends on method selection
        pass  # Will be handled in stretch-specific section
    elif needs_api_key:
        if api_key:
            st.sidebar.success("✅ API Key loaded from .env file")
        else:
            st.error("⚠️ Please set OPENAI_API_KEY in .env file")
            st.info("💡 Create a .env file in the project root with: OPENAI_API_KEY=your_key_here")
            return

    # Analysis-specific parameters
    if analysis_type == "Pause Analysis":
        st.sidebar.header("⚙️ Pause Parameters")
        silence_db = st.sidebar.slider("Silence Threshold (dB)", -60.0, -20.0, -38.0, 1.0)
        min_pause_sec = st.sidebar.slider("Min Pause Duration (sec)", 0.05, 2.0, 0.5, 0.05)

    elif analysis_type == "Stretch Analysis":
        st.sidebar.header("⚙️ Stretch Parameters")

        # Method selection
        from src.transcribers.forcealign_transcriber import check_forcealign_availability, install_forcealign_instructions

        analysis_method = st.sidebar.selectbox(
            "Analysis Method",
            options=["OpenAI Whisper", "ForceAlign", "Whisper + ForceAlign (Hybrid)", "Deepgram + ForceAlign (Hybrid)"],
            index=0,
            help="Choose the method for word-level timing analysis"
        )

        # Method-specific controls
        if analysis_method == "OpenAI Whisper":
            # Check API key for OpenAI
            if not api_key:
                st.sidebar.error("❌ OpenAI API Key not found")
                st.error("❌ OpenAI API Key required for OpenAI Whisper method. Please set OPENAI_API_KEY in your .env file or switch to ForceAlign method.")
                return
            else:
                st.sidebar.success("✅ API Key loaded from .env")

            transcription_model = st.sidebar.selectbox("Transcription Model", ["whisper-1", "gpt-4o-transcribe"], index=0)

            if transcription_model == "gpt-4o-transcribe":
                st.sidebar.warning("⚠️ Will auto-switch to whisper-1 for word timestamps")

        elif analysis_method == "Deepgram + ForceAlign (Hybrid)":
            # Hybrid method - needs both Deepgram and ForceAlign
            transcription_model = None

            # Check Deepgram API key
            deepgram_key = os.getenv("DEEPGRAM_API_KEY")
            if not deepgram_key:
                st.sidebar.error("❌ Deepgram API Key not found")
                st.error("❌ Deepgram API Key required for hybrid method. Please set DEEPGRAM_API_KEY in your .env file.")
                return
            else:
                st.sidebar.success("✅ Deepgram API Key loaded")

            # Check ForceAlign availability
            if check_forcealign_availability():
                st.sidebar.success("✅ ForceAlign is available")
            else:
                st.sidebar.error("❌ ForceAlign not installed")
                st.sidebar.markdown(install_forcealign_instructions())
                st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
                return

            # Check Deepgram SDK
            from src.transcribers.deepgram_transcriber import check_deepgram_availability
            if check_deepgram_availability():
                st.sidebar.success("✅ Deepgram SDK is available")
            else:
                st.sidebar.error("❌ Deepgram SDK not installed")
                st.error("❌ Deepgram SDK not available. Please install it with: pip install deepgram-sdk")
                return

            st.sidebar.info("🎯 Best of both: Deepgram transcription + ForceAlign timing!")

        elif analysis_method == "Whisper + ForceAlign (Hybrid)":
            # Whisper + ForceAlign hybrid method
            transcription_model = None

            # Check OpenAI API key
            if not api_key:
                st.sidebar.error("❌ OpenAI API Key not found")
                st.error("❌ OpenAI API Key required for Whisper+ForceAlign hybrid. Please set OPENAI_API_KEY in your .env file or switch to ForceAlign method.")
                return
            else:
                st.sidebar.success("✅ OpenAI API Key loaded")

            # Check ForceAlign availability
            if check_forcealign_availability():
                st.sidebar.success("✅ ForceAlign is available")
            else:
                st.sidebar.error("❌ ForceAlign not installed")
                st.sidebar.markdown(install_forcealign_instructions())
                st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
                return

            st.sidebar.info("🎯 Best combo: Whisper accuracy + ForceAlign precision!")

        else:
            # ForceAlign method
            transcription_model = None

            # Check ForceAlign availability
            if check_forcealign_availability():
                st.sidebar.success("✅ ForceAlign is available")
                st.sidebar.info("💡 No API key required - works offline!")
            else:
                st.sidebar.error("❌ ForceAlign not installed")
                st.sidebar.markdown(install_forcealign_instructions())
                st.error("❌ ForceAlign not available. Please install it with: pip install forcealign")
                return

        stretch_threshold = st.sidebar.slider("Stretch Threshold (sec/syllable)", 0.1, 1.0, 0.38, 0.05)

    # File upload section
    st.header("📁 Upload Audio Files")
    uploaded_files = st.file_uploader(
        "Choose audio files",
        type=['wav', 'mp3', 'm4a', 'flac'],
        accept_multiple_files=True,
        help="Supported formats: WAV, MP3, M4A, FLAC"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")

        # Display file list
        with st.expander("📋 Uploaded Files"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size/1024:.1f} KB)")

        # Analysis button
        if st.button("🚀 Start Batch Analysis", type="primary"):
            if analysis_type == "Volume & Velocity":
                analyze_batch_files(uploaded_files, analysis_type)
            elif analysis_type == "Pause Analysis":
                analyze_batch_pause(uploaded_files, silence_db, min_pause_sec)
            elif analysis_type == "Stretch Analysis":
                if analysis_method == "ForceAlign":
                    method = "forcealign"
                elif analysis_method == "Deepgram + ForceAlign (Hybrid)":
                    method = "deepgram_forcealign"
                elif analysis_method == "Whisper + ForceAlign (Hybrid)":
                    method = "whisper_forcealign"
                else:
                    method = "openai"
                analyze_batch_stretch(uploaded_files, stretch_threshold, transcription_model, method)

def analyze_batch_files(uploaded_files, analysis_type):
    """Process multiple files and display results"""

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    results = []
    temp_files = []

    try:
        # Save all files to temp directory first
        status_text.text("📁 Preparing files...")
        for i, file in enumerate(uploaded_files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(file.getvalue())
                temp_files.append((tmp_file.name, file.name))
            progress_bar.progress((i + 1) / (len(uploaded_files) * 2))

        # Analyze files in parallel
        status_text.text("🔄 Analyzing files...")

        def analyze_single_file(file_info):
            temp_path, original_name = file_info
            result = analyze_audio_file(temp_path)
            result['original_filename'] = original_name
            return result

        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_file = {executor.submit(analyze_single_file, file_info): file_info[1] for file_info in temp_files}

            completed = 0
            for future in concurrent.futures.as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    progress_bar.progress(0.5 + (completed / len(temp_files)) * 0.5)
                    status_text.text(f"✅ Completed: {filename}")
                except Exception as e:
                    st.error(f"❌ Error analyzing {filename}: {str(e)}")

        # Clean up temp files
        for temp_path, _ in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass

        # Display results
        display_batch_results(results)

        # Store results in session state for download
        st.session_state['batch_results'] = results

    except Exception as e:
        st.error(f"❌ Batch analysis failed: {str(e)}")
        # Clean up on error
        for temp_path, _ in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass

def display_batch_results(results):
    """Display comprehensive batch analysis results"""

    st.header("📊 Batch Analysis Results")

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    successful_analyses = [r for r in results if r['analysis_status']['overall_success']]

    with col1:
        st.metric("Total Files", len(results))
    with col2:
        st.metric("Successful", len(successful_analyses))
    with col3:
        st.metric("Failed", len(results) - len(successful_analyses))
    with col4:
        success_rate = (len(successful_analyses) / len(results)) * 100 if results else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")

    # Detailed results tables
    if successful_analyses:

        # Process files and apply volume scoring
        for result in successful_analyses:
            if 'error' not in result['volume_analysis']:
                scored_volume = calculate_volume_score(result['volume_analysis'])
                result['volume_analysis'] = scored_volume  # Update with scored version

        # Volume Results Table (SBF Style)
        st.subheader("📋 Bảng kết quả chi tiết Volume")

        # Prepare data for SBF-style table
        volume_results = []
        file_labels = []

        for result in successful_analyses:
            if 'error' not in result['volume_analysis']:
                volume_results.append(result['volume_analysis'])
                file_labels.append(result['original_filename'])

        if volume_results:
            # Create table data with scoring
            table_data = create_results_table_data(volume_results, file_labels)
            results_df = pd.DataFrame(table_data)

            # Style the dataframe like SBF
            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "STT": st.column_config.NumberColumn("STT", width="small"),
                    "Tên file": st.column_config.TextColumn("Tên file", width="medium"),
                    "Min (dBFS)": st.column_config.TextColumn("Min", width="small"),
                    "Max (dBFS)": st.column_config.TextColumn("Max", width="small"),
                    "Avg (dBFS)": st.column_config.TextColumn("Avg", width="small"),
                    "Range (dB)": st.column_config.TextColumn("Range", width="small"),
                    "Coverage (%)": st.column_config.TextColumn("Coverage", width="small"),
                    "Điểm": st.column_config.TextColumn("Điểm", width="small"),
                    "Xếp loại": st.column_config.TextColumn("Xếp loại", width="medium"),
                    "Trạng thái": st.column_config.TextColumn("TT", width="small"),
                    "So với chuẩn": st.column_config.TextColumn("So với chuẩn", width="medium")
                }
            )

            # === OVERALL SUMMARY (SBF Style) ===
            all_frame_values = []
            for result in volume_results:
                all_frame_values.extend(result["frame_values"])

            if all_frame_values:
                Q1 = np.percentile(all_frame_values, 25)
                Q3 = np.percentile(all_frame_values, 75)
                IQR = Q3 - Q1
                valid_values = [v for v in all_frame_values if Q1 - 1.5 * IQR <= v <= Q3 + 1.5 * IQR]

                overall_result = {
                    "volume_min": min(valid_values),
                    "volume_max": max(valid_values),
                    "volume_avg": np.mean(valid_values),
                    "volume_range": max(valid_values) - min(valid_values),
                    "frame_values": valid_values,
                    "coverage_vs_target": sum(-30 <= v <= -10 for v in valid_values) / len(valid_values) * 100
                }

                overall_scored = calculate_volume_score(overall_result)

                st.subheader("📊 Tổng kết chung cho tất cả file")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("📈 Điểm tổng", f"{overall_scored['score']:.1f}/100")
                with col2:
                    st.metric("🎯 Xếp loại", overall_scored['grade'].split()[1])
                with col3:
                    st.metric("📊 Coverage", f"{overall_scored['coverage_vs_target']:.1f}%")
                with col4:
                    st.metric("🔊 Trạng thái", overall_scored['comparison']['user_vs_normal'])

                # Recommendations
                if overall_scored['recommendations']:
                    st.subheader("💡 Nhận xét và gợi ý cải thiện")
                    for rec in overall_scored['recommendations']:
                        st.info(rec)

        # Velocity Results Table (SBF Style)
        st.subheader("📋 Bảng kết quả chi tiết Velocity")

        velocity_data = []
        for i, result in enumerate(successful_analyses, 1):
            velocity = result['velocity_analysis']
            if 'error' not in velocity:
                velocity_data.append({
                    "STT": i,
                    "File": result['original_filename'],
                    "Thời gian bắt đầu (s)": velocity['real_start_time'],
                    "Thời gian kết thúc (s)": velocity['real_end_time'],
                    "Thời gian thực tế (s)": velocity['duration_spoken'],
                    "Tổng từ": velocity['word_count_total'],
                    "Từ hợp lệ": velocity['word_count_clean'],
                    "WPS (từ/giây)": velocity['wps'],
                    "WPM (từ/phút)": velocity['wpm'],
                    "Xếp loại": velocity['velocity_level']
                })

        if velocity_data:
            velocity_df = pd.DataFrame(velocity_data)
            st.dataframe(
                velocity_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "STT": st.column_config.NumberColumn("STT", width="small"),
                    "File": st.column_config.TextColumn("File", width="medium"),
                    "Thời gian bắt đầu (s)": st.column_config.NumberColumn("Start (s)", width="small"),
                    "Thời gian kết thúc (s)": st.column_config.NumberColumn("End (s)", width="small"),
                    "Thời gian thực tế (s)": st.column_config.NumberColumn("Duration (s)", width="small"),
                    "Tổng từ": st.column_config.NumberColumn("Total Words", width="small"),
                    "Từ hợp lệ": st.column_config.NumberColumn("Clean Words", width="small"),
                    "WPS (từ/giây)": st.column_config.NumberColumn("WPS", width="small"),
                    "WPM (từ/phút)": st.column_config.NumberColumn("WPM", width="small"),
                    "Xếp loại": st.column_config.TextColumn("Level", width="medium")
                }
            )

            # Velocity summary statistics
            avg_wps = velocity_df['WPS (từ/giây)'].mean()
            level_counts = velocity_df['Xếp loại'].value_counts()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Average WPS", f"{avg_wps:.2f}")
            with col2:
                st.metric("📈 Most Common Level", level_counts.index[0])
            with col3:
                st.metric("🎯 Files at This Level", level_counts.iloc[0])

        # Individual File Details
        st.subheader("📝 Individual File Details")

        for result in results:
            filename = result['original_filename']
            status = result['analysis_status']

            with st.expander(f"📄 {filename} {'✅' if status['overall_success'] else '❌'}"):

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**🔊 Volume Analysis:**")
                    volume = result['volume_analysis']
                    if 'error' in volume:
                        st.error(f"Error: {volume['error']}")
                    else:
                        # Apply volume scoring if not already applied
                        if 'score' not in volume:
                            volume = calculate_volume_score(volume)
                            result['volume_analysis'] = volume

                        st.write(f"- Min/Max/Avg: {volume['volume_min']}/{volume['volume_max']}/{volume['volume_avg']} dBFS")
                        st.write(f"- Range: {volume['volume_range']} dBFS")
                        st.write(f"- Target Coverage: {volume['coverage_vs_target']}%")
                        st.write(f"- Score: {volume['score']}/100")
                        st.write(f"- Grade: {volume['grade']}")

                        # Add assessment field
                        if volume['recommendations']:
                            st.write("**📝 Đánh giá:**")
                            main_assessment = volume['recommendations'][0]  # First recommendation as main assessment
                            st.write(f"- {main_assessment}")
                        else:
                            st.write("**📝 Đánh giá:** Excellent volume control!")

                with col2:
                    st.write("**🏃 Velocity Analysis:**")
                    velocity = result['velocity_analysis']
                    if 'error' in velocity:
                        st.error(f"Error: {velocity['error']}")
                    else:
                        st.write(f"- Words: {velocity['word_count_clean']}/{velocity['word_count_total']} (clean/total)")
                        st.write(f"- Duration: {velocity['duration_spoken']}s")
                        st.write(f"- Speed: {velocity['wps']} WPS ({velocity['wpm']} WPM)")
                        st.write(f"- Level: {velocity['velocity_level']}")
                        st.write(f"- Detailed: {velocity['detailed_explanation']['velocity_calculation']}")

                        if velocity['transcript']:
                            st.write("**📄 Transcript:**")
                            st.text_area("", velocity['transcript'], height=80, key=f"transcript_{filename}")

                        if velocity['filled_pauses']:
                            st.write(f"**🗣️ Filled Pauses:** {', '.join(velocity['filled_pauses'])} (Count: {len(velocity['filled_pauses'])})")

                # Add visualizations section
                st.write("**📈 Visualizations:**")

                # Create tabs for different visualizations
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Volume Chart", "Velocity Gauge", "Detailed Metrics"])

                with viz_tab1:
                    # Volume histogram for this file
                    volume = result['volume_analysis']
                    if 'error' not in volume and 'frame_values' in volume:
                        plot_volume_histogram_individual(volume, filename)
                    else:
                        st.warning("Volume visualization not available")

                with viz_tab2:
                    # Velocity gauge for this file
                    velocity = result['velocity_analysis']
                    if 'error' not in velocity:
                        plot_velocity_gauge(velocity, filename)
                    else:
                        st.warning("Velocity visualization not available")

                with viz_tab3:
                    # Detailed metrics table
                    velocity = result['velocity_analysis']
                    if 'error' not in velocity:
                        plot_velocity_metrics_table(velocity)
                    else:
                        st.warning("Velocity metrics not available")

        # Summary visualizations
        st.subheader("📈 Summary Visualizations")

        # Extract data for summary charts
        volume_data_for_viz = []
        velocity_data_for_viz = []
        filenames_for_viz = []

        for result in successful_analyses:
            if 'error' not in result['volume_analysis']:
                volume_data_for_viz.append(result['volume_analysis'])
            if 'error' not in result['velocity_analysis']:
                velocity_data_for_viz.append(result['velocity_analysis'])
            filenames_for_viz.append(result['original_filename'])

        if volume_data_for_viz and velocity_data_for_viz:
            # Create summary visualization tabs
            summary_tab1, summary_tab2, summary_tab3 = st.tabs(["Volume Summary", "Combined Overview", "Export Data"])

            with summary_tab1:
                st.write("**Volume Analysis Summary Across All Files**")
                create_volume_summary_chart(volume_data_for_viz, filenames_for_viz)

            with summary_tab2:
                st.write("**Combined Volume & Velocity Metrics Overview**")
                create_combined_metrics_overview(volume_data_for_viz, velocity_data_for_viz, filenames_for_viz)

            with summary_tab3:
                st.write("**Export Analysis Results**")
                if st.button("📊 Download Comprehensive Results as CSV"):
                    create_export_csv(successful_analyses)
        else:
            # Fallback export option
            st.subheader("📥 Export Results")
            if st.button("📊 Download Results as CSV"):
                create_export_csv(successful_analyses)

def create_export_csv(results):
    """Create downloadable CSV with all results"""

    export_data = []

    for result in results:
        filename = result['original_filename']
        volume = result['volume_analysis']
        velocity = result['velocity_analysis']

        row = {
            "Filename": filename,
            "Volume_Min_dBFS": volume.get('volume_min', ''),
            "Volume_Max_dBFS": volume.get('volume_max', ''),
            "Volume_Avg_dBFS": volume.get('volume_avg', ''),
            "Volume_Range_dBFS": volume.get('volume_range', ''),
            "Volume_Target_Coverage_Percent": volume.get('coverage_vs_target', ''),
            "Volume_Score": volume.get('score', '') if 'score' in volume else '',
            "Volume_Grade": volume.get('grade', '') if 'grade' in volume else '',
            "Total_Words": velocity.get('word_count_total', ''),
            "Clean_Words": velocity.get('word_count_clean', ''),
            "Duration_Seconds": velocity.get('duration_spoken', ''),
            "Real_Start_Time": velocity.get('real_start_time', ''),
            "Real_End_Time": velocity.get('real_end_time', ''),
            "WPS": velocity.get('wps', ''),
            "WPM": velocity.get('wpm', ''),
            "Velocity_Level": velocity.get('velocity_level', ''),
            "Filled_Pauses_Count": len(velocity.get('filled_pauses', [])),
            "Filled_Pauses_List": ', '.join(velocity.get('filled_pauses', [])),
            "Transcript": velocity.get('transcript', ''),
            "Velocity_Explanation": velocity.get('detailed_explanation', {}).get('velocity_calculation', '')
        }
        export_data.append(row)

    export_df = pd.DataFrame(export_data)
    csv = export_df.to_csv(index=False)

    st.download_button(
        label="📊 Download Comprehensive Results CSV",
        data=csv,
        file_name=f"audio_analysis_results_{len(results)}_files.csv",
        mime="text/csv",
        help="Download detailed results including volume scores, velocity metrics, and transcriptions"
    )

def analyze_batch_pause(uploaded_files, silence_db, min_pause_sec):
    """Process multiple files for pause analysis"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))

        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name

            # Run analysis
            result = analyze_pause_with_words(temp_path, silence_db=silence_db, min_pause_sec=min_pause_sec)

            # Add filename to result
            result['original_filename'] = uploaded_file.name

            # Clean up temp file
            os.unlink(temp_path)

            # Store full result (not just summary)
            results.append(result)

        except Exception as e:
            results.append({
                "original_filename": uploaded_file.name,
                "success": False,
                "error": str(e)
            })

    status_text.text("✅ Batch pause analysis completed!")
    progress_bar.progress(1.0)

    # Display comprehensive results
    display_batch_pause_results(results, silence_db, min_pause_sec)

def display_batch_pause_results(results, silence_db, min_pause_sec):
    """Display comprehensive batch pause analysis results with same info as single pause analysis"""

    st.header("📊 Batch Pause Analysis Results")

    # Summary statistics
    successful_results = [r for r in results if r.get('success', False)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Files", len(results))
    with col2:
        st.metric("Successful", len(successful_results))
    with col3:
        st.metric("Failed", len(results) - len(successful_results))
    with col4:
        success_rate = (len(successful_results) / len(results)) * 100 if results else 0
        st.metric("Success Rate", f"{success_rate:.1f}%")

    # Current parameters display
    st.subheader("🎛️ Analysis Parameters Used")
    param_col1, param_col2 = st.columns(2)
    with param_col1:
        st.info(f"**Silence Threshold:** {silence_db} dB")
    with param_col2:
        st.info(f"**Min Pause Duration:** {min_pause_sec} sec")

    if successful_results:
        # Summary table
        st.subheader("📋 Summary Table")
        summary_data = []
        for i, result in enumerate(successful_results, 1):
            summary = result['summary']
            total_words = summary['total_words']
            words_with_pauses = summary['words_with_pauses']
            pause_ratio = (words_with_pauses / total_words) * 100 if total_words > 0 else 0

            summary_data.append({
                "STT": i,
                "File": result['original_filename'],
                "Total Pauses": summary['total_pauses'],
                "Audio Duration (s)": summary['audio_duration'],
                "Total Words": total_words,
                "Words with Pauses": words_with_pauses,
                "Pause Ratio (%)": f"{pause_ratio:.1f}%"
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "STT": st.column_config.NumberColumn("STT", width="small"),
                "File": st.column_config.TextColumn("File", width="medium"),
                "Total Pauses": st.column_config.NumberColumn("Total Pauses", width="small"),
                "Audio Duration (s)": st.column_config.NumberColumn("Duration (s)", width="small"),
                "Total Words": st.column_config.NumberColumn("Total Words", width="small")
            }
        )

        # Overall Analysis Interpretation
        st.subheader("🎯 Overall Analysis Interpretation")

        # Calculate overall statistics
        total_pauses_all = sum(r['summary']['total_pauses'] for r in successful_results)
        total_words_all = sum(r['summary']['total_words'] for r in successful_results)
        total_words_with_pauses_all = sum(r['summary']['words_with_pauses'] for r in successful_results)
        overall_pause_ratio = (total_words_with_pauses_all / total_words_all) * 100 if total_words_all > 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Pauses", total_pauses_all)
        with col2:
            st.metric("📝 Total Words", total_words_all)
        with col3:
            st.metric("⏸️ Overall Pause Ratio", f"{overall_pause_ratio:.1f}%")

        # Interpretation message
        if total_words_with_pauses_all == 0:
            st.success("**Excellent fluency across all files** - No pauses detected around words. Speech appears very fluent without hesitations.")
        elif overall_pause_ratio > 30:
            st.warning(f"**High pause frequency across files ({overall_pause_ratio:.1f}% of words)** - Many words have pauses before/after them. May indicate hesitation or careful articulation.")
        elif overall_pause_ratio > 15:
            st.info(f"**Moderate pause frequency across files ({overall_pause_ratio:.1f}% of words)** - Some words have pauses, which is normal in conversational speech.")
        else:
            st.success(f"**Good fluency across files ({overall_pause_ratio:.1f}% of words)** - Few words have pauses, indicating generally fluent speech.")

        # Individual file results (same format as single pause analysis)
        st.subheader("📝 Individual File Results")

        for result in results:
            filename = result['original_filename']

            if result.get('success', False):
                with st.expander(f"📄 {filename} ✅"):
                    # Summary metrics for this file
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Total Pauses", result['summary']['total_pauses'])
                    with col2:
                        st.metric("Audio Duration", f"{result['summary']['audio_duration']}s")

                    # Waveform visualization
                    st.write("**📈 Audio Waveform with Pauses**")
                    if result.get('plot_image'):
                        st.image(f"data:image/png;base64,{result['plot_image']}", use_container_width=True)
                    else:
                        st.warning("Waveform visualization not available for this file")

                    # Full transcript
                    st.write("**📄 Full Transcript**")
                    if result.get('transcript'):
                        with st.expander("View Full Transcript"):
                            st.text_area("Transcribed text:", result['transcript'], height=100, key=f"transcript_{filename}")
                    else:
                        st.info("Transcript not available for this file")

                    # Analysis interpretation for this file
                    st.write("**🎯 Analysis Interpretation**")

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
            else:
                with st.expander(f"📄 {filename} ❌"):
                    st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")

        # Tips for parameter adjustment (same as single analysis)
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

        # Download comprehensive results
        st.subheader("📥 Export Results")
        if st.button("📊 Download Comprehensive Pause Results CSV"):
            create_pause_export_csv(successful_results)

    else:
        st.error("No successful analyses to display. Please check your files and parameters.")

def create_pause_export_csv(results):
    """Create downloadable CSV with comprehensive pause analysis results"""

    export_data = []

    for result in results:
        filename = result['original_filename']
        summary = result['summary']

        # Calculate pause ratio
        total_words = summary['total_words']
        words_with_pauses = summary['words_with_pauses']
        pause_ratio = (words_with_pauses / total_words) * 100 if total_words > 0 else 0

        row = {
            "Filename": filename,
            "Total_Pauses": summary['total_pauses'],
            "Audio_Duration_Seconds": summary['audio_duration'],
            "Total_Words": total_words,
            "Words_With_Pauses": words_with_pauses,
            "Pause_Ratio_Percent": pause_ratio,
            "Silence_Threshold_dB": result['parameters_used']['silence_threshold_db'],
            "Min_Pause_Duration_Sec": result['parameters_used']['min_pause_duration_sec'],
            "Transcript": result.get('transcript', ''),
            "Analysis_Success": "Yes"
        }
        export_data.append(row)

    export_df = pd.DataFrame(export_data)
    csv = export_df.to_csv(index=False)

    st.download_button(
        label="📊 Download Comprehensive Pause Results CSV",
        data=csv,
        file_name=f"pause_batch_analysis_{len(results)}_files.csv",
        mime="text/csv",
        help="Download detailed pause analysis results with parameters and transcriptions"
    )

def analyze_batch_stretch(uploaded_files, stretch_threshold, transcription_model, method="openai"):
    """Process multiple files for stretch analysis"""

    # Display method info
    method_display = {
        "openai": "🔄 OpenAI Whisper",
        "forcealign": "🎯 ForceAlign (Free/Offline)",
        "deepgram_forcealign": "🚀 Deepgram + ForceAlign Hybrid",
        "whisper_forcealign": "🎯 Whisper + ForceAlign Hybrid"
    }
    st.info(f"**Analysis Method:** {method_display.get(method, method)}")

    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []
    detailed_results = []  # Store full analysis results

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Processing {uploaded_file.name}...")
        progress_bar.progress((i + 1) / len(uploaded_files))

        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name

            # Run analysis with selected method
            result = analyze_stretch(temp_path, stretch_threshold=stretch_threshold, model=transcription_model, method=method)

            # Clean up temp file
            os.unlink(temp_path)

            # Store result
            if result['success']:
                # Summary for table
                results.append({
                    "File": uploaded_file.name,
                    "Total Words": result['summary']['total_words'],
                    "Stretched Words": result['summary']['stretched_words'],
                    "Stretch %": f"{result['summary']['stretch_percentage']}%",
                    "Avg Stretch Score": f"{result['summary']['avg_stretch_score']} sec/syl",
                    "Status": "✅ Success"
                })
                # Full result for detailed view
                detailed_results.append({
                    "filename": uploaded_file.name,
                    "result": result,
                    "success": True
                })
            else:
                results.append({
                    "File": uploaded_file.name,
                    "Total Words": 0,
                    "Stretched Words": 0,
                    "Stretch %": "N/A",
                    "Avg Stretch Score": "N/A",
                    "Status": f"❌ Error: {result.get('error', 'Unknown error')}"
                })
                detailed_results.append({
                    "filename": uploaded_file.name,
                    "result": result,
                    "success": False
                })

        except Exception as e:
            results.append({
                "File": uploaded_file.name,
                "Total Words": 0,
                "Stretched Words": 0,
                "Stretch %": "N/A",
                "Avg Stretch Score": "N/A",
                "Status": f"❌ Error: {str(e)}"
            })
            detailed_results.append({
                "filename": uploaded_file.name,
                "result": {"error": str(e)},
                "success": False
            })

    status_text.text("✅ Batch stretch analysis completed!")
    progress_bar.progress(1.0)

    # Display results
    st.header("📊 Batch Stretch Analysis Results")

    # Summary table
    st.subheader("📋 Summary Table")
    batch_df = pd.DataFrame(results)
    st.dataframe(batch_df, use_container_width=True)

    # Download summary
    csv = batch_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Summary CSV",
        data=csv,
        file_name="stretch_batch_summary.csv",
        mime="text/csv"
    )

    # Detailed results for each file
    st.markdown("---")
    st.header("📊 Detailed Results by File")

    for file_data in detailed_results:
        filename = file_data['filename']
        result = file_data['result']
        success = file_data['success']

        with st.expander(f"📄 {filename}", expanded=False):
            if success and result['success']:
                display_individual_stretch_results(filename, result, stretch_threshold)
            else:
                st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

def display_individual_stretch_results(filename, result, stretch_threshold):
    """Display detailed stretch analysis results for a single file (like individual page)"""

    # Summary metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    summary = result['summary']

    with col1:
        st.metric("Total Words", summary['total_words'])
    with col2:
        st.metric("Stretched Words", summary['stretched_words'])
    with col3:
        st.metric("Normal Words", summary['normal_words'])
    with col4:
        st.metric("Stretch %", f"{summary['stretch_percentage']}%")

    # Additional metrics
    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Avg Stretch", f"{summary['avg_stretch_score']} s/syl")
    with col6:
        st.metric("Max Stretch", f"{summary['max_stretch_score']} s/syl")
    with col7:
        st.metric("Speech Duration", f"{summary['total_speech_duration']}s")

    # Visualization
    st.subheader("📈 Stretch Score Visualization")

    word_table = result['word_table']

    if len(word_table) > 0:
        # Create interactive plot
        fig = go.Figure()

        # Stretched = Green (#4ecdc4), Normal = Red (#ff6b6b)
        colors = ['#4ecdc4' if x == 'Stretched' else '#ff6b6b' for x in word_table['Classification']]

        fig.add_trace(go.Scatter(
            x=list(range(len(word_table))),
            y=word_table['Stretch Score'],
            mode='markers+lines',
            marker=dict(color=colors, size=8),
            text=word_table['Word'],
            hovertemplate='<b>%{text}</b><br>Stretch: %{y}<br>Word #: %{x}<extra></extra>',
            name='Words'
        ))

        # Threshold line
        fig.add_hline(
            y=stretch_threshold,
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold"
        )

        fig.update_layout(
            title=f"Stretch Scores - {filename}",
            xaxis_title="Word Order",
            yaxis_title="Stretch Score (sec/syllable)",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    # Word table
    st.subheader("📋 Word Analysis Table")

    # Check if timing correction was applied
    timing_method = result['parameters_used'].get('timing_method', 'transcription_based')
    show_corrected_times = True  # Default to True

    if timing_method == "energy_corrected":
        real_start = summary.get('real_start_time', 0)
        st.info(f"ℹ️ **Showing corrected times:** Real speech starts at {real_start:.3f}s (silence excluded)")

    # Filter options
    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        filter_option = st.selectbox(
            "Filter:",
            ["All Words", "Stretched Only", "Normal Only"],
            key=f"filter_{filename}"
        )

    filtered_table = word_table.copy()

    # Apply time correction if energy-corrected timing was used
    if show_corrected_times and timing_method == "energy_corrected":
        real_start = summary.get('real_start_time', 0)
        filtered_table = filtered_table.copy()
        filtered_table['Start'] = filtered_table['Start'] + real_start
        filtered_table['End'] = filtered_table['End'] + real_start

    # Apply filter
    if filter_option == "Stretched Only":
        filtered_table = filtered_table[filtered_table['Classification'] == 'Stretched']
    elif filter_option == "Normal Only":
        filtered_table = filtered_table[filtered_table['Classification'] == 'Normal']

    if len(filtered_table) > 0:
        # Style table
        # Stretched = Green background, Normal = Red background
        def highlight_stretch(row):
            if row['Classification'] == 'Stretched':
                return ['background-color: #e8f5e8'] * len(row)  # Light green
            else:
                return ['background-color: #ffebee'] * len(row)  # Light red

        styled_df = filtered_table.style.apply(highlight_stretch, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info(f"No words match filter: {filter_option}")

    # Most stretched words
    if len(word_table) > 0:
        stretched_words = word_table[word_table['Classification'] == 'Stretched']
        if len(stretched_words) > 0:
            st.subheader("🔍 Most Stretched Words")
            top_stretched = stretched_words.nlargest(5, 'Stretch Score')[['Word', 'Stretch Score', 'Duration', 'Syllables']]
            st.dataframe(top_stretched, use_container_width=True)

    # Transcript
    st.subheader("📄 Transcript")
    if result.get('transcript'):
        st.text_area("Full transcript:", result['transcript'], height=100, key=f"transcript_{filename}")

if __name__ == "__main__":
    batch_analyze_page()