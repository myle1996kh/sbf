import concurrent.futures
from src.analyzers.volume_analyzer import analyze_volume
from src.analyzers.velocity_analyzer import analyze_velocity

def analyze_audio_file(file_path):
    """
    Analyze audio file for both volume and velocity simultaneously
    Returns combined results from both analyses
    """
    print(f"🔄 Starting analysis for: {file_path}")

    # Run volume and velocity analysis in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit both analyses
        volume_future = executor.submit(analyze_volume, file_path)
        velocity_future = executor.submit(analyze_velocity, file_path)

        # Get results
        volume_result = volume_future.result()
        velocity_result = velocity_future.result()

    # Combine results
    combined_result = {
        "file_path": file_path,
        "volume_analysis": volume_result,
        "velocity_analysis": velocity_result,
        "analysis_status": {
            "volume_success": "error" not in volume_result,
            "velocity_success": "error" not in velocity_result,
            "overall_success": "error" not in volume_result and "error" not in velocity_result
        }
    }

    print(f"✅ Analysis completed for: {file_path}")
    return combined_result

def display_results(result):
    """
    Display analysis results in a formatted way
    """
    print("\n" + "="*60)
    print(f"📊 AUDIO ANALYSIS RESULTS")
    print(f"File: {result['file_path']}")
    print("="*60)

    # Volume Results
    print("\n🔊 VOLUME ANALYSIS:")
    volume = result['volume_analysis']
    if 'error' in volume:
        print(f"❌ Error: {volume['error']}")
    else:
        print(f"   Min Volume: {volume['volume_min']} dBFS")
        print(f"   Max Volume: {volume['volume_max']} dBFS")
        print(f"   Avg Volume: {volume['volume_avg']} dBFS")
        print(f"   Volume Range: {volume['volume_range']} dBFS")
        print(f"   Target Coverage: {volume['coverage_vs_target']}%")

    # Velocity Results
    print("\n🏃 VELOCITY ANALYSIS:")
    velocity = result['velocity_analysis']
    if 'error' in velocity:
        print(f"❌ Error: {velocity['error']}")
    else:
        print(f"   Transcript: {velocity['transcript']}")
        print(f"   Total Words: {velocity['word_count_total']}")
        print(f"   Clean Words: {velocity['word_count_clean']}")
        print(f"   Duration: {velocity['duration_spoken']}s")
        print(f"   WPS: {velocity['wps']} words/second")
        print(f"   WPM: {velocity['wpm']} words/minute")
        print(f"   Level: {velocity['velocity_level']}")
        print(f"   Filled Pauses: {velocity['filled_pauses']}")

    # Analysis Status
    print(f"\n📈 ANALYSIS STATUS:")
    status = result['analysis_status']
    print(f"   Volume Analysis: {'✅ Success' if status['volume_success'] else '❌ Failed'}")
    print(f"   Velocity Analysis: {'✅ Success' if status['velocity_success'] else '❌ Failed'}")
    print(f"   Overall: {'✅ Success' if status['overall_success'] else '❌ Partial/Failed'}")
    print("="*60)