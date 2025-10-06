# ForceAlign Mechanism - Cơ chế hoạt động chi tiết

## 📋 Tổng quan

ForceAlign là kỹ thuật **Forced Alignment** - "ép buộc" việc khớp (align) giữa:
- **Text** (transcript đã biết trước)
- **Audio** (file âm thanh thực tế)

Kết quả: Timing chính xác cho từng từ/âm vị (phoneme) với độ chính xác ±10ms.

---

## 🔄 Quy trình tổng quan

```
INPUT:
  Audio: [waveform liên tục]
  Text:  "DEMANDING" (đã biết trước)

PROCESS:
  Step 1: Chia audio thành frames nhỏ (10-25ms mỗi frame)
  Step 2: Trích xuất acoustic features từ mỗi frame
  Step 3: Chia text thành phonemes
  Step 4: Khớp phonemes với audio frames (Viterbi Algorithm)
  Step 5: Tìm boundaries của từng từ

OUTPUT:
  "DEMANDING": 1.18s → 1.78s (chính xác ±10ms)
```

---

## 📊 Step 1: Chia audio thành frames

Audio là sóng liên tục, được chia thành **chunks nhỏ** (frames):

```
Audio waveform (1.18s - 1.78s = 600ms):
├─────┬─────┬─────┬─────┬─────┬─────┬...
Frame Frame Frame Frame Frame Frame
118   119   120   121   122   123
↓     ↓     ↓     ↓     ↓     ↓
10ms  10ms  10ms  10ms  10ms  10ms

Tổng: 600ms ÷ 10ms = 60 frames cho từ "demanding"
```

**Tại sao chia nhỏ?**
- Phoneme thay đổi rất nhanh (50-200ms)
- Cần độ phân giải cao để phát hiện ranh giới
- 10ms là đủ nhỏ để catch transitions

---

## 🎵 Step 2: Trích xuất Acoustic Features

Mỗi frame được chuyển thành **vector đặc trưng**:

```python
# Frame 118 (1.18s):
Waveform: [amplitude values]
    ↓
Feature Extraction:
    ↓
Features = [
    MFCC coefficients: [2.3, -1.1, 0.8, ...],  # 13-39 values
    Energy: 0.65,                               # Độ lớn
    Zero-crossing rate: 0.32,                   # Tần số
    Spectral features: [...],                   # Phổ tần
]

# Mỗi frame → 1 vector ~40 dimensions
```

**Các đặc trưng này mô tả:**
- Âm cao/thấp (pitch)
- Năng lượng (loudness)
- Cấu trúc phổ tần (formants)
- → Đủ để phân biệt phonemes

### Ví dụ: Phoneme "AE" (như trong "cat")

```python
Acoustic signature của "AE":
- F1 (formant 1): ~700 Hz   ← Low first formant
- F2 (formant 2): ~1700 Hz  ← High second formant
- Duration: Usually 100-250ms

Frame 148 features:
F1: 695 Hz  ┐
F2: 1720 Hz ├─ MATCH! Đây chắc chắn là "AE"
Duration: ✓ ┘
```

---

## 🔤 Step 3: Chia text thành Phonemes

```python
# Text đã biết: "DEMANDING"

# Tra từ điển phoneme (CMU Dictionary hoặc G2P model):
"DEMANDING" → Phoneme sequence:

D   IH   M   AE   N   D   IH   NG
|    |    |    |    |   |    |    |
└─ Plosive consonant (âm tắc)
     └─ Short vowel (nguyên âm ngắn)
          └─ Nasal consonant (âm mũi)
               └─ Open vowel (nguyên âm mở)
                    └─ Nasal consonant
                         └─ Plosive
                              └─ Short vowel
                                   └─ Nasal

# Tổng: 8 phonemes cần khớp với ~60 audio frames
```

**Đặc điểm phonemes:**

| Phoneme | Type | Acoustic Signature | Duration |
|---------|------|-------------------|----------|
| D | Plosive | Burst energy, low frequency | 10-30ms |
| IH | Vowel | Steady formants, mid energy | 30-80ms |
| M | Nasal | Low F2, nasal formant | 40-100ms |
| AE | Vowel | F1~700Hz, F2~1700Hz | 100-250ms |
| N | Nasal | High F2, nasal formant | 40-100ms |
| NG | Nasal | Velar, low energy | 30-80ms |

---

## 🎯 Step 4: Khớp Phonemes với Frames - Viterbi Algorithm

Đây là **TRÁI TIM** của ForceAlign!

### A. Hidden Markov Model (HMM)

