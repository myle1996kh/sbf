"""
Compare Whisper + ForceAlign vs Deepgram + ForceAlign hybrid methods
against ground truth transcripts.
"""

import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcribers.deepgram_transcriber import whisper_forcealign_hybrid_timestamps, hybrid_deepgram_forcealign_timestamps

# Ground truth data from the screenshot
GROUND_TRUTH = {
    "S 2 demanding finance.mp3": {
        "transcript": "MY BOSS IS VERY DEMANDING ESPECIALLY WHEN ITS COME TO FINANCE",
        "stretched_words": ["demanding", "finance"]
    },
    "S 2 you have.mp3": {
        "transcript": "IF YOU WANTED TO CREATE A MARKETABLE PRODUCT YOU HAVE TO BE MASTER AT CUSTOMER INSIGHT",
        "stretched_words": ["you", "have"]
    },
    "S 2 you know.mp3": {
        "transcript": "WHO KNOWS MAYBE WE HAVE TO WITHDRAW THE PRODUCT THIS TIME YOU KNOW WHAT IT MEANS",
        "stretched_words": ["you", "know"]
    },
    "S - mix - 8.mp3": {
        "transcript": "SORRY TO CALL YOU AT THIS HOUR I JUST WANNA ASK YOU SOMETHING ABOUT WORD OF MOUTH",
        "stretched_words": ["at", "this", "hour", "you"]
    },
    "S-3-mix.mp3": {
        "transcript": "HERE WE GO AGAIN IM BEEN TALKING ABOUT THE RAIN RECOGNITION",
        "stretched_words": ["been", "talking", "recognition"]
    },
    "S-m-3.mp3": {
        "transcript": "IN ORDER TO REGAIN THE MARKET SHARE WE HAVE TO ELIMINATE THIS COMPETITOR",
        "stretched_words": ["we", "have", "to"]
    },
    "S-f-7.mp3": {
        "transcript": "IN ORDER TO REGAIN THE MARKET SHARE WE HAVE TO ELIMINATE THIS COMPETITOR",
        "stretched_words": ["in", "to", "the", "share"]
    }
}


def normalize_text(text):
    """Normalize text for comparison"""
    return text.upper().strip()


def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, normalize_text(str1), normalize_text(str2)).ratio()


def word_accuracy(predicted, ground_truth):
    """Calculate word-level accuracy"""
    pred_words = normalize_text(predicted).split()
    truth_words = normalize_text(ground_truth).split()

    if len(truth_words) == 0:
        return 0.0

    # Count matching words
    matches = 0
    for truth_word in truth_words:
        if truth_word in pred_words:
            matches += 1
            pred_words.remove(truth_word)  # Remove to handle duplicates

    return (matches / len(truth_words)) * 100


def identify_errors(predicted, ground_truth):
    """Identify what words were wrong"""
    pred_words = normalize_text(predicted).split()
    truth_words = normalize_text(ground_truth).split()

    errors = []
    missing = []
    extra = []

    # Find missing words
    for word in truth_words:
        if word not in pred_words:
            missing.append(word)

    # Find extra words
    for word in pred_words:
        if word not in truth_words:
            extra.append(word)

    return {
        "missing": missing,
        "extra": extra
    }


def test_method(audio_path, method_name, method_func):
    """Test a specific transcription method"""
    print(f"\n{'='*60}")
    print(f"Testing {method_name} on {os.path.basename(audio_path)}")
    print(f"{'='*60}")

    try:
        result = method_func(audio_path)

        if result["success"]:
            transcript = result["transcript"]
            print(f"✅ Success!")
            print(f"Transcript: {transcript}")
            return {
                "success": True,
                "transcript": transcript,
                "word_count": len(transcript.split())
            }
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error")
            }
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Run comparison test"""

    input_dir = Path("input")
    results = {}

    print("\n" + "="*80)
    print("HYBRID METHOD COMPARISON TEST")
    print("="*80)
    print("\nTesting files from input/ folder")
    print(f"Total files to test: {len(GROUND_TRUTH)}\n")

    # Test each file with both methods
    for filename, ground_truth in GROUND_TRUTH.items():
        audio_path = input_dir / filename

        if not audio_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        print(f"\n{'#'*80}")
        print(f"FILE: {filename}")
        print(f"{'#'*80}")
        print(f"Ground Truth: {ground_truth['transcript']}")

        results[filename] = {
            "ground_truth": ground_truth["transcript"],
            "whisper_forcealign": None,
            "deepgram_forcealign": None
        }

        # Test Whisper + ForceAlign
        whisper_result = test_method(
            str(audio_path),
            "Whisper + ForceAlign",
            whisper_forcealign_hybrid_timestamps
        )
        results[filename]["whisper_forcealign"] = whisper_result

        # Test Deepgram + ForceAlign
        deepgram_result = test_method(
            str(audio_path),
            "Deepgram + ForceAlign",
            hybrid_deepgram_forcealign_timestamps
        )
        results[filename]["deepgram_forcealign"] = deepgram_result

        # Compare results
        print(f"\n{'-'*60}")
        print("COMPARISON:")
        print(f"{'-'*60}")

        if whisper_result["success"]:
            whisper_sim = calculate_similarity(whisper_result["transcript"], ground_truth["transcript"])
            whisper_acc = word_accuracy(whisper_result["transcript"], ground_truth["transcript"])
            whisper_errors = identify_errors(whisper_result["transcript"], ground_truth["transcript"])

            print(f"\n🎯 Whisper + ForceAlign:")
            print(f"   Similarity: {whisper_sim*100:.1f}%")
            print(f"   Word Accuracy: {whisper_acc:.1f}%")
            if whisper_errors["missing"]:
                print(f"   Missing words: {', '.join(whisper_errors['missing'])}")
            if whisper_errors["extra"]:
                print(f"   Extra words: {', '.join(whisper_errors['extra'])}")

            results[filename]["whisper_forcealign"]["similarity"] = whisper_sim * 100
            results[filename]["whisper_forcealign"]["word_accuracy"] = whisper_acc
            results[filename]["whisper_forcealign"]["errors"] = whisper_errors

        if deepgram_result["success"]:
            deepgram_sim = calculate_similarity(deepgram_result["transcript"], ground_truth["transcript"])
            deepgram_acc = word_accuracy(deepgram_result["transcript"], ground_truth["transcript"])
            deepgram_errors = identify_errors(deepgram_result["transcript"], ground_truth["transcript"])

            print(f"\n🚀 Deepgram + ForceAlign:")
            print(f"   Similarity: {deepgram_sim*100:.1f}%")
            print(f"   Word Accuracy: {deepgram_acc:.1f}%")
            if deepgram_errors["missing"]:
                print(f"   Missing words: {', '.join(deepgram_errors['missing'])}")
            if deepgram_errors["extra"]:
                print(f"   Extra words: {', '.join(deepgram_errors['extra'])}")

            results[filename]["deepgram_forcealign"]["similarity"] = deepgram_sim * 100
            results[filename]["deepgram_forcealign"]["word_accuracy"] = deepgram_acc
            results[filename]["deepgram_forcealign"]["errors"] = deepgram_errors

    # Generate summary report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)

    whisper_scores = []
    deepgram_scores = []
    whisper_word_acc = []
    deepgram_word_acc = []

    for filename, result in results.items():
        if result["whisper_forcealign"] and result["whisper_forcealign"]["success"]:
            whisper_scores.append(result["whisper_forcealign"]["similarity"])
            whisper_word_acc.append(result["whisper_forcealign"]["word_accuracy"])

        if result["deepgram_forcealign"] and result["deepgram_forcealign"]["success"]:
            deepgram_scores.append(result["deepgram_forcealign"]["similarity"])
            deepgram_word_acc.append(result["deepgram_forcealign"]["word_accuracy"])

    print("\n📊 Average Similarity Scores:")
    if whisper_scores:
        print(f"   Whisper + ForceAlign: {sum(whisper_scores)/len(whisper_scores):.1f}%")
    if deepgram_scores:
        print(f"   Deepgram + ForceAlign: {sum(deepgram_scores)/len(deepgram_scores):.1f}%")

    print("\n📊 Average Word Accuracy:")
    if whisper_word_acc:
        print(f"   Whisper + ForceAlign: {sum(whisper_word_acc)/len(whisper_word_acc):.1f}%")
    if deepgram_word_acc:
        print(f"   Deepgram + ForceAlign: {sum(deepgram_word_acc)/len(deepgram_word_acc):.1f}%")

    # Save detailed results to JSON
    output_path = Path("test_results") / "method_comparison.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {output_path}")

    # Determine winner
    print("\n🏆 WINNER:")
    if whisper_scores and deepgram_scores:
        avg_whisper = sum(whisper_word_acc) / len(whisper_word_acc)
        avg_deepgram = sum(deepgram_word_acc) / len(deepgram_word_acc)

        if avg_whisper > avg_deepgram:
            diff = avg_whisper - avg_deepgram
            print(f"   Whisper + ForceAlign wins by {diff:.1f}% word accuracy!")
        elif avg_deepgram > avg_whisper:
            diff = avg_deepgram - avg_whisper
            print(f"   Deepgram + ForceAlign wins by {diff:.1f}% word accuracy!")
        else:
            print("   It's a tie!")

    print("\n" + "="*80)


if __name__ == "__main__":
    main()
