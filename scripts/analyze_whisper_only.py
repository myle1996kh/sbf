"""
Analyze Whisper transcription accuracy against ground truth.
"""

import os
import sys
from pathlib import Path
from difflib import SequenceMatcher
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps

# Ground truth data from the screenshot
GROUND_TRUTH = {
    "S 2 demanding finance.mp3": "MY BOSS IS VERY DEMANDING ESPECIALLY WHEN ITS COME TO FINANCE",
    "S 2 you have.mp3": "IF YOU WANTED TO CREATE A MARKETABLE PRODUCT YOU HAVE TO BE MASTER AT CUSTOMER INSIGHT",
    "S 2 you know.mp3": "WHO KNOWS MAYBE WE HAVE TO WITHDRAW THE PRODUCT THIS TIME YOU KNOW WHAT IT MEANS",
    "S - mix - 8.mp3": "SORRY TO CALL YOU AT THIS HOUR I JUST WANNA ASK YOU SOMETHING ABOUT WORD OF MOUTH",
    "S-3-mix.mp3": "HERE WE GO AGAIN IM BEEN TALKING ABOUT THE RAIN RECOGNITION",
    "S-m-3.mp3": "IN ORDER TO REGAIN THE MARKET SHARE WE HAVE TO ELIMINATE THIS COMPETITOR",
    "S-f-7.mp3": "IN ORDER TO REGAIN THE MARKET SHARE WE HAVE TO ELIMINATE THIS COMPETITOR"
}


def normalize_text(text):
    """Normalize text for comparison"""
    # Remove punctuation and convert to uppercase
    import string
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.upper().strip()


def calculate_similarity(str1, str2):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, normalize_text(str1), normalize_text(str2)).ratio()


def word_accuracy(predicted, ground_truth):
    """Calculate word-level accuracy"""
    pred_words = normalize_text(predicted).split()
    truth_words = normalize_text(ground_truth).split()

    if len(truth_words) == 0:
        return 0.0, 0, len(truth_words)

    # Count matching words (in order)
    matches = 0
    pred_copy = pred_words.copy()

    for truth_word in truth_words:
        if truth_word in pred_copy:
            matches += 1
            pred_copy.remove(truth_word)  # Remove to handle duplicates

    accuracy = (matches / len(truth_words)) * 100
    return accuracy, matches, len(truth_words)


def identify_errors(predicted, ground_truth):
    """Identify what words were wrong"""
    pred_words = normalize_text(predicted).split()
    truth_words = normalize_text(ground_truth).split()

    pred_copy = pred_words.copy()
    missing = []
    extra = []

    # Find missing words
    for word in truth_words:
        if word in pred_copy:
            pred_copy.remove(word)
        else:
            missing.append(word)

    # Remaining words in pred_copy are extra
    extra = pred_copy

    # Find substitutions (words that are in similar positions)
    substitutions = []
    max_len = max(len(pred_words), len(truth_words))
    for i in range(max_len):
        if i < len(pred_words) and i < len(truth_words):
            if pred_words[i] != truth_words[i]:
                substitutions.append(f"{truth_words[i]} → {pred_words[i]}")

    return {
        "missing": missing,
        "extra": extra,
        "substitutions": substitutions[:5]  # Limit to first 5
    }


def main():
    """Run Whisper accuracy analysis"""

    input_dir = Path("input")
    results = {}

    print("\n" + "="*80)
    print("WHISPER TRANSCRIPTION ACCURACY TEST")
    print("="*80)
    print("\nComparing Whisper transcriptions against ground truth")
    print(f"Total files to test: {len(GROUND_TRUTH)}\n")

    total_accuracy = []
    total_similarity = []

    # Test each file
    for filename, ground_truth in GROUND_TRUTH.items():
        audio_path = input_dir / filename

        if not audio_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        print(f"\n{'#'*80}")
        print(f"FILE: {filename}")
        print(f"{'#'*80}")
        print(f"Ground Truth: {ground_truth}")

        try:
            # Get Whisper transcription
            words_data = transcribe_with_openai_timestamps(str(audio_path))

            if not words_data:
                print("❌ Failed to get transcription")
                results[filename] = {"success": False, "error": "No transcription returned"}
                continue

            transcript = " ".join([w["word"] for w in words_data])
            print(f"Whisper Says: {transcript}")

            # Calculate metrics
            similarity = calculate_similarity(transcript, ground_truth)
            accuracy, matches, total = word_accuracy(transcript, ground_truth)
            errors = identify_errors(transcript, ground_truth)

            print(f"\n📊 METRICS:")
            print(f"   Similarity Score: {similarity*100:.1f}%")
            print(f"   Word Accuracy: {accuracy:.1f}% ({matches}/{total} words correct)")

            if errors["missing"]:
                print(f"   ❌ Missing Words: {', '.join(errors['missing'])}")

            if errors["extra"]:
                print(f"   ➕ Extra Words: {', '.join(errors['extra'])}")

            if errors["substitutions"]:
                print(f"   🔄 Substitutions:")
                for sub in errors["substitutions"]:
                    print(f"      {sub}")

            results[filename] = {
                "success": True,
                "ground_truth": ground_truth,
                "transcription": transcript,
                "similarity": similarity * 100,
                "word_accuracy": accuracy,
                "matches": matches,
                "total_words": total,
                "errors": errors
            }

            total_accuracy.append(accuracy)
            total_similarity.append(similarity * 100)

        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[filename] = {"success": False, "error": str(e)}

    # Generate summary report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)

    if total_accuracy:
        avg_accuracy = sum(total_accuracy) / len(total_accuracy)
        avg_similarity = sum(total_similarity) / len(total_similarity)

        print(f"\n📊 Average Metrics:")
        print(f"   Word Accuracy: {avg_accuracy:.1f}%")
        print(f"   Similarity Score: {avg_similarity:.1f}%")
        print(f"   Files Tested: {len(total_accuracy)}/{len(GROUND_TRUTH)}")

        # Identify common error patterns
        print(f"\n🔍 ERROR PATTERN ANALYSIS:")
        all_missing = []
        all_substitutions = []

        for filename, result in results.items():
            if result.get("success") and result.get("errors"):
                all_missing.extend(result["errors"].get("missing", []))
                all_substitutions.extend(result["errors"].get("substitutions", []))

        if all_missing:
            from collections import Counter
            missing_counts = Counter(all_missing)
            print(f"\n   Most Commonly Missing Words:")
            for word, count in missing_counts.most_common(5):
                print(f"      '{word}': {count} times")

        if all_substitutions:
            print(f"\n   Common Word Substitutions:")
            sub_counts = Counter(all_substitutions)
            for sub, count in sub_counts.most_common(5):
                print(f"      {sub}")

        # Files with issues
        print(f"\n❌ FILES WITH ERRORS:")
        for filename, result in results.items():
            if result.get("success") and result.get("word_accuracy", 100) < 100:
                acc = result["word_accuracy"]
                print(f"   {filename}: {acc:.1f}% accurate")

    # Save detailed results to JSON
    output_path = Path("test_results") / "whisper_accuracy.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Detailed results saved to: {output_path}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
