# Speech Analytics Dashboard - Metrics Overview

## What We Measure

This application analyzes speech audio files across **4 key dimensions** to evaluate speech quality and delivery patterns.

---

## 📊 The 4 Core Metrics

### 1. 🔊 Volume Analysis
**What it measures:** Audio loudness levels across the entire recording

**Technical definition:** Sound pressure in dBFS (decibels relative to full scale)

**Why it matters:** Ensures consistent, audible speech without distortion
- Too quiet → Hard to hear
- Too loud → Audio distortion/clipping
- Inconsistent → Poor listening experience

**Target range:** -30 to -10 dBFS (optimal speech clarity)

**What you get:**
- Minimum/Maximum/Average volume
- Volume range (dynamic range)
- Coverage percentage in target range
- Frame-by-frame volume distribution

**Quality indicators:**
- ✅ Good: ≥70% coverage in target range
- ⚠️ Moderate: 40-70% coverage
- ❌ Poor: <40% coverage

---

### 2. 🏃 Velocity Analysis
**What it measures:** How fast the speaker talks

**Technical definition:** Speech rate in words per second (WPS) and words per minute (WPM)

**Why it matters:** Optimal pacing ensures comprehension
- Too slow → Listener disengagement
- Too fast → Information overload
- Just right → Clear, comfortable delivery

**Calculation method:**
```
Duration = Last word end time - First word start time
Velocity = Clean word count ÷ Duration
```

**What counts as "clean words":**
- Excludes filled pauses: "um", "uh", "ah", "like", "you know"
- Only counts meaningful words with clear timing

**Speed classification:**
- 🐌 Slow: <2.0 WPS (<120 WPM)
- ✅ Normal: 2.0-3.5 WPS (120-210 WPM)
- 🚀 Fast: >3.5 WPS (>210 WPM)

**What you get:**
- Full transcript
- Total words vs clean words count
- Actual speech duration (excluding silence)
- WPS and WPM metrics
- Filled pause detection
- Velocity classification

---

### 3. ⏸️ Pause Analysis
**What it measures:** Silent gaps **between** speech segments

**Technical definition:** Silence intervals detected during active speech (excludes beginning/end silence)

**Why it matters:** Natural pauses enhance comprehension
- Strategic pauses → Better message delivery
- Excessive pauses → Hesitation, uncertainty
- No pauses → Rushed, unclear speech

**Detection method:**
1. Find all silence regions in audio
2. Remove first and last silence (beginning/end of recording)
3. Match remaining pauses with word timestamps
4. Show which words each pause occurs before/after

**Configurable parameters:**
- **Silence threshold:** How quiet is considered "silent" (-40 dB default)
- **Minimum pause duration:** Shortest pause to detect (0.1s default)

**What you get:**
- Word-by-word pause table
- Pause before/after each word
- Total pause count
- Timeline visualization showing pauses on waveform
- Words affected by pauses

**Key insight:** Only counts pauses **during** speech, not at start/end of recording

---

### 4. 📏 Stretch Analysis
**What it measures:** How long each word is pronounced relative to its syllable count

**Technical definition:** Duration per syllable (seconds/syllable)

**Why it matters:** Identifies unnaturally slow/emphasized pronunciation
- Normal speech → ~0.2-0.3s per syllable
- Stretched words → >0.3s per syllable (may indicate emphasis, hesitation, or clarity issues)

**Calculation method:**
```
For each word:
  1. Count syllables using CMU pronunciation dictionary
  2. Measure word duration from timestamps
  3. Stretch Score = Duration ÷ Syllables
  4. Classify: Stretched if score ≥ threshold (default 0.3)
```

**Example:**
- Word: "hello" (2 syllables)
- Duration: 0.8 seconds
- Stretch score: 0.8 ÷ 2 = **0.4 seconds/syllable**
- Classification: **Stretched** (>0.3 threshold)

**Configurable parameters:**
- **Stretch threshold:** Duration per syllable to classify as "stretched" (0.3s default)
- **Transcription method:** OpenAI Whisper / ForceAlign / Deepgram+ForceAlign

**What you get:**
- Word-by-word analysis table
- Syllable count per word
- Duration and stretch score for each word
- Stretched vs Normal classification
- Overall stretch percentage
- Average/min/max stretch scores
- Full transcript with stretch highlighting

**Advanced features:**
- Energy-based timing correction for accuracy
- Real speech duration calculation
- Customizable threshold with live reclassification

---

## 🎯 Common Use Cases

### For Speech Coaches & Trainers
- **Volume:** Ensure students maintain consistent vocal projection
- **Velocity:** Train optimal pacing for presentations
- **Pause:** Teach strategic pause placement
- **Stretch:** Identify overemphasis or hesitation patterns

### For Content Creators & Podcasters
- **Volume:** Verify audio levels meet broadcast standards
- **Velocity:** Maintain engaging pace for audience retention
- **Pause:** Edit out excessive pauses
- **Stretch:** Identify filler words or nervous speech patterns

### For Language Learners
- **Volume:** Practice consistent voice projection
- **Velocity:** Match native speaker pacing
- **Pause:** Learn natural pause patterns
- **Stretch:** Avoid over-pronunciation of words

### For Voice-Over Artists
- **Volume:** Meet client audio specifications
- **Velocity:** Match script timing requirements
- **Pause:** Perfect pause timing for dramatic effect
- **Stretch:** Ensure natural, professional delivery

---

## 🔬 Technical Foundation

**Transcription engine:** OpenAI Whisper API (word-level timestamps)

**Audio processing libraries:**
- pydub (audio manipulation)
- librosa (audio analysis)
- numpy (numerical processing)

**Accuracy enhancements:**
- Energy-based speech boundary detection
- Filled pause filtering
- CMU pronunciation dictionary
- Beginning/end silence removal

**Batch processing:** Analyze multiple files simultaneously with parallel processing

---

## 📈 Output Formats

All metrics provide:
- ✅ Numerical scores and classifications
- ✅ Detailed data tables
- ✅ Visual charts and graphs
- ✅ Full transcripts
- ✅ Exportable results (CSV, etc.)
- ✅ Parameter customization

---

## 🎤 Quality Metrics Summary

| Metric | Measures | Good Range | Warning Signs |
|--------|----------|------------|---------------|
| **Volume** | Loudness (dBFS) | -30 to -10 dBFS | <40% in target range |
| **Velocity** | Speed (WPS) | 2.0-3.5 WPS | <2.0 or >3.5 WPS |
| **Pause** | Silence gaps | Strategic pauses | Excessive or no pauses |
| **Stretch** | Duration/syllable | <0.3 s/syllable | >30% stretched words |

---

*Generated for Speech Analytics Dashboard v2.0*