Mỗi phoneme được mô hình hóa như một **state machine** với 3 states:

```python
# Ví dụ: Phoneme "D" (plosive) có 3 states:

State 1: Silence/closure  (miệng đóng, không khí tích tụ)
   ↓
State 2: Burst release    (mở miệng đột ngột, burst sound)
   ↓
State 3: Transition       (chuyển sang âm tiếp theo)

# Mỗi state có probability distribution cho features
# P(features | state) được học từ training data
```

### B. Viterbi Alignment

Tìm **đường đi tối ưu** qua các states để maximize probability:

```
Phonemes:  D      IH     M      AE     N      D      IH     NG
States:   [123]  [123]  [123]  [123]  [123]  [123]  [123]  [123]
           ↓      ↓      ↓      ↓      ↓      ↓      ↓      ↓
Frames:   118─┐  125─┐  132─┐  145─┐  160─┐  168─┐  172─┐  175─┐
          119 │  126 │  133 │  146 │  161 │  169 │  173 │  176 │
          120 │  127 │  134 │  147 │  162 │  170 │  174 │  177 │
          121 │  128 │  135 │  148 │  163 │  171 │  ... │  178 │
          122 │  129 │  ... │  ... │  ... │  ... │
          123 │  130 │
          124─┘  131─┘

Algorithm tìm match tốt nhất giữa phoneme states và frame features
```

### C. Scoring Mechanism

```python
# Với mỗi frame, tính xác suất:
P(frame_features | phoneme_state)

# Ví dụ Frame 118:
Features: [burst sound, low freq, high energy=0.65]
                ↓
P(features | "D" state-1) = 0.05
P(features | "D" state-2) = 0.85  ← HIGH! Khớp với burst!
P(features | "D" state-3) = 0.12
P(features | "IH" state-1) = 0.03

# → Frame 118 thuộc phoneme "D" state-2

# Ví dụ Frame 125:
Features: [steady formants, mid energy=0.45]
                ↓
P(features | "D" state-3) = 0.25
P(features | "IH" state-1) = 0.78  ← HIGH! Khớp với vowel!
P(features | "M" state-1) = 0.05

# → Frame 125 là ranh giới D→IH
```

---

## 📈 Step 5: Kết quả Frame-by-Frame

```python
# FRAME-BY-FRAME ANALYSIS CHO "DEMANDING":

Time    Frame   Features                    Best Match      Phoneme
────────────────────────────────────────────────────────────────────
1.18s   118     [burst, low freq, high E]   D-state2        D
1.19s   119     [transition, decreasing]    D-state3        D
1.20s   120     [high formants, steady]     IH-state1       ├─ IH
1.21s   121     [vowel, mid energy]         IH-state2       │
1.22s   122     [vowel sustained]           IH-state3       ┘
1.23s   123     [nasal onset, low F2]       M-state1        M
1.24s   124     [nasal formant]             M-state2        M
1.25s   125     [nasal ending]              M-state3        M
1.26s   126     [vowel onset]               AE-state1       ├─ AE
...     ...     [open vowel sustained]      AE-state2       │  (longest)
1.57s   157     [vowel ending]              AE-state3       ┘
1.58s   158     [nasal onset]               N-state1        N
...
1.78s   178     [nasal, velar, low E]       NG-state3       NG

# TỔNG HỢP:
Phoneme  Frames      Time Range    Duration    Notes
─────────────────────────────────────────────────────────────
D        118-119     1.18-1.19s    10ms        Burst release
IH       120-124     1.20-1.24s    40ms        Short vowel
M        125-131     1.25-1.31s    60ms        Nasal
AE       132-157     1.32-1.57s    250ms       ← Vowel dài nhất
N        158-167     1.58-1.67s    90ms        Nasal
D        168-171     1.68-1.71s    30ms        Second plosive
IH       172-174     1.72-1.74s    20ms        Reduced vowel
NG       175-178     1.75-1.78s    30ms        Final nasal

# → Từ "DEMANDING": 1.18s - 1.78s (chính xác ±10ms!)
```

---

## 🆚 So sánh: Whisper vs ForceAlign

### WHISPER (ASR - Automatic Speech Recognition)

```python
# Whisper phải làm 2 việc CÙNG LÚC:
Task 1: Nhận diện từ (Speech → Text)  ← Khó!
Task 2: Tìm timing của từ              ← Phụ thuộc Task 1

# Quy trình:
Audio → Feature Extraction → Encoder → Decoder
                                          ↓
                              "Đoán" cả từ + timing
                                          ↓
                              Không chắc chắn 100%
                                          ↓
                              Timing ±50-100ms
```

**Vấn đề của Whisper:**
- ❌ Phải **đoán** từ là gì → có thể sai
- ❌ Timing dựa trên **attention weights** → không chính xác tuyệt đối
- ❌ Model optimize cho **transcript accuracy**, không phải timing
- ❌ Lỗi ±50-100ms là bình thường

**Ví dụ Whisper có thể sai:**
```python
# Audio thực tế:
"demanding" từ 1.180s → 1.780s (0.600s)

# Whisper có thể cho:
"demanding" từ 1.150s → 1.750s (0.600s)
# → Thời lượng đúng, nhưng vị trí sai 30ms!
# → Stretch score bị ảnh hưởng!
```

---

### FORCEALIGN (Forced Alignment)

```python
# ForceAlign chỉ làm 1 việc duy nhất:
Task: Tìm timing cho từ ĐÃ BIẾT  ← Dễ hơn nhiều!

# Quy trình:
Audio + Text (known) → Phoneme Sequence → HMM States
                                              ↓
                                    Viterbi Algorithm
                                              ↓
                                    Acoustic Feature Matching
                                              ↓
                                    Timing CHÍNH XÁC ±10ms
```

**Tại sao ForceAlign chính xác hơn?**

✅ **Đã biết từ** → Không cần đoán
✅ **Chỉ tìm vị trí** → Tập trung 100% vào timing
✅ **Dùng acoustic features** → Khớp waveform với phoneme signatures
✅ **Viterbi guarantees** → Optimal alignment path
✅ **Frame-level precision** → 10ms resolution

---

## 🔬 Tại sao Timing chính xác?

### 1. Không cần đoán từ

```python
# WHISPER:
- Phải đoán "demanding" hoặc "demand" hoặc "dementing"?
- Nếu đoán sai từ → timing cũng sai

# FORCEALIGN:
- Đã BIẾT chắc chắn là "demanding"
- Chỉ cần tìm nó ở đâu trong audio
- → Không có uncertainty về text!
```

### 2. Tối ưu hóa cho alignment

```python
# WHISPER model objective:
- Maximize P(text | audio)
- Primary goal: Transcript accuracy
- Timing: Byproduct (phụ phẩm)

# FORCEALIGN model objective:
- Find best alignment path
- Primary goal: Timing accuracy
- Chuyên dụng cho phoneme-to-frame mapping
```

### 3. Acoustic matching vật lý

```python
# FORCEALIGN nhìn trực tiếp vào waveform:

Audio waveform:
     ╱╲    ← Energy spike! Burst sound!
────╱  ╲────────
1.18s
    ↓
  Đây là phoneme "D" (plosive)

     ╱╲╱╲╱╲  ← Vowel formants
────╱      ╲────
1.48s
    ↓
  Đây là phoneme "AE" (open vowel)

# Match chính xác từng phoneme với acoustic signature
```

### 4. Constraints từ transcript

```python
# ForceAlign BIẾT trước sequence phải là:
D → IH → M → AE → N → D → IH → NG

# Không thể:
- Skip phonemes (phải đủ 8 phonemes)
- Reorder (phải đúng thứ tự)
- Add extra phonemes

# → Chỉ cần tìm WHERE, không cần tìm WHAT
# → Whisper phải tìm cả WHAT và WHERE → khó hơn nhiều!
```

---

## 💎 Hybrid Method: Whisper + ForceAlign

Kết hợp điểm mạnh của cả hai:

```
┌─────────────────────────────────────────┐
│  WHISPER + FORCEALIGN HYBRID            │
├─────────────────────────────────────────┤
│                                         │
│  Step 1: Whisper                        │
│  - High accuracy transcript             │
│  - "MY BOSS IS VERY DEMANDING"          │
│  - Đảm bảo đúng từ                      │
│                                         │
│  Step 2: ForceAlign                     │
│  - Use Whisper's transcript             │
│  - Find precise timing                  │
│  - Acoustic feature matching            │
│  - "demanding": 1.18s - 1.78s           │
│                                         │
│  = BEST OF BOTH WORLDS                  │
│  - 100% transcript accuracy             │
│  - ±10ms timing precision               │
└─────────────────────────────────────────┘
```

### Quy trình Hybrid:

```python
# Bước 1: Whisper cho transcript
from src.transcribers.openai_transcriber import transcribe_with_openai_timestamps

whisper_words = transcribe_with_openai_timestamps(audio_path)
transcript = " ".join([w["word"] for w in whisper_words])
# → "MY BOSS IS VERY DEMANDING"

# Bước 2: ForceAlign với transcript từ Whisper
from src.transcribers.forcealign_transcriber import transcribe_with_forcealign_timestamps

word_timestamps = transcribe_with_forcealign_timestamps(
    audio_path,
    transcript  # ← Transcript chính xác từ Whisper!
)

# Kết quả:
[
    {"word": "my", "start": 0.00, "end": 0.15},
    {"word": "boss", "start": 0.15, "end": 0.45},
    {"word": "is", "start": 0.45, "end": 0.58},
    {"word": "very", "start": 0.58, "end": 0.85},
    {"word": "demanding", "start": 1.18, "end": 1.78},  # ← Chính xác!
]
```

---

## 📊 Visualization

```
AUDIO WAVEFORM:
     ┌───────────── "DEMANDING" ──────────────┐
     │                                         │
  ╱╲ │ ╱╲  ╱─────╲  ╱──╲ ╱╲  ╱──╲  ╱╲        │
─╱  ╲┼╱  ╲╱       ╲╱    ╲  ╲╱    ╲╱  ╲───────┤
     │D  IH   M     AE    N   D   IH   NG     │
     │                                         │
    1.18s                                   1.78s

FORCEALIGN FRAMES (10ms each):
     ├─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┤...├─┤
     118 119 120 121 ... 175 176 177 178

PHONEME STATES (HMM):
     [D──][IH─][M──][AE─────────][N───][D─][IH][NG─]
       ↑              ↑                            ↑
    Start         Longest                       End
   (1.18s)      (vowel AE)                   (1.78s)

VITERBI MATCHING:
Frame features → Best phoneme state → Word boundaries
     [0.85]         "D" state-2          1.18s (start)
     [0.78]         "IH" state-1
     ...            ...                  ...
     [0.72]         "NG" state-3         1.78s (end)
```

---

## 🎯 Ứng dụng cho Stretch Analysis

### Tại sao cần timing chính xác?

```python
# Stretch score = Duration / Syllables

# VỚI WHISPER (±50ms error):
Word: "demanding"
Duration: 0.55s (có thể sai!)
Syllables: 3
Stretch: 0.55 / 3 = 0.183 s/syllable

# VỚI FORCEALIGN (±10ms):
Word: "demanding"
Duration: 0.60s (chính xác!)
Syllables: 3
Stretch: 0.60 / 3 = 0.200 s/syllable

# Chênh lệch: 0.017s/syllable = 8.5% error!
# → Có thể classify sai Normal vs Stretched!
```

### Threshold sensitivity:

```python
# Stretch threshold = 0.19 s/syllable

# Whisper timing:
- Stretch score: 0.183 → NORMAL (sai!)

# ForceAlign timing:
- Stretch score: 0.200 → STRETCHED (đúng!)

# → Timing chính xác là critical cho stretch analysis!
```

---

## 📚 Tham khảo Code

### File locations:

1. **ForceAlign Transcriber**
   `src/transcribers/forcealign_transcriber.py`
   - `transcribe_with_forcealign_timestamps()` - Core alignment function

2. **Hybrid Methods**
   `src/transcribers/deepgram_transcriber.py`
   - `whisper_forcealign_hybrid_timestamps()` - Whisper + ForceAlign
   - `hybrid_deepgram_forcealign_timestamps()` - Deepgram + ForceAlign

3. **Stretch Analyzer**
   `src/analyzers/stretch_analyzer.py`
   - `analyze_stretch()` - Uses hybrid methods for stretch analysis

---

## ✅ Kết luận

**ForceAlign hoạt động bằng cách:**

1. ✅ Chia audio thành frames nhỏ (10ms)
2. ✅ Trích xuất acoustic features từ mỗi frame
3. ✅ Chuyển text thành phoneme sequence (đã biết trước)
4. ✅ Dùng HMM + Viterbi để match phonemes với frames
5. ✅ Tìm word boundaries chính xác ±10ms

**Ưu điểm so với Whisper standalone:**
- Không cần đoán từ → chính xác hơn
- Tối ưu cho timing → precision cao
- Acoustic matching → dựa trên vật lý âm thanh
- Frame-level resolution → 10ms precision

**Best practice cho Stretch Analysis:**
- Dùng **Whisper + ForceAlign Hybrid**
- Whisper: Transcript accuracy
- ForceAlign: Timing precision
- = Perfect combination!

---

**Generated:** 2025-10-04
**Project:** SBF Audio Analyzer V1
