# SBF Audio Analyzer - Hướng dẫn toàn diện 4 Thông số

## 📋 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Volume (Âm lượng)](#1️⃣-volume-âm-lượng)
3. [Velocity (Tốc độ nói)](#2️⃣-velocity-tốc-độ-nói)
4. [Pause (Khoảng lặng)](#3️⃣-pause-khoảng-lặng)
5. [Stretch (Kéo dài âm)](#4️⃣-stretch-kéo-dài-âm)
6. [Tích hợp 4 thông số](#tích-hợp-4-thông-số)
7. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
8. [Use Cases](#use-cases--ví-dụ)

---

## Giới thiệu

### 🎯 Mục đích của SBF Audio Analyzer

**SBF Audio Analyzer** là công cụ phân tích chất lượng giọng nói chuyên sâu, được thiết kế để đánh giá 4 thông số quan trọng nhất trong kỹ năng giao tiếp và thuyết trình:

```
┌─────────────────────────────────────────────┐
│   SBF AUDIO ANALYZER - 4 CORE METRICS      │
├─────────────────────────────────────────────┤
│                                             │
│  1. VOLUME    → Energy & Confidence         │
│  2. VELOCITY  → Clarity & Pacing            │
│  3. PAUSE     → Rhythm & Structure          │
│  4. STRETCH   → Emphasis & Emotion          │
│                                             │
│  → Comprehensive Speech Quality Analysis    │
└─────────────────────────────────────────────┘
```

### 💡 Tại sao phân tích 4 thông số này?

Trong giao tiếp hiệu quả:

| Thông số | Ảnh hưởng đến | Ví dụ |
|----------|---------------|-------|
| **Volume** | Sự thu hút, thuyết phục | Nói quá nhỏ → thiếu tự tin |
| **Velocity** | Sự rõ ràng, professional | Nói quá nhanh → khó hiểu |
| **Pause** | Nhịp điệu, cấu trúc | Pause đúng chỗ → nhấn mạnh ý |
| **Stretch** | Cảm xúc, nhấn mạnh | Kéo dài từ khóa → thu hút |

### 🎓 Ứng dụng chính

- 🎤 **Đào tạo thuyết trình**: Presentation skills coaching
- 📞 **Call center QA**: Đánh giá chất lượng cuộc gọi
- 🎓 **Luyện thi speaking**: IELTS, TOEFL preparation
- 🎬 **Voice-over training**: Luyện lồng tiếng chuyên nghiệp
- 📊 **Nghiên cứu ngữ âm**: Speech research & analysis

---

## 1️⃣ VOLUME (Âm lượng)

### 📖 Định nghĩa

**Volume** là cường độ âm thanh (loudness) của giọng nói, được đo bằng **decibel (dB)**.

```
Volume = 20 × log₁₀(RMS_amplitude)
```

Trong SBF Analyzer, sử dụng **dBFS** (decibels relative to Full Scale):
- 0 dBFS = Âm lượng tối đa (có thể bị distortion)
- -60 dBFS = Rất nhỏ, gần như không nghe được
- -30 dBFS đến -10 dBFS = Khoảng lý tưởng cho speech

### 🔬 Phương pháp phân tích

**Bước 1: Chia audio thành segments**
```python
# Mỗi segment = ~2 giây
Segment 1: 0.0s - 2.0s
Segment 2: 2.0s - 4.0s
Segment 3: 4.0s - 6.0s
...
```

**Bước 2: Tính RMS energy cho mỗi segment**
```python
import numpy as np
import librosa

# Load audio
y, sr = librosa.load(audio_file, sr=16000)

# Tính RMS cho mỗi frame
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)

# Convert to dB
db = 20 * np.log10(rms + 1e-6)  # +1e-6 để tránh log(0)
```

**Bước 3: Phân loại mỗi segment**

| Classification | dB Range | Color | Ý nghĩa |
|----------------|----------|-------|---------|
| **Too Quiet** | < -30 dB | 🔴 Red | Quá nhỏ, khó nghe rõ |
| **Quiet** | -30 dB đến -25 dB | 🟠 Orange | Nhỏ nhưng vẫn nghe được |
| **Normal** | -25 dB đến -15 dB | 🟢 Green | Vừa phải, thoải mái |
| **Loud** | -15 dB đến -10 dB | 🟡 Yellow | To, có năng lượng |
| **Too Loud** | > -10 dB | 🔴 Red | Quá to, có thể distortion |

### 📊 Metrics được tính

```python
Volume Metrics:
├─ Min Volume: -35.2 dB
├─ Max Volume: -12.5 dB
├─ Avg Volume: -22.8 dB
├─ Volume Range: 22.7 dB (max - min)
└─ Coverage in target range: 85.3%
```

### 🎯 Scoring System

```python
def calculate_volume_score(avg_db, coverage_percent):
    score = 0

    # Base score từ average dB
    if -25 <= avg_db <= -15:
        score += 50  # Ideal range
    elif -30 <= avg_db < -25 or -15 < avg_db <= -10:
        score += 35  # Acceptable
    else:
        score += 10  # Needs improvement

    # Bonus từ coverage percentage
    if coverage_percent >= 70:
        score += 30  # High coverage
    elif coverage_percent >= 50:
        score += 20  # Moderate coverage
    else:
        score += 5   # Low coverage

    # Consistency bonus (low variance)
    if volume_variance < 5:
        score += 20  # Very consistent

    return min(score, 100)
```

### 🖼️ UI Screenshot - Volume Analysis

**[Placeholder: Chụp ảnh UI Volume Analysis]**

Nội dung cần có trong ảnh:
- 📈 Line chart: Volume (dB) theo thời gian
- 🎨 Color-coded segments (Red/Orange/Green/Yellow)
- 📊 Metrics summary box (Min/Max/Avg/Coverage)
- 🎯 Score rating (0-100)
- 💡 Recommendations

```
┌─────────────────────────────────────────────┐
│         VOLUME ANALYSIS RESULT              │
├─────────────────────────────────────────────┤
│                                             │
│  [LINE CHART: Volume over time]             │
│   dB                                        │
│   -10 ┤━━━━━ Too Loud (yellow line)         │
│   -15 ┤━━━━━ Ideal range                    │
│   -20 ┤ ╱╲╱╲  (green area)                  │
│   -25 ┤━━━━━                                │
│   -30 ┤━━━━━ Too Quiet (red line)           │
│        └────────────────────→ Time          │
│                                             │
│  📊 Metrics:                                │
│  ├─ Min: -35.2 dB                           │
│  ├─ Max: -12.5 dB                           │
│  ├─ Avg: -22.8 dB  ✅                       │
│  ├─ Range: 22.7 dB                          │
│  └─ Target Coverage: 85.3%                  │
│                                             │
│  🎯 Score: 85/100                           │
│  📝 Rating: Good                            │
│                                             │
│  💡 Recommendations:                        │
│  ✅ Volume level is good                    │
│  💡 Maintain consistency                    │
└─────────────────────────────────────────────┘
```

### 💡 Interpretation Guide

**Good volume:**
- ✅ Avg -25 dB to -15 dB
- ✅ Coverage ≥ 70%
- ✅ Low variance (consistent)

**Needs improvement:**
- ❌ Avg < -30 dB or > -10 dB
- ❌ Coverage < 50%
- ❌ High variance (inconsistent)

---

## 2️⃣ VELOCITY (Tốc độ nói)

### 📖 Định nghĩa

**Velocity** là tốc độ phát âm, được đo bằng **words per second (WPS)** hoặc **words per minute (WPM)**.

```
Velocity (WPS) = Clean Words / Real Speech Duration
Velocity (WPM) = WPS × 60
```

### 🔬 Phương pháp phân tích

**Bước 1: Transcribe audio với word timestamps**

```python
from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps

# Gọi Whisper API
words_data = transcribe_with_openai_timestamps(audio_path)

# Kết quả:
[
    {"word": "my", "start": 0.00, "end": 0.15},
    {"word": "boss", "start": 0.15, "end": 0.45},
    {"word": "is", "start": 0.45, "end": 0.58},
    {"word": "very", "start": 0.58, "end": 0.85},
    {"word": "demanding", "start": 1.18, "end": 1.78},
]
```

**Bước 2: Lọc filled pauses**

```python
FILLED_PAUSES = ["um", "uh", "ah", "eh", "like", "you know", "mm", "mhm"]

# Loại bỏ filled pauses
clean_words = [w for w in words_data if w["word"] not in FILLED_PAUSES]
```

**Bước 3: Tính Real Speech Duration**

```python
# KHÔNG tính toàn bộ file duration!
# CHỈ tính từ từ đầu tiên → từ cuối cùng

real_start = clean_words[0]["start"]  # First word start
real_end = clean_words[-1]["end"]     # Last word end
real_duration = real_end - real_start

# Ví dụ:
# File duration: 10.0s
# First word start: 1.2s
# Last word end: 8.5s
# Real duration: 8.5 - 1.2 = 7.3s  ← Chỉ tính phần có nói!
```

**Bước 4: Tính Velocity**

```python
total_words = len(words_data)        # Tất cả từ
clean_words_count = len(clean_words) # Không có um, uh
filled_count = total_words - clean_words_count

velocity_wps = clean_words_count / real_duration
velocity_wpm = velocity_wps * 60

# Ví dụ:
# Clean words: 22 từ
# Real duration: 7.3s
# Velocity: 22 / 7.3 = 3.01 WPS = 181 WPM
```

### 📊 Classification

| Category | WPS Range | WPM Range | Đặc điểm |
|----------|-----------|-----------|----------|
| **Too Slow** | < 2.0 | < 120 | Quá chậm, gây buồn ngủ |
| **Slow** | 2.0 - 2.5 | 120 - 150 | Chậm nhưng rõ ràng |
| **Normal** | 2.5 - 3.5 | 150 - 210 | Tốc độ chuẩn, dễ nghe |
| **Fast** | 3.5 - 4.0 | 210 - 240 | Nhanh, năng động |
| **Too Fast** | > 4.0 | > 240 | Quá nhanh, khó theo kịp |

### 🎯 Scoring System

```python
def calculate_velocity_score(wps):
    # Ideal range: 2.8 - 3.2 WPS
    if 2.8 <= wps <= 3.2:
        return 100  # Perfect

    # Good range: 2.5 - 3.5 WPS
    elif 2.5 <= wps <= 3.5:
        return 90

    # Acceptable: 2.0 - 4.0 WPS
    elif 2.0 <= wps <= 4.0:
        return 75

    # Outside acceptable range
    else:
        # Penalty increases with distance from ideal
        distance = min(abs(wps - 2.8), abs(wps - 3.2))
        penalty = distance * 20
        return max(50 - penalty, 0)
```

### 🖼️ UI Screenshot - Velocity Analysis

**[Placeholder: Chụp ảnh UI Velocity Analysis]**

```
┌─────────────────────────────────────────────┐
│        VELOCITY ANALYSIS RESULT             │
├─────────────────────────────────────────────┤
│                                             │
│  📝 Transcript:                             │
│  "My boss is very demanding especially      │
│   when it comes to finance"                 │
│                                             │
│  [WORD TIMELINE]                            │
│  my    boss   is   very  demanding...       │
│  ├──┤  ├───┤ ├┤  ├──┤  ├──────┤            │
│  0.0s  0.5s  1.0s  1.5s  2.0s               │
│                                             │
│  📊 Metrics:                                │
│  ├─ Total Words: 25                         │
│  ├─ Clean Words: 22 (removed 3 "um")        │
│  ├─ Real Speech Duration: 7.3s              │
│  ├─ Velocity: 3.01 WPS                      │
│  ├─ Velocity: 181 WPM                       │
│  └─ Classification: Normal ✅               │
│                                             │
│  🎯 Score: 92/100                           │
│  📝 Rating: Excellent                       │
│                                             │
│  💡 Recommendations:                        │
│  ✅ Perfect pacing for clarity              │
│  ✅ Good filler word control                │
└─────────────────────────────────────────────┘
```

### 💡 Interpretation Guide

**Tốc độ lý tưởng theo ngữ cảnh:**

| Ngữ cảnh | Ideal WPS | Lý do |
|----------|-----------|-------|
| Presentation | 2.5 - 3.0 | Rõ ràng, dễ theo dõi |
| Conversation | 2.8 - 3.5 | Tự nhiên, thoải mái |
| News/Formal | 2.6 - 3.0 | Professional, clear |
| Storytelling | 3.0 - 3.8 | Dynamic, engaging |

---

## 3️⃣ PAUSE (Khoảng lặng)

### 📖 Định nghĩa

**Pause** là khoảng dừng (silence gaps) giữa các từ trong lúc nói, không bao gồm khoảng lặng đầu/cuối file.

### 🔬 Phương pháp phân tích

**Bước 1: Detect pauses giữa words**

```python
# Tính gap giữa các từ liên tiếp
for i in range(len(words) - 1):
    pause_gap = words[i+1]["start"] - words[i]["end"]

    if pause_gap >= pause_threshold:  # Default 0.2s
        pauses.append({
            "after_word": words[i]["word"],
            "before_word": words[i+1]["word"],
            "duration": pause_gap,
            "position": words[i]["end"]
        })
```

**Bước 2: Verify với energy analysis (optional)**

```python
# Kiểm tra pause có thực sự là silence không
import librosa

y, sr = librosa.load(audio_path)
rms = librosa.feature.rms(y=y)

# Trong khoảng pause, energy phải thấp
for pause in pauses:
    start_sample = pause["position"] * sr
    end_sample = (pause["position"] + pause["duration"]) * sr
    pause_energy = rms[:, start_sample:end_sample].mean()

    if pause_energy < silence_threshold:
        pause["verified"] = True  # Đúng là silence
```

### 📊 Pause Classification

| Type | Duration | Purpose | Evaluation |
|------|----------|---------|------------|
| **Micro** | < 0.2s | Breathing, rhythm | Natural ✅ |
| **Short** | 0.2 - 0.5s | Separate phrases | Ideal ✅ |
| **Medium** | 0.5 - 1.0s | Emphasis, thinking | OK ⚠️ |
| **Long** | 1.0 - 2.0s | Major transitions | Careful ⚠️ |
| **Very Long** | > 2.0s | Hesitation, lost | Avoid ❌ |

### 📈 Pause Quality Metrics

```python
Pause Metrics:
├─ Total Pauses: 8
├─ Pause Density: 0.20 (20% of words have pause after)
├─ Average Duration: 0.42s
├─ Micro Pauses: 2
├─ Short Pauses: 4  ← Most common (good!)
├─ Medium Pauses: 1
├─ Long Pauses: 1
├─ Very Long Pauses: 0 ✅
└─ Filled Pause Count: 3 ("um", "uh")
```

### 🎯 Scoring System

```python
def calculate_pause_score(metrics):
    score = 0

    # 1. Pause Density (30 points)
    density = metrics["pause_count"] / metrics["total_words"]
    if 0.15 <= density <= 0.25:
        score += 30  # Ideal density
    elif 0.10 <= density <= 0.30:
        score += 20  # Acceptable
    else:
        score += 10  # Too many or too few

    # 2. Average Duration (30 points)
    avg_duration = metrics["avg_pause_duration"]
    if 0.3 <= avg_duration <= 0.6:
        score += 30  # Ideal length
    elif 0.2 <= avg_duration <= 0.8:
        score += 20  # Acceptable
    else:
        score += 10  # Too short or too long

    # 3. Filled Pause Ratio (30 points)
    filled_ratio = metrics["filled_count"] / max(metrics["pause_count"], 1)
    if filled_ratio < 0.10:
        score += 30  # Very few fillers
    elif filled_ratio < 0.20:
        score += 20  # Some fillers
    else:
        score += 5   # Too many fillers

    # 4. Long Pause Penalty (10 points)
    if metrics["very_long_count"] == 0:
        score += 10  # No very long pauses

    return score
```

### 🖼️ UI Screenshot - Pause Analysis

**[Placeholder: Chụp ảnh UI Pause Analysis]**

```
┌─────────────────────────────────────────────┐
│         PAUSE ANALYSIS RESULT               │
├─────────────────────────────────────────────┤
│                                             │
│  [PAUSE TIMELINE]                           │
│  Word:    my  boss  is   very demanding     │
│  Pause:      ├0.3s┤  ├0.5s┤  ├0.2s┤        │
│  Timeline: ──┬────┬────┬────┬────┬──→       │
│             0s    1s   2s   3s   4s          │
│                                             │
│  📊 Pause Distribution:                     │
│  Micro (<0.2s):     ██ 2                    │
│  Short (0.2-0.5s):  ████ 4  ← Most          │
│  Medium (0.5-1.0s): █ 1                     │
│  Long (1.0-2.0s):   █ 1                     │
│  Very Long (>2.0s): 0  ✅                   │
│                                             │
│  📊 Quality Metrics:                        │
│  ├─ Total Pauses: 8                         │
│  ├─ Pause Density: 0.20 (20%)  ✅           │
│  ├─ Avg Duration: 0.42s  ✅                 │
│  ├─ Filled Pauses: 3 ("um" x2, "uh" x1)     │
│  └─ Filled Ratio: 37.5%  ⚠️                 │
│                                             │
│  🎯 Score: 75/100                           │
│  📝 Rating: Good                            │
│                                             │
│  💡 Recommendations:                        │
│  ✅ Good pause rhythm                       │
│  ⚠️ Reduce filler words ("um", "uh")        │
│  💡 Practice strategic pausing              │
└─────────────────────────────────────────────┘
```

### 💡 Interpretation Guide

**Good pause patterns:**
- ✅ Density 15-25% (natural rhythm)
- ✅ Mostly short pauses (0.2-0.5s)
- ✅ Few or no filled pauses (<10%)
- ✅ No very long pauses

**Problematic patterns:**
- ❌ Too many pauses (>40%) → Hesitant
- ❌ Too few pauses (<10%) → Rushed
- ❌ Many filled pauses (>20%) → Nervous
- ❌ Many long pauses → Lost track

---

## 4️⃣ STRETCH (Kéo dài âm)

### 📖 Định nghĩa

**Stretch** là việc phát âm một từ dài hơn bình thường so với số âm tiết, được đo bằng **seconds per syllable**.

```
Stretch Score = Word Duration / Syllable Count
```

### 🔬 Phương pháp phân tích

**Method 1: OpenAI Whisper Only**

```python
# Step 1: Get word timestamps from Whisper
words = transcribe_with_openai_timestamps(audio_path)

# Step 2: Count syllables using CMU Dictionary
from nltk.corpus import cmudict
cmu_dict = cmudict.dict()

def count_syllables(word):
    if word in cmu_dict:
        # Count phonemes with stress markers (digits)
        pronunciations = cmu_dict[word]
        return max([len([y for y in x if y[-1].isdigit()])
                    for x in pronunciations])
    else:
        # Fallback: count vowel groups
        return estimate_syllables(word)

# Step 3: Calculate stretch
word = "demanding"
duration = 0.60  # From Whisper timestamps
syllables = 3    # de-man-ding
stretch_score = 0.60 / 3 = 0.200 s/syllable
```

**Method 2: Whisper + ForceAlign Hybrid** ⭐ **RECOMMENDED**

```python
# Step 1: Whisper cho high-accuracy transcript
from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps
whisper_words = transcribe_with_openai_timestamps(audio_path)
transcript = " ".join([w["word"] for w in whisper_words])

# Step 2: ForceAlign cho precise timing (±10ms)
from src.transcribers.forcealign_transcriber import transcribe_with_forcealign_timestamps
word_timestamps = transcribe_with_forcealign_timestamps(audio_path, transcript)

# Step 3: Calculate stretch với timing chính xác
word = "demanding"
duration = 0.60  # From ForceAlign (precise!)
syllables = 3
stretch_score = 0.60 / 3 = 0.200 s/syllable
```

**Tại sao Hybrid tốt hơn?**
- Whisper: High transcript accuracy
- ForceAlign: ±10ms timing precision
- → Best stretch calculation!

Xem chi tiết: [FORCEALIGN_MECHANISM_EXPLAINED.md](FORCEALIGN_MECHANISM_EXPLAINED.md)

### 📊 Classification

```python
# Threshold configurable (default: 0.3 s/syllable)
if stretch_score >= threshold:
    classification = "STRETCHED"  # Kéo dài
else:
    classification = "NORMAL"     # Bình thường
```

**Recommended thresholds:**

| Context | Threshold | Rationale |
|---------|-----------|-----------|
| Conversational | 0.25 - 0.30 | Natural speech |
| Presentation | 0.30 - 0.35 | Clear delivery |
| Dramatic/Theatrical | 0.35 - 0.40 | Emphasis |

### 📈 Stretch Metrics

```python
Stretch Metrics:
├─ Total Words: 25
├─ Stretched Words: 5 (20%)
├─ Normal Words: 20 (80%)
├─ Avg Stretch Score: 0.185 s/syllable
├─ Max Stretch: 0.420 s/syllable ("demanding")
├─ Min Stretch: 0.085 s/syllable ("is")
├─ Overall Stretch: 0.192 s/syllable
└─ Total Syllables: 38
```

**Overall Stretch:**
```
Overall = Total Speech Duration / Total Syllables
        = 7.3s / 38 syllables
        = 0.192 s/syllable
```

### 🎯 Scoring System

```python
def calculate_stretch_score(metrics, threshold):
    score = 0

    # 1. Stretch Percentage (40 points)
    stretch_pct = (metrics["stretched_count"] / metrics["total_words"]) * 100

    if stretch_pct <= 20:
        score += 40  # Natural: 10-20% stretched
    elif stretch_pct <= 30:
        score += 30  # Acceptable
    elif stretch_pct <= 40:
        score += 20  # Presentation style
    else:
        score += 5   # Over-stretched

    # 2. Average Stretch Score (40 points)
    avg_stretch = metrics["avg_stretch_score"]

    if avg_stretch <= 0.25:
        score += 40  # Natural pacing
    elif avg_stretch <= 0.30:
        score += 30  # Good
    else:
        score += 15  # Too slow

    # 3. Variance (20 points)
    # Low variance = consistent delivery
    if stretch_variance < 0.05:
        score += 20
    elif stretch_variance < 0.10:
        score += 10

    return score
```

### 🖼️ UI Screenshot - Stretch Analysis

**[Placeholder: Chụp ảnh UI Stretch Analysis]**

```
┌─────────────────────────────────────────────┐
│        STRETCH ANALYSIS RESULT              │
├─────────────────────────────────────────────┤
│                                             │
│  📝 Transcript with Stretch Highlighting:   │
│  "My boss is very DEMANDING especially      │
│   when it COMES to finance"                 │
│   (CAPITALIZED = Stretched words)           │
│                                             │
│  [WORD TABLE]                               │
│  Word      │ Syl │ Dur  │ Score │ Class    │
│  ─────────────────────────────────────────  │
│  my        │  1  │ 0.15 │ 0.150 │ Normal   │
│  boss      │  1  │ 0.30 │ 0.300 │ Stretched│
│  is        │  1  │ 0.13 │ 0.130 │ Normal   │
│  very      │  2  │ 0.27 │ 0.135 │ Normal   │
│  demanding │  3  │ 0.60 │ 0.200 │ Normal   │
│  ...       │ ... │ ...  │ ...   │ ...      │
│                                             │
│  🎨 Stretch Distribution:                   │
│  Normal:     ████████████████ 20 (80%)      │
│  Stretched:  ████ 5 (20%)  ✅               │
│                                             │
│  📊 Metrics:                                │
│  ├─ Avg Stretch: 0.185 s/syl  ✅            │
│  ├─ Max Stretch: 0.420 s/syl (demanding)    │
│  ├─ Min Stretch: 0.085 s/syl (is)           │
│  ├─ Overall: 0.192 s/syl                    │
│  └─ Threshold: 0.300 s/syl (adjustable)     │
│                                             │
│  🎯 Score: 90/100                           │
│  📝 Rating: Excellent                       │
│                                             │
│  💡 Recommendations:                        │
│  ✅ Good natural pacing                     │
│  ✅ Strategic emphasis on key words         │
│  💡 20% stretch ratio is ideal              │
└─────────────────────────────────────────────┘
```

**Interactive Threshold Slider:**
```
Stretch Threshold: [────●────] 0.30 s/syllable
                   0.20       0.40

As you adjust:
- Classification updates in real-time
- Metrics recalculate instantly
- No need to re-analyze audio
```

### 💡 Interpretation Guide

**Stretch có chủ ý (Good):**
```python
"My boss is very DEMANDING"
                  ↑
Từ "demanding" stretched (0.35 s/syllable)
→ Nhấn mạnh sự khắt khe
→ Emotion & emphasis ✅
```

**Stretch không mong muốn (Bad):**
```python
"I uhhh... REALLY... NEED... MORE... TIME"
        ↑     ↑       ↑      ↑      ↑
Tất cả từ đều stretched (avg 0.45 s/syllable)
→ Hesitation, nervousness
→ Lack of confidence ❌
```

**Ideal patterns:**
- ✅ 10-20% stretched (natural)
- ✅ 20-30% stretched (presentation)
- ✅ Stretch on keywords only
- ✅ Avg < 0.25 s/syllable

**Problematic patterns:**
- ❌ >50% stretched (over-emphasis)
- ❌ Avg > 0.35 s/syllable (too slow)
- ❌ Random stretch (no pattern)
- ❌ All content words stretched (monotone emphasis)

---

## Tích hợp 4 thông số

### 🔗 Cách 4 metrics hoạt động cùng nhau

```
┌─────────────────────────────────────────────┐
│      COMPREHENSIVE SPEECH ANALYSIS          │
├─────────────────────────────────────────────┤
│                                             │
│  VOLUME (Energy)                            │
│    ↓                                        │
│  Đảm bảo người nghe được                    │
│  Thể hiện confidence                        │
│                                             │
│  VELOCITY (Pacing)                          │
│    ↓                                        │
│  Đảm bảo rõ ràng, dễ hiểu                   │
│  Control nhịp độ information                │
│                                             │
│  PAUSE (Rhythm)                             │
│    ↓                                        │
│  Tạo cấu trúc, nhịp điệu                    │
│  Cho thời gian người nghe absorb            │
│                                             │
│  STRETCH (Emphasis)                         │
│    ↓                                        │
│  Nhấn mạnh từ khóa                          │
│  Thể hiện cảm xúc, ý định                   │
│                                             │
│  = OVERALL QUALITY SCORE                    │
└─────────────────────────────────────────────┘
```

### 📊 Comprehensive Dashboard

**[Placeholder: Chụp ảnh Comprehensive Dashboard]**

```
┌─────────────────────────────────────────────┐
│   COMPREHENSIVE ANALYSIS DASHBOARD          │
├─────────────────────────────────────────────┤
│                                             │
│  📊 Overall Score: 88/100                   │
│  ⭐⭐⭐⭐☆ (4/5 stars)                        │
│                                             │
│  [4 MINI CHARTS IN GRID]                    │
│  ┌────────┬────────┐                        │
│  │ Volume │Velocity│                        │
│  │  85/100│ 92/100 │                        │
│  ├────────┼────────┤                        │
│  │ Pause  │Stretch │                        │
│  │  75/100│ 90/100 │                        │
│  └────────┴────────┘                        │
│                                             │
│  📈 Detailed Metrics:                       │
│  ┌─────────────────────────────┐            │
│  │ Volume:   -22 dB  │  85/100│            │
│  │ Velocity: 2.8 WPS │  92/100│            │
│  │ Pause:    0.42s   │  75/100│            │
│  │ Stretch:  0.185   │  90/100│            │
│  └─────────────────────────────┘            │
│                                             │
│  ✅ Strengths:                              │
│  • Excellent pacing (2.8 WPS)               │
│  • Good volume consistency                  │
│  • Strategic word emphasis                  │
│                                             │
│  ⚠️ Areas for Improvement:                  │
│  • Reduce filler words (37% filled pauses)  │
│  • Add more strategic pauses                │
│                                             │
│  💡 Overall Assessment:                     │
│  Good quality speech with clear delivery.   │
│  Focus on reducing "um, uh" for more        │
│  professional presentation.                 │
│                                             │
│  [Export] [View Details] [Compare]          │
└─────────────────────────────────────────────┘
```

### 🎯 Use Case Examples

**Example 1: Professional Presentation**
```
Audio: Product launch presentation

Volume:   -20 dB      → Good energy        (85/100)
Velocity: 3.0 WPS     → Clear pacing       (92/100)
Pause:    Good rhythm → Strategic pauses   (88/100)
Stretch:  20% ratio   → Emphasis on key    (90/100)

Overall: 88.75/100 → Excellent presenter!
```

**Example 2: Nervous Speaker**
```
Audio: Job interview response

Volume:   -28 dB      → Too quiet          (60/100)
Velocity: 4.2 WPS     → Too fast           (55/100)
Pause:    Many "um"   → 40% filled         (45/100)
Stretch:  Random      → No pattern         (50/100)

Overall: 52.5/100 → Needs confidence training
```

---

## Hướng dẫn sử dụng

### 📤 Step 1: Upload Audio

1. Click **"Browse files"** button
2. Select audio file:
   - ✅ Formats: WAV, MP3, M4A, FLAC
   - ✅ Max size: 25MB
   - ✅ Language: English

### 🎯 Step 2: Select Analysis

Choose metric(s) to analyze:

```
□ Volume Analysis
□ Velocity Analysis
□ Pause Analysis
□ Stretch Analysis
```

Hoặc:
```
☑ Comprehensive Analysis (All 4 metrics)
```

### ⚙️ Step 3: Configure Parameters

**For Volume:**
- No parameters needed

**For Velocity:**
- Model: whisper-1 / gpt-4o-transcribe

**For Pause:**
- Pause threshold: 0.2s (default)
- Silence threshold: -40 dB (default)

**For Stretch:**
- Threshold: 0.3 s/syllable (default)
- Method: Whisper only / **Whisper+ForceAlign** ⭐
- Model: whisper-1

### ▶️ Step 4: Analyze

1. Click **"🎯 Analyze"** button
2. Wait for processing:
   - Volume: ~2-3 seconds
   - Velocity: ~5-10 seconds
   - Pause: ~5-10 seconds
   - Stretch: ~10-15 seconds
3. View results

### 📊 Step 5: Interpret Results

**Look for:**
- ✅ Green indicators (good)
- ⚠️ Yellow/Orange (needs attention)
- ❌ Red (needs improvement)

**Check:**
- Numerical scores
- Classification labels
- Visual charts
- Recommendations

### 💾 Step 6: Export (Optional)

```
[Download JSON] - Full analysis data
[Download CSV]  - Metrics table
[Save Chart]    - Visualization image
```

---

## Use Cases & Ví dụ

### 🎤 Use Case 1: Presentation Training

**Scenario:** Luyện tập thuyết trình sản phẩm cho leadership team

**Goals:**
- Volume: Confident, consistent
- Velocity: Clear, professional (2.8-3.2 WPS)
- Pause: Strategic, minimal fillers
- Stretch: Emphasis on benefits

**Analysis Result:**
```
✅ Volume:   -20 dB   (Good energy)
✅ Velocity: 3.0 WPS  (Clear pacing)
⚠️ Pause:    0.6s avg (A bit long)
✅ Stretch:  18%      (Good emphasis)

Recommendations:
• Maintain volume and velocity ✅
• Shorten pause duration slightly
• Continue strategic emphasis
```

---

### 📞 Use Case 2: Call Center QA

**Scenario:** Đánh giá chất lượng cuộc gọi customer service

**Goals:**
- Volume: Audible but not aggressive
- Velocity: Patient, clear (2.5-3.0 WPS)
- Pause: Natural, few fillers
- Stretch: Clear pronunciation

**Analysis Result:**
```
❌ Volume:   -28 dB   (Too quiet)
❌ Velocity: 4.2 WPS  (Too fast)
❌ Pause:    40% filled ("um", "uh")
⚠️ Stretch:  35%      (Over-emphasis)

Recommendations:
• Increase volume 5-8 dB
• Slow down to 2.8-3.0 WPS
• Practice filler word reduction
• Relax pronunciation
```

---

### 🎓 Use Case 3: IELTS Speaking Practice

**Scenario:** Luyện thi IELTS Speaking Part 2

**Goals:**
- Volume: Confident projection
- Velocity: Natural (2.5-3.5 WPS)
- Pause: Strategic breaks only
- Stretch: Natural emphasis

**Analysis Result:**
```
✅ Volume:   -23 dB   (Good)
✅ Velocity: 2.9 WPS  (Natural)
⚠️ Pause:    25% filled
❌ Stretch:  48%      (Accent issue)

Recommendations:
• Volume and velocity excellent ✅
• Reduce fillers through practice
• Focus on syllable reduction
• Practice connected speech
```

---

## 📚 Technical References

### Technology Stack

- **Frontend:** Streamlit
- **Charts:** Plotly
- **Audio:** Librosa, Pydub
- **Transcription:** OpenAI Whisper API
- **Alignment:** ForceAlign (Wav2Vec2)
- **Dictionary:** CMU Pronouncing Dictionary

### Accuracy Specifications

| Metric | Method | Precision |
|--------|--------|-----------|
| Volume | RMS Energy | ±1 dB |
| Velocity | Word timestamps | ±0.1 WPS |
| Pause | Gap detection | ±50ms |
| Stretch (Whisper) | Word timestamps | ±50-100ms |
| Stretch (Hybrid) | ForceAlign | ±10ms ⭐ |

---

## 🆘 FAQ

**Q: File nào được hỗ trợ?**
A: WAV, MP3, M4A, FLAC. Max 25MB, English only.

**Q: Whisper vs Whisper+ForceAlign khác nhau như thế nào?**
A:
- Whisper: Timing ±50-100ms
- Hybrid: Timing ±10ms (chính xác gấp 5-10 lần!)
- Xem chi tiết: [FORCEALIGN_MECHANISM_EXPLAINED.md](FORCEALIGN_MECHANISM_EXPLAINED.md)

**Q: Làm sao để cải thiện score?**
A: Xem recommendations trong results. Practice theo từng metric:
- Volume: Voice projection exercises
- Velocity: Pacing drills
- Pause: Filler word elimination
- Stretch: Syllable reduction practice

**Q: Batch analysis xử lý bao nhiêu files?**
A: Maximum 10 files, process 5 parallel cùng lúc.

**Q: Export format nào available?**
A: JSON (full data), CSV (metrics table).

---

**Version:** 1.0.0
**Last Updated:** 2025-10-04
**Project:** SBF Audio Analyzer V1

---

## 📸 Screenshot Checklist

Cần chụp các ảnh UI sau:

- [ ] Volume Analysis full page
- [ ] Velocity Analysis with transcript
- [ ] Pause Analysis with timeline
- [ ] Stretch Analysis with threshold slider
- [ ] Comprehensive Dashboard (4 metrics)
- [ ] Single File Upload interface
- [ ] Batch Analysis page
- [ ] Parameter configuration panel
- [ ] Export options
- [ ] Use case comparison (good vs needs improvement)
