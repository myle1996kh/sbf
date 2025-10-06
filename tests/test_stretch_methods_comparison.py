"""
Test script to compare all 3 stretch analysis methods:
1. OpenAI Whisper
2. ForceAlign
3. Deepgram + ForceAlign Hybrid

Run this to see which method works best for your audio.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzers.stretch_analyzer import analyze_stretch
import pandas as pd

def test_all_methods(audio_file: str):
    """Test all 3 stretch analysis methods on the same audio file."""

    print("=" * 80)
    print(f"🎯 TESTING STRETCH ANALYSIS METHODS")
    print(f"📁 Audio file: {audio_file}")
    print("=" * 80)

    methods = [
        ("openai", "OpenAI Whisper"),
        ("forcealign", "ForceAlign"),
        ("deepgram_forcealign", "Deepgram + ForceAlign Hybrid")
    ]

    results = {}

    for method_key, method_name in methods:
        print(f"\n{'='*80}")
        print(f"🔄 Testing: {method_name}")
        print(f"{'='*80}")

        try:
            # Run analysis
            result = analyze_stretch(
                file_path=audio_file,
                stretch_threshold=0.38,  # Use default threshold
                method=method_key
            )

            if result['success']:
                results[method_name] = result

                # Print summary
                summary = result['summary']
                print(f"\n✅ SUCCESS!")
                print(f"\n📊 Results Summary:")
                print(f"   Total Words: {summary['total_words']}")
                print(f"   Stretched Words: {summary['stretched_words']} ({summary['stretch_percentage']}%)")
                print(f"   Normal Words: {summary['normal_words']}")
                print(f"   Avg Stretch Score: {summary['avg_stretch_score']} sec/syllable")
                print(f"   Speech Duration: {summary['total_speech_duration']} seconds")

                # Print timing method used
                params = result['parameters_used']
                timing = params.get('timing_method', 'unknown')
                print(f"   Timing Method: {timing}")

                # Print transcript snippet
                transcript = result['transcript']
                transcript_preview = transcript[:100] + "..." if len(transcript) > 100 else transcript
                print(f"\n📝 Transcript Preview:")
                print(f"   {transcript_preview}")

                # Show most stretched words
                df = result['word_table']
                stretched = df[df['Classification'] == 'Stretched']
                if len(stretched) > 0:
                    print(f"\n🔍 Top 3 Most Stretched Words:")
                    top_3 = stretched.nlargest(3, 'Stretch Score')
                    for idx, row in top_3.iterrows():
                        print(f"   - '{row['Word']}': {row['Stretch Score']} sec/syl ({row['Duration']}s / {row['Syllables']} syllables)")

            else:
                print(f"\n❌ FAILED: {result['error']}")
                results[method_name] = {"error": result['error']}

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            results[method_name] = {"error": str(e)}

    # Comparison table
    print(f"\n\n{'='*80}")
    print("📊 COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    comparison_data = []
    for method_name in [m[1] for m in methods]:
        if method_name in results and 'summary' in results[method_name]:
            r = results[method_name]['summary']
            comparison_data.append({
                "Method": method_name,
                "Total Words": r['total_words'],
                "Stretched %": f"{r['stretch_percentage']}%",
                "Avg Stretch": f"{r['avg_stretch_score']}",
                "Duration": f"{r['total_speech_duration']}s",
                "Status": "✅ Success"
            })
        else:
            error_msg = results.get(method_name, {}).get('error', 'Unknown error')
            comparison_data.append({
                "Method": method_name,
                "Total Words": "N/A",
                "Stretched %": "N/A",
                "Avg Stretch": "N/A",
                "Duration": "N/A",
                "Status": f"❌ {error_msg[:30]}"
            })

    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))

    # Recommendations
    print(f"\n\n{'='*80}")
    print("💡 RECOMMENDATIONS")
    print(f"{'='*80}\n")

    successful_methods = [m for m in results.keys() if 'summary' in results[m]]

    if len(successful_methods) == 0:
        print("❌ No methods succeeded. Check your API keys and installations.")
    elif len(successful_methods) == 1:
        print(f"✅ Only {successful_methods[0]} worked.")
        print(f"   Use this method for your analysis.")
    else:
        print("✅ Multiple methods worked! Here's how to choose:")
        print("\n🔄 OpenAI Whisper:")
        print("   - Best for: High accuracy, multiple languages, production use")
        print("   - Requires: OpenAI API key, internet connection")
        print("   - Cost: ~$0.006 per minute\n")

        print("🎯 ForceAlign:")
        print("   - Best for: Free/offline processing, English-only, clear audio")
        print("   - Requires: pip install forcealign")
        print("   - Cost: Free\n")

        print("🚀 Deepgram + ForceAlign Hybrid:")
        print("   - Best for: Maximum accuracy + precision, English audio")
        print("   - Requires: Deepgram API key, ForceAlign installation")
        print("   - Cost: ~$0.004 per minute (Deepgram only)\n")

    print(f"{'='*80}\n")

    return results


if __name__ == "__main__":
    # Test with sample audio
    sample_audio = "sample_audio/Stretch 3.wav"

    if not os.path.exists(sample_audio):
        print(f"❌ Sample audio not found: {sample_audio}")
        print("\n💡 Please provide an audio file path:")
        print("   python tests/test_stretch_methods_comparison.py <path_to_audio>")

        # Check for command line argument
        if len(sys.argv) > 1:
            sample_audio = sys.argv[1]
        else:
            print("\nSearching for any audio files in sample_audio/...")
            sample_dir = Path("sample_audio")
            if sample_dir.exists():
                audio_files = list(sample_dir.glob("*.wav")) + list(sample_dir.glob("*.mp3"))
                if audio_files:
                    sample_audio = str(audio_files[0])
                    print(f"✅ Found: {sample_audio}")
                else:
                    print("❌ No audio files found in sample_audio/")
                    sys.exit(1)
            else:
                sys.exit(1)

    # Run comparison
    results = test_all_methods(sample_audio)

    print("\n✅ Test complete! Check the results above to choose your preferred method.")
    print("\n💡 To test with a different file:")
    print("   python tests/test_stretch_methods_comparison.py <path_to_your_audio.wav>")
