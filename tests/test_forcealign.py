#!/usr/bin/env python3
"""
Test script for ForceAlign stretch analysis with Stretch 3.mp3
"""

import os
import sys
from stretch_analyzer import analyze_stretch

def test_forcealign_stretch():
    """Test ForceAlign stretch analysis on Stretch 3.mp3"""

    audio_file = "Stretch 3.mp3"

    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ Error: {audio_file} not found!")
        return

    print(f"🎯 Testing ForceAlign stretch analysis on: {audio_file}")
    print("=" * 60)

    try:
        # Test ForceAlign method
        print("🔄 Running ForceAlign analysis...")
        result = analyze_stretch(
            file_path=audio_file,
            stretch_threshold=0.38,
            method="forcealign"
        )

        if result['success']:
            print("✅ ForceAlign analysis successful!")
            print("\n📊 Analysis Results:")
            print("-" * 40)

            # Summary metrics
            summary = result['summary']
            print(f"Total Words: {summary['total_words']}")
            print(f"Stretched Words: {summary['stretched_words']}")
            print(f"Normal Words: {summary['normal_words']}")
            print(f"Stretch Percentage: {summary['stretch_percentage']}%")
            print(f"Average Stretch Score: {summary['avg_stretch_score']} sec/syllable")
            print(f"Max Stretch Score: {summary['max_stretch_score']} sec/syllable")
            print(f"Speech Duration: {summary['total_speech_duration']} seconds")

            # Parameters used
            params = result['parameters_used']
            print(f"\n🎛️ Parameters Used:")
            print(f"Method: {params['analysis_method']}")
            print(f"Threshold: {params['stretch_threshold']} sec/syllable")
            print(f"Model: {params['transcription_model']}")

            # Show transcript
            print(f"\n📄 Transcript:")
            print(f"'{result['transcript']}'")

            # Show first few words with details
            word_table = result['word_table']
            if len(word_table) > 0:
                print(f"\n📋 First 10 Words Details:")
                print("-" * 80)
                print(f"{'Word':<15} {'Start':<8} {'End':<8} {'Duration':<10} {'Syllables':<10} {'Stretch':<12} {'Type':<10}")
                print("-" * 80)

                for i in range(min(10, len(word_table))):
                    row = word_table.iloc[i]
                    print(f"{row['Word']:<15} {row['Start']:<8} {row['End']:<8} {row['Duration']:<10} {row['Syllables']:<10} {row['Stretch Score']:<12} {row['Classification']:<10}")

        else:
            print(f"❌ ForceAlign analysis failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_forcealign_stretch()