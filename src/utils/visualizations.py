"""
Visualization Module - Charts for Volume and Velocity Analysis
Adapted from SBF project chart.py module
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Constants for visualization
VOLUME_TARGET_RANGE = (-30, -10)  # Standard volume range in dBFS
VELOCITY_TARGET_RANGE = (2.0, 3.5)  # Standard WPS range

def plot_volume_histogram_individual(result, filename):
    """
    Plot individual file histogram with compact design for multiple files display.

    Args:
        result (dict): Contains 'frame_values' list of volume measurements in dBFS
        filename (str): Name of the file for title
    """
    if 'frame_values' not in result or not result["frame_values"]:
        st.warning(f"No volume data available for {filename}")
        return

    values = result["frame_values"]

    # Remove outliers using IQR method
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter valid values
    valid_values = [v for v in values if lower_bound <= v <= upper_bound]

    if not valid_values:
        st.warning(f"No valid volume data for {filename}")
        return

    # Calculate statistics
    user_min = min(valid_values)
    user_max = max(valid_values)
    user_avg = np.mean(valid_values)

    # Create compact histogram
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(valid_values, bins=20, color="#cccccc", edgecolor="black", alpha=0.8)

    # Add standard range
    ax.axvspan(-30, -10, facecolor='lightgreen', alpha=0.3, label="Standard Range")

    # Add average line
    ax.axvline(user_avg, color='blue', linestyle='-', linewidth=2, label=f"Avg: {user_avg:.1f}")

    # Labels and styling
    ax.set_title(f"📊 Volume Distribution - {filename[:20]}{'...' if len(filename) > 20 else ''}")
    ax.set_xlabel("Volume (dBFS)")
    ax.set_ylabel("Frequency")
    ax.legend(fontsize=8)
    ax.grid(True, linestyle="--", alpha=0.3)

    # Display in Streamlit
    st.pyplot(fig)
    plt.close(fig)  # Free memory


def plot_velocity_gauge(velocity_result, filename):
    """
    Create gauge chart showing speaking speed relative to target range.

    Args:
        velocity_result (dict): Contains WPS and velocity metrics
        filename (str): Name of the file for title
    """
    if 'wps' not in velocity_result:
        st.warning(f"No velocity data available for {filename}")
        return

    wps = velocity_result['wps']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=wps,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"📁 {filename[:25]}{'...' if len(filename) > 25 else ''}"},
        gauge={
            'axis': {'range': [0, 5], 'tickwidth': 1},
            'bar': {'color': 'gray'},
            'steps': [
                {'range': [0, 2.0], 'color': 'white'},     # Slow zone - white
                {'range': [2.0, 3.5], 'color': '#d6f5d6'}, # Standard zone - light green
                {'range': [3.5, 5], 'color': 'white'}      # Fast zone - white
            ],
            'threshold': {
                'line': {'color': "red", 'width': 3},
                'thickness': 0.75,
                'value': wps
            }
        }
    ))

    fig.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)


def plot_velocity_dot_strip(velocity_results, filenames):
    """
    Create a dot strip plot showing speaking speed distribution across files.

    Args:
        velocity_results (list): List of velocity analysis results
        filenames (list): List of corresponding filenames
    """
    wps_values = []
    labels = []

    for result, filename in zip(velocity_results, filenames):
        if 'wps' in result and 'error' not in result:
            wps_values.append(result['wps'])
            labels.append(filename)

    if not wps_values:
        st.warning("No velocity data available for dot strip plot")
        return

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.set_facecolor('white')

    # Add standard range background
    ax.axvspan(2.0, 3.5, facecolor='#d6f5d6', alpha=0.6, label="🟩 Standard Range (2.0 - 3.5 WPS)")

    # Plot WPS dots
    ax.scatter(wps_values, [1]*len(wps_values), s=200, color='gray', zorder=3)

    # Add WPS labels
    for i, (wps, label) in enumerate(zip(wps_values, labels)):
        ax.text(wps, 1.02, f"{wps:.2f}", ha='center', fontsize=9)
        # Add filename below (abbreviated)
        short_name = label[:10] + '...' if len(label) > 10 else label
        ax.text(wps, 0.98, short_name, ha='center', fontsize=7, rotation=45)

    ax.set_xlim(0, 5)
    ax.set_ylim(0.9, 1.1)
    ax.set_yticks([])
    ax.set_xlabel("Speaking Speed (WPS)")
    ax.set_title("📍 Speed Comparison Across Files")
    ax.legend(loc='upper left')
    ax.grid(True, linestyle="--", alpha=0.3)

    st.pyplot(fig)
    plt.close(fig)  # Free memory


def plot_velocity_metrics_table(velocity_result):
    """
    Create a detailed table showing velocity analysis metrics.

    Args:
        velocity_result (dict): Contains all velocity analysis data
    """
    if 'error' in velocity_result:
        st.error(f"Velocity analysis error: {velocity_result['error']}")
        return

    # Create metrics data
    metrics_data = {
        "Metric": [
            "Total Words Detected",
            "Clean Words (Valid)",
            "Filled Pauses Count",
            "Speaking Duration",
            "Real Start Time",
            "Real End Time",
            "Words Per Second (WPS)",
            "Words Per Minute (WPM)",
            "Velocity Classification"
        ],
        "Value": [
            velocity_result.get('word_count_total', 0),
            velocity_result.get('word_count_clean', 0),
            len(velocity_result.get('filled_pauses', [])),
            f"{velocity_result.get('duration_spoken', 0)}s",
            f"{velocity_result.get('real_start_time', 0)}s",
            f"{velocity_result.get('real_end_time', 0)}s",
            f"{velocity_result.get('wps', 0)} words/sec",
            f"{velocity_result.get('wpm', 0)} words/min",
            velocity_result.get('velocity_level', 'Unknown')
        ]
    }

    # Create and display DataFrame
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # Add status indicator
    wps = velocity_result.get('wps', 0)
    level = velocity_result.get('velocity_level', 'Unknown')

    if level == "Normal":
        st.success("✅ Normal speech velocity (2.0-3.5 WPS)")
    elif level == "Slow":
        st.info("ℹ️ Slow speech velocity (<2.0 WPS)")
    elif level == "Fast":
        st.warning("⚠️ Fast speech velocity (>3.5 WPS)")
    else:
        st.info(f"ℹ️ Speech velocity: {level}")


def create_volume_summary_chart(volume_results, filenames):
    """
    Create a summary chart showing volume metrics across multiple files.

    Args:
        volume_results (list): List of volume analysis results
        filenames (list): List of corresponding filenames
    """
    if not volume_results:
        st.warning("No volume data available for summary chart")
        return

    # Extract metrics
    file_data = []
    for result, filename in zip(volume_results, filenames):
        if 'error' not in result:
            file_data.append({
                'filename': filename[:15] + '...' if len(filename) > 15 else filename,
                'min': result.get('volume_min', 0),
                'avg': result.get('volume_avg', 0),
                'max': result.get('volume_max', 0),
                'coverage': result.get('coverage_vs_target', 0)
            })

    if not file_data:
        st.warning("No valid volume data for summary chart")
        return

    # Create subplot with 2 charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Chart 1: Min/Avg/Max comparison
    x_pos = range(len(file_data))
    filenames_short = [d['filename'] for d in file_data]

    ax1.scatter(x_pos, [d['min'] for d in file_data], color='red', label='Min dBFS', alpha=0.7)
    ax1.scatter(x_pos, [d['avg'] for d in file_data], color='blue', label='Avg dBFS', alpha=0.7)
    ax1.scatter(x_pos, [d['max'] for d in file_data], color='orange', label='Max dBFS', alpha=0.7)

    # Add standard range
    ax1.axhspan(-30, -10, facecolor='lightgreen', alpha=0.3, label="Standard Range")

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(filenames_short, rotation=45, ha='right')
    ax1.set_ylabel("Volume (dBFS)")
    ax1.set_title("📊 Volume Levels by File")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.3)

    # Chart 2: Coverage percentage
    coverage_values = [d['coverage'] for d in file_data]
    bars = ax2.bar(x_pos, coverage_values, color='lightblue', alpha=0.7)

    # Color bars based on coverage quality
    for i, (bar, coverage) in enumerate(zip(bars, coverage_values)):
        if coverage >= 70:
            bar.set_color('lightgreen')
        elif coverage >= 40:
            bar.set_color('lightyellow')
        else:
            bar.set_color('lightcoral')

    # Add coverage target line
    ax2.axhline(y=70, color='green', linestyle='--', label='Good Coverage (70%)')
    ax2.axhline(y=40, color='orange', linestyle='--', label='Fair Coverage (40%)')

    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(filenames_short, rotation=45, ha='right')
    ax2.set_ylabel("Target Coverage (%)")
    ax2.set_title("📈 Target Range Coverage")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.set_ylim(0, 100)

    # Add coverage values on bars
    for i, coverage in enumerate(coverage_values):
        ax2.text(i, coverage + 2, f'{coverage:.1f}%', ha='center', fontsize=8)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)  # Free memory


def create_combined_metrics_overview(volume_results, velocity_results, filenames):
    """
    Create a combined overview showing both volume and velocity metrics.

    Args:
        volume_results (list): List of volume analysis results
        velocity_results (list): List of velocity analysis results
        filenames (list): List of corresponding filenames
    """
    if not volume_results or not velocity_results:
        st.warning("Insufficient data for combined metrics overview")
        return

    # Create combined data
    combined_data = []
    for i, filename in enumerate(filenames):
        if i < len(volume_results) and i < len(velocity_results):
            vol_result = volume_results[i]
            vel_result = velocity_results[i]

            if 'error' not in vol_result and 'error' not in vel_result:
                combined_data.append({
                    'File': filename[:20] + '...' if len(filename) > 20 else filename,
                    'Volume Avg (dBFS)': vol_result.get('volume_avg', 0),
                    'Volume Coverage (%)': vol_result.get('coverage_vs_target', 0),
                    'Volume Score': vol_result.get('score', 0) if 'score' in vol_result else 0,
                    'WPS': vel_result.get('wps', 0),
                    'Velocity Level': vel_result.get('velocity_level', 'Unknown'),
                    'Clean Words': vel_result.get('word_count_clean', 0)
                })

    if not combined_data:
        st.warning("No valid data for combined overview")
        return

    # Create DataFrame
    df = pd.DataFrame(combined_data)

    # Display as enhanced table with color coding
    st.subheader("📊 Combined Metrics Overview")

    # Create columns for metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Average Volume Coverage", f"{df['Volume Coverage (%)'].mean():.1f}%")
    with col2:
        st.metric("Average WPS", f"{df['WPS'].mean():.2f}")
    with col3:
        st.metric("Average Clean Words", f"{df['Clean Words'].mean():.0f}")

    # Display detailed table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "File": st.column_config.TextColumn("File", width="medium"),
            "Volume Avg (dBFS)": st.column_config.NumberColumn("Vol Avg", format="%.1f"),
            "Volume Coverage (%)": st.column_config.NumberColumn("Coverage %", format="%.1f"),
            "Volume Score": st.column_config.NumberColumn("Vol Score", format="%.1f"),
            "WPS": st.column_config.NumberColumn("WPS", format="%.2f"),
            "Velocity Level": st.column_config.TextColumn("Vel Level", width="small"),
            "Clean Words": st.column_config.NumberColumn("Words", format="%d")
        }
    )