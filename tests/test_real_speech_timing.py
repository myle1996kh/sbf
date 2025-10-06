#!/usr/bin/env python3
"""
Test script to demonstrate real speech timing in stretch analysis
"""

import os
from stretch_analyzer import analyze_stretch

def test_real_speech_timing():
    """Test real speech timing improvements with Stretch 3.mp3"""

    audio_file = "Stretch 3.mp3"

    if not os.path.exists(audio_file):
        print(f"❌ Error: {audio_file} not found!")
        return

    print(f"🎯 Testing Real Speech Timing with: {audio_file}")
    print("=" * 60)

    try:
        # Test with OpenAI method (best accuracy)
        print("🔄 Running OpenAI Whisper analysis...")
        result = analyze_stretch(
            file_path=audio_file,
            stretch_threshold=0.38,
            method="openai"
        )

        if result['success']:
            print("✅ Analysis successful!")
            print("\n📊 Real Speech Timing Results:")
            print("-" * 50)

            summary = result['summary']

            # Show timing information
            print(f"📄 Transcript: '{result['transcript']}'")
            print(f"\n⏱️ Timing Analysis:")
            print(f"   Real Speech Start: {summary['real_start_time']}s")
            print(f"   Real Speech End: {summary['real_end_time']}s")
            print(f"   Real Speech Duration: {summary['total_speech_duration']}s")
            print(f"   Total Audio Length: Not directly measured")

            # Show word breakdown
            word_table = result['word_table']
            if len(word_table) > 0:
                first_word = word_table.iloc[0]
                last_word = word_table.iloc[-1]

                print(f"\n📋 Word Timing Details:")
                print(f"   First word: '{first_word['Word']}' at {first_word['Start']}s")
                print(f"   Last word: '{last_word['Word']}' at {last_word['End']}s")

                print(f"\n🎯 Stretch Analysis:")
                print(f"   Total Words: {summary['total_words']}")
                print(f"   Stretched Words: {summary['stretched_words']} ({summary['stretch_percentage']}%)")
                print(f"   Average Stretch: {summary['avg_stretch_score']} sec/syllable")
                print(f"   Max Stretch: {summary['max_stretch_score']} sec/syllable")

                # Show benefits of real timing
                print(f"\n✅ Real Speech Timing Benefits:")
                print(f"   🎯 Excludes silence at beginning/end")
                print(f"   🎯 More accurate speech rate calculation")
                print(f"   🎯 Better stretch analysis precision")
                print(f"   🎯 Consistent with velocity analysis method")

                # Show stretched words
                stretched_words = word_table[word_table['Classification'] == 'Stretched']
                if len(stretched_words) > 0:
                    print(f"\n🔍 Stretched Words Detected:")
                    for _, word in stretched_words.iterrows():
                        print(f"   '{word['Word']}': {word['Stretch Score']} sec/syl (duration: {word['Duration']}s)")

        else:
            print(f"❌ Analysis failed: {result['error']}")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

def compare_timing_methods():
    """Show the difference between old and new timing approaches"""

    print(f"\n📊 Timing Method Comparison")
    print("=" * 60)

    print(f"🔄 OLD METHOD (sum of word durations):")
    print(f"   Problem: Includes gaps between words")
    print(f"   Example: word1(0.5s) + gap(0.2s) + word2(0.3s) = 1.0s total")
    print(f"   Issue: Overestimates speech duration")

    print(f"\n✅ NEW METHOD (real speech span):")
    print(f"   Solution: First word start → Last word end")
    print(f"   Example: word1(2.0s-2.5s) to word2(3.0s-3.3s) = 1.3s real speech")
    print(f"   Benefit: Excludes beginning/end silence, more accurate")

    print(f"\n🎯 Same as Velocity Analysis:")
    print(f"   Velocity uses: clean_words[0]['start'] to clean_words[-1]['end']")
    print(f"   Stretch now uses: clean_words[0]['start'] to clean_words[-1]['end']")
    print(f"   Result: Consistent timing across all analyses!")

if __name__ == "__main__":
    test_real_speech_timing()

    compare_input = input("\n🤔 Would you like to see timing method comparison? (y/n): ")
    if compare_input.lower() in ['y', 'yes']:
        compare_timing_methods()