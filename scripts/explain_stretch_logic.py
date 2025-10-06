#!/usr/bin/env python3
"""
Detailed explanation of stretch analysis logic with Whisper-1
"""

import os
from stretch_analyzer import count_syllables, analyze_stretch

def explain_stretch_calculation():
    """Step-by-step explanation of how stretch is calculated"""

    print("🎯 STRETCH ANALYSIS LOGIC WITH WHISPER-1")
    print("=" * 60)

    # Example from our actual data
    example_words = [
        {"word": "I", "start": 0.0, "end": 2.42},
        {"word": "don't", "start": 2.42, "end": 4.18},
        {"word": "know", "start": 4.18, "end": 5.68},
        {"word": "whether", "start": 5.68, "end": 7.48},
        {"word": "or", "start": 7.48, "end": 8.96},
    ]

    print("\n📊 STEP-BY-STEP CALCULATION:")
    print("-" * 50)

    for i, word_data in enumerate(example_words, 1):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        # Step 1: Calculate word duration
        duration = end - start

        # Step 2: Count syllables
        syllables = count_syllables(word)

        # Step 3: Calculate stretch score
        stretch_score = duration / syllables

        # Step 4: Classify
        threshold = 0.38
        classification = "Stretched" if stretch_score >= threshold else "Normal"

        print(f"\n{i}. Word: '{word}'")
        print(f"   📏 Duration: {end:.2f}s - {start:.2f}s = {duration:.2f}s")
        print(f"   🔤 Syllables: {syllables}")
        print(f"   ⏱️  Stretch Score: {duration:.2f}s ÷ {syllables} = {stretch_score:.3f} sec/syllable")
        print(f"   🎯 Classification: {classification} (threshold: {threshold})")

    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • Whisper-1 provides precise start/end times for each word")
    print(f"   • Duration = end_time - start_time")
    print(f"   • Syllable counting uses CMU pronunciation dictionary")
    print(f"   • Stretch = time_per_syllable (how long each syllable takes)")
    print(f"   • Higher stretch = slower, more deliberate pronunciation")

def explain_whisper_timestamp_accuracy():
    """Explain how accurate Whisper-1 timestamps are"""

    print(f"\n🔍 WHISPER-1 TIMESTAMP ACCURACY")
    print("=" * 50)

    print(f"\n📊 How Whisper-1 Determines Word Boundaries:")
    print(f"   1. 🎵 Audio Analysis: Analyzes mel-spectrogram features")
    print(f"   2. 🧠 Attention Mechanism: Uses transformer attention to align audio-text")
    print(f"   3. ⏰ Forced Alignment: Maps each word to audio segments")
    print(f"   4. 📍 Timestamp Generation: Provides start/end times")

    print(f"\n✅ Strengths:")
    print(f"   • Very accurate for clear speech")
    print(f"   • Handles multiple languages")
    print(f"   • Good with natural pauses and rhythm")
    print(f"   • Robust to background noise")

    print(f"\n⚠️ Limitations:")
    print(f"   • May not catch very short pauses between words")
    print(f"   • Could assign silence to word duration")
    print(f"   • Timestamp resolution ~10-20ms (not perfect)")
    print(f"   • May struggle with very fast or very slow speech")

def compare_stretch_methods():
    """Compare different approaches to measuring stretch"""

    print(f"\n⚖️ STRETCH MEASUREMENT APPROACHES")
    print("=" * 50)

    print(f"\n1️⃣ TRANSCRIPTION-BASED (Our Current Method)")
    print(f"   📝 Source: OpenAI Whisper-1 word timestamps")
    print(f"   ⏱️  Measurement: word_duration / syllable_count")
    print(f"   ✅ Pros: Available, easy to use, good accuracy")
    print(f"   ❌ Cons: Limited by transcription timestamp accuracy")

    print(f"\n2️⃣ ACOUSTIC-BASED (Alternative)")
    print(f"   📝 Source: Direct audio signal analysis")
    print(f"   ⏱️  Measurement: Vowel duration, formant analysis")
    print(f"   ✅ Pros: More precise, captures actual speech timing")
    print(f"   ❌ Cons: Complex, computationally expensive")

    print(f"\n3️⃣ HYBRID APPROACH (Best of Both)")
    print(f"   📝 Source: Transcription + Energy Detection")
    print(f"   ⏱️  Measurement: Corrected word boundaries + syllable timing")
    print(f"   ✅ Pros: Better accuracy, speech boundary correction")
    print(f"   ❌ Cons: More complex processing")

def analyze_stretch_factors():
    """Explain what causes high stretch scores"""

    print(f"\n🎭 WHAT CAUSES HIGH STRETCH SCORES?")
    print("=" * 50)

    factors = [
        ("🎯 Emphasis", "Speaker emphasizes important words", "Normal: 'yes' → Stretched: 'yeeees'"),
        ("🤔 Hesitation", "Speaker is uncertain or thinking", "Normal: 'maybe' → Stretched: 'maaybe'"),
        ("😬 Difficulty", "Hard to pronounce words", "Normal: 'specific' → Stretched: 'speeecific'"),
        ("🎭 Dramatic Effect", "Intentional elongation for effect", "Normal: 'wow' → Stretched: 'woooow'"),
        ("🗣️ Clear Articulation", "Careful pronunciation for clarity", "Normal: 'understand' → Stretched: 'un-der-stand'"),
        ("⚠️ Speech Issues", "Medical or developmental conditions", "Varies by individual")
    ]

    for emoji, cause, example in factors:
        print(f"\n{emoji} {cause}:")
        print(f"   Example: {example}")

    print(f"\n📊 STRETCH SCORE INTERPRETATION:")
    print(f"   • 0.10-0.25 sec/syl: Very fast speech")
    print(f"   • 0.25-0.35 sec/syl: Normal conversational speed")
    print(f"   • 0.35-0.50 sec/syl: Slow/careful speech")
    print(f"   • 0.50+ sec/syl: Very stretched/emphasized")

def test_with_real_audio():
    """Test stretch analysis with actual audio file"""

    audio_file = "Stretch 3.mp3"

    if not os.path.exists(audio_file):
        print(f"\n❌ {audio_file} not found for testing")
        return

    print(f"\n🧪 TESTING WITH REAL AUDIO: {audio_file}")
    print("=" * 50)

    try:
        result = analyze_stretch(audio_file, stretch_threshold=0.38, method="openai")

        if result['success']:
            print(f"\n📊 REAL ANALYSIS RESULTS:")
            summary = result['summary']
            word_table = result['word_table']

            print(f"   Total Words: {summary['total_words']}")
            print(f"   Stretched Words: {summary['stretched_words']} ({summary['stretch_percentage']}%)")
            print(f"   Average Stretch: {summary['avg_stretch_score']} sec/syllable")
            print(f"   Max Stretch: {summary['max_stretch_score']} sec/syllable")

            print(f"\n🔍 DETAILED WORD BREAKDOWN:")
            print(f"   {'Word':<12} {'Duration':<10} {'Syllables':<10} {'Stretch':<12} {'Type':<10}")
            print(f"   {'-'*60}")

            for _, row in word_table.iterrows():
                print(f"   {row['Word']:<12} {row['Duration']:<10} {row['Syllables']:<10} {row['Stretch Score']:<12} {row['Classification']:<10}")

            # Explain the results
            print(f"\n💡 ANALYSIS EXPLANATION:")
            if summary['stretch_percentage'] > 50:
                print(f"   🎯 High stretch ratio suggests deliberate slow speech")
            elif summary['stretch_percentage'] > 20:
                print(f"   📝 Moderate stretch indicates some emphasis or careful articulation")
            else:
                print(f"   ⚡ Low stretch ratio shows relatively fluent speech")

            # Show most stretched word
            most_stretched = word_table.loc[word_table['Stretch Score'].idxmax()]
            print(f"\n🏆 MOST STRETCHED WORD:")
            print(f"   '{most_stretched['Word']}': {most_stretched['Stretch Score']:.3f} sec/syllable")
            print(f"   Duration: {most_stretched['Duration']}s for {most_stretched['Syllables']} syllable(s)")

        else:
            print(f"❌ Analysis failed: {result['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explain_stretch_calculation()
    explain_whisper_timestamp_accuracy()
    compare_stretch_methods()
    analyze_stretch_factors()
    test_with_real_audio()