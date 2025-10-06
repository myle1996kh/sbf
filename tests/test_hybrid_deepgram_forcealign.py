#!/usr/bin/env python3
"""
Test script for Deepgram + ForceAlign hybrid stretch analysis
"""

import os
import sys
from stretch_analyzer import analyze_stretch

def test_hybrid_approach():
    """Test Deepgram + ForceAlign hybrid method on Stretch 3.mp3"""

    audio_file = "Stretch 3.mp3"

    # Check if file exists
    if not os.path.exists(audio_file):
        print(f"❌ Error: {audio_file} not found!")
        return

    # Check if Deepgram API key is set
    deepgram_key = os.getenv("DEEPGRAM_API_KEY")
    if not deepgram_key:
        print("❌ DEEPGRAM_API_KEY not found in environment variables")
        print("💡 Please set it in your .env file: DEEPGRAM_API_KEY=your_key_here")
        return

    print(f"🎯 Testing Deepgram + ForceAlign hybrid approach on: {audio_file}")
    print("=" * 70)

    try:
        # Test hybrid method
        print("🔄 Running Deepgram + ForceAlign hybrid analysis...")
        result = analyze_stretch(
            file_path=audio_file,
            stretch_threshold=0.38,
            method="deepgram_forcealign"
        )

        if result['success']:
            print("✅ Hybrid analysis successful!")
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
            print(f"\n📄 Transcript (from Deepgram):")
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

            print(f"\n🎯 Hybrid Method Benefits:")
            print("✅ Superior transcription quality from Deepgram")
            print("✅ Precise word-level timing from ForceAlign")
            print("✅ Best accuracy for stretch analysis")

        else:
            print(f"❌ Hybrid analysis failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

def compare_with_forcealign_only():
    """Compare hybrid approach with ForceAlign-only approach"""

    audio_file = "Stretch 3.mp3"

    print(f"\n🔄 Comparing methods...")
    print("=" * 70)

    try:
        # Test ForceAlign only
        print("1️⃣ Testing ForceAlign only...")
        forcealign_result = analyze_stretch(
            file_path=audio_file,
            stretch_threshold=0.38,
            method="forcealign"
        )

        # Test hybrid
        print("2️⃣ Testing Deepgram + ForceAlign hybrid...")
        hybrid_result = analyze_stretch(
            file_path=audio_file,
            stretch_threshold=0.38,
            method="deepgram_forcealign"
        )

        print("\n📊 Comparison Results:")
        print("-" * 50)

        if forcealign_result['success'] and hybrid_result['success']:
            print(f"{'Method':<25} {'Transcript':<40}")
            print("-" * 65)
            print(f"{'ForceAlign only':<25} {forcealign_result['transcript']:<40}")
            print(f"{'Deepgram + ForceAlign':<25} {hybrid_result['transcript']:<40}")

            print(f"\n{'Method':<25} {'Total Words':<15} {'Stretched':<15} {'Stretch %':<15}")
            print("-" * 70)
            fa_summary = forcealign_result['summary']
            hy_summary = hybrid_result['summary']
            print(f"{'ForceAlign only':<25} {fa_summary['total_words']:<15} {fa_summary['stretched_words']:<15} {fa_summary['stretch_percentage']}%")
            print(f"{'Deepgram + ForceAlign':<25} {hy_summary['total_words']:<15} {hy_summary['stretched_words']:<15} {hy_summary['stretch_percentage']}%")

        else:
            if not forcealign_result['success']:
                print(f"❌ ForceAlign only failed: {forcealign_result['error']}")
            if not hybrid_result['success']:
                print(f"❌ Hybrid method failed: {hybrid_result['error']}")

    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")

if __name__ == "__main__":
    # Check if Deepgram SDK is available
    try:
        from deepgram_transcriber import check_deepgram_availability
        if not check_deepgram_availability():
            print("❌ Deepgram SDK not available. Please install: pip install deepgram-sdk")
            sys.exit(1)
    except ImportError:
        print("❌ Deepgram transcriber module not found.")
        sys.exit(1)

    test_hybrid_approach()

    # Optional: Compare methods
    compare_input = input("\n🤔 Would you like to compare with ForceAlign-only method? (y/n): ")
    if compare_input.lower() in ['y', 'yes']:
        compare_with_forcealign_only()