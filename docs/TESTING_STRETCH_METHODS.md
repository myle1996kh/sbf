# Testing Stretch Analysis Methods

## 🎯 Goal
Compare all 3 transcription methods for stretch analysis to see which works best for your needs.

---

## 📋 Prerequisites

### For All Methods:
```bash
pip install nltk librosa numpy pandas
```

### Method 1: OpenAI Whisper
```bash
# Set in .env file:
OPENAI_API_KEY=sk-your-key-here
```

### Method 2: ForceAlign
```bash
pip install forcealign
```

### Method 3: Deepgram + ForceAlign Hybrid
```bash
pip install forcealign deepgram-sdk

# Set in .env file:
DEEPGRAM_API_KEY=your-key-here
```

---

## 🧪 How to Test

### Option 1: Run Automated Comparison Test

```bash
# Test with default sample audio
python tests/test_stretch_methods_comparison.py

# Test with your own audio file
python tests/test_stretch_methods_comparison.py path/to/your/audio.wav
```

This will:
- ✅ Run all 3 methods on the same audio
- ✅ Show side-by-side comparison
- ✅ Display which methods succeeded/failed
- ✅ Provide recommendations

### Option 2: Test via UI (Streamlit)

1. Start the app:
```bash
streamlit run app.py
```

2. Navigate to: **Stretch Analysis** page

3. In sidebar, select analysis method:
   - OpenAI Whisper
   - ForceAlign
   - Deepgram + ForceAlign (Hybrid)

4. Upload audio and click **Analyze Speech Stretch**

5. Compare results by switching methods and re-analyzing

---

## 📊 What to Look For

### Success Indicators:
- ✅ Analysis completes without errors
- ✅ Transcript matches audio content
- ✅ Word count is reasonable
- ✅ Stretch scores make sense (0.2-0.5 s/syllable)

### Quality Comparison:

**Transcription Accuracy:**
- Check if transcript matches what was actually said
- Look for missing words or hallucinations
- Verify proper word boundaries

**Timing Precision:**
- Check if stretch scores correlate with actual pronunciation
- Look at "energy_corrected" vs "transcription_based" timing
- Verify speech duration is reasonable

**Method Reliability:**
- Does it handle your audio quality?
- Does it work with your accent/language?
- Is it consistent across multiple files?

---

## 🔬 Sample Test Output

```
================================================================================
🎯 TESTING STRETCH ANALYSIS METHODS
📁 Audio file: sample_audio/Stretch 3.wav
================================================================================

================================================================================
🔄 Testing: OpenAI Whisper
================================================================================

✅ SUCCESS!

📊 Results Summary:
   Total Words: 42
   Stretched Words: 12 (28.6%)
   Normal Words: 30
   Avg Stretch Score: 0.31 sec/syllable
   Speech Duration: 15.2 seconds
   Timing Method: energy_corrected

📝 Transcript Preview:
   hello everyone welcome to this demonstration of speech stretch analysis...

🔍 Top 3 Most Stretched Words:
   - 'demonstration': 0.52 sec/syl (2.6s / 5 syllables)
   - 'analysis': 0.48 sec/syl (1.9s / 4 syllables)
   - 'welcome': 0.41 sec/syl (0.82s / 2 syllables)

================================================================================
📊 COMPARISON SUMMARY
================================================================================

Method                              Total Words Stretched %  Avg Stretch Duration  Status
OpenAI Whisper                      42          28.6%        0.31        15.2s     ✅ Success
ForceAlign                          41          26.8%        0.29        15.1s     ✅ Success
Deepgram + ForceAlign Hybrid        42          30.9%        0.33        15.3s     ✅ Success

================================================================================
💡 RECOMMENDATIONS
================================================================================

✅ Multiple methods worked! Here's how to choose:

🔄 OpenAI Whisper:
   - Best for: High accuracy, multiple languages, production use
   - Requires: OpenAI API key, internet connection
   - Cost: ~$0.006 per minute

🎯 ForceAlign:
   - Best for: Free/offline processing, English-only, clear audio
   - Requires: pip install forcealign
   - Cost: Free

🚀 Deepgram + ForceAlign Hybrid:
   - Best for: Maximum accuracy + precision, English audio
   - Requires: Deepgram API key, ForceAlign installation
   - Cost: ~$0.004 per minute (Deepgram only)
```

---

## 🐛 Troubleshooting

### OpenAI Whisper Issues:

**Error: "OpenAI API Key not found"**
```bash
# Add to .env file
OPENAI_API_KEY=sk-your-actual-key
```

**Error: "No word timestamps"**
- Make sure you're using `whisper-1` model
- `gpt-4o-transcribe` doesn't support word timestamps

### ForceAlign Issues:

**Error: "ForceAlign not available"**
```bash
pip install forcealign
# May require PyTorch
pip install torch
```

**Error: "Import error"**
- ForceAlign needs clear audio
- Try resampling audio to 16kHz WAV

### Deepgram Issues:

**Error: "Deepgram API Key not found"**
```bash
# Add to .env file
DEEPGRAM_API_KEY=your-deepgram-key
```

**Error: "Deepgram SDK not installed"**
```bash
pip install deepgram-sdk
```

---

## 💡 Tips for Best Results

### Audio Quality:
- ✅ Use WAV or high-quality MP3
- ✅ Clear speech (minimal background noise)
- ✅ Sample rate: 16kHz or higher
- ✅ Mono or stereo both work

### Method Selection:
- **Production app:** OpenAI Whisper (most reliable)
- **Budget conscious:** ForceAlign (free!)
- **Maximum accuracy:** Deepgram + ForceAlign
- **Offline needed:** ForceAlign only

### Threshold Tuning:
- Start with **0.38 sec/syllable** (default)
- Lower (0.30) = more sensitive, catches slower words
- Higher (0.45) = less sensitive, only very stretched words

---

## 📈 Expected Results

### Normal Speech:
- Avg stretch: 0.20-0.30 sec/syllable
- Stretched words: 10-20%

### Slow/Careful Speech:
- Avg stretch: 0.30-0.40 sec/syllable
- Stretched words: 20-40%

### Emphasized Speech:
- Avg stretch: 0.35-0.50 sec/syllable
- Stretched words: 30-50%

---

## ✅ Next Steps

After testing, update your UI method selection based on:
1. Which methods worked for your audio
2. Your budget (free vs paid)
3. Your accuracy requirements
4. Online vs offline needs

The Streamlit UI already supports all 3 methods - just select in the dropdown!

---

*For more details, see [STRETCH_ANALYSIS_RESEARCH.md](STRETCH_ANALYSIS_RESEARCH.md)*
