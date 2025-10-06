# Báo Cáo Dự Án: Sound-Based Foundation (SBF) - Phân Tích Giọng Nói

## Tổng Quan Dự Án

**Tên dự án**: Sound-Based Foundation (SBF) - Hệ thống phân tích giọng nói đa chiều
**Mục tiêu**: Phát triển hệ thống đo lường và phân tích 4 chỉ số cơ bản của giọng nói
**Ngôn ngữ**: Python
**Thư viện chính**: OpenAI Whisper, Parselmouth (Praat), Librosa, Streamlit

---

## 4 Chỉ Số Đo Lường Chính

### 1. STRETCH (Độ Kéo Dài)

#### **Định nghĩa:**
Stretch là hiện tượng kéo dài bất thường của các âm thanh, âm tiết hoặc từ ngữ vượt quá thời lượng bình thường trong lời nói.

#### **Mục đích sử dụng:**
- Chẩn đoán rối loạn ngôn ngữ (dysarthria, apraxia)
- Đánh giá bệnh lý thần kinh (Parkinson, đột quỵ)
- Theo dõi tiến trình trị liệu ngôn ngữ
- Nghiên cứu phát triển ngôn ngữ ở trẻ em

#### **Cách đo lường:**
- **Công thức**: Thời gian (giây) / Số âm tiết
- **Ngưỡng bình thường**: 4-6 âm tiết/giây
- **Ngưỡng stretch**: <3.5 âm tiết/giây hoặc >0.38 giây/âm tiết

#### **Input & Output:**
```
INPUT:
- File âm thanh (.wav, .mp3, .m4a)
- Transcript (tùy chọn)

OUTPUT:
- Bảng phân tích từng từ:
  * Từ ngữ
  * Thời gian bắt đầu/kết thúc
  * Số âm tiết
  * Điểm stretch
  * Phân loại (Normal/Stretched)
- Tổng quan:
  * Tỷ lệ từ bị stretch
  * Điểm trung bình
  * Biểu đồ phân bố
```

#### **Phương pháp kỹ thuật:**
1. **Whisper-1**: Timestamp từng từ (có vấn đề liên tục)
2. **Parselmouth + Praat**: Phân tích prosody chính xác hơn
3. **NeMo Forced Aligner**: Alignment thần kinh, độ chính xác cao
4. **ForceAlign**: Offline, miễn phí

---

### 2. VELOCITY (Tốc Độ Nói)

#### **Định nghĩa:**
Velocity là tốc độ phát âm được đo bằng số từ hoặc âm tiết được phát ra trong một đơn vị thời gian.

#### **Mục đích sử dụng:**
- Đánh giá khả năng giao tiếp
- Phát hiện rối loạn tốc độ nói
- Theo dõi hiệu quả trị liệu
- Nghiên cứu phát triển ngôn ngữ

#### **Cách đo lường:**
- **Words Per Second (WPS)**: Số từ/giây
- **Words Per Minute (WPM)**: Số từ/phút
- **Syllables Per Second**: Số âm tiết/giây

#### **Ngưỡng đánh giá:**
- **Chậm**: <1.5 từ/giây (<90 từ/phút)
- **Bình thường**: 1.5-2.5 từ/giây (90-150 từ/phút)
- **Nhanh**: >2.5 từ/giây (>150 từ/phút)

#### **Input & Output:**
```
INPUT:
- File âm thanh
- Ngưỡng tốc độ (tùy chỉnh)

OUTPUT:
- Chỉ số tốc độ:
  * WPS (từ/giây)
  * WPM (từ/phút)
  * Thời gian nói thực tế
  * Tỷ lệ câm lặng
- Phân loại: Slow/Normal/Fast
- Biểu đồ tốc độ theo thời gian
```

---

### 3. VOLUME (Âm Lượng)

#### **Định nghĩa:**
Volume là cường độ âm thanh được đo bằng decibel (dB), phản ánh mức độ to/nhỏ của giọng nói.

#### **Mục đích sử dụng:**
- Đánh giá rối loạn âm lượng giọng nói
- Phát hiện vấn đề hô hấp/thanh quản
- Theo dõi sức khỏe giọng nói
- Đào tạo kỹ năng thuyết trình

#### **Cách đo lường:**
- **RMS Energy**: Năng lượng trung bình
- **Peak Amplitude**: Biên độ đỉnh
- **Dynamic Range**: Khoảng biến thiên âm lượng

#### **Ngưỡng đánh giá:**
- **Nhỏ**: <50 dB
- **Bình thường**: 50-70 dB
- **To**: >70 dB

#### **Input & Output:**
```
INPUT:
- File âm thanh
- Ngưỡng âm lượng

OUTPUT:
- Phân tích âm lượng:
  * Âm lượng trung bình
  * Âm lượng tối đa/tối thiểu
  * Độ biến thiên
  * Phân bố âm lượng
- Biểu đồ:
  * Đường cong âm lượng theo thời gian
  * Histogram phân bố
- Phân loại: Quiet/Normal/Loud
```

---

### 4. RHYTHM (Nhịp Điệu)

#### **Định nghĩa:**
Rhythm là mẫu hình thời gian của lời nói, bao gồm nhịp độ, trọng âm, và khoảng nghỉ giữa các âm tiết/từ.

#### **Mục đích sử dụng:**
- Đánh giá rối loạn prosody
- Phát hiện vấn đề thần kinh ảnh hưởng nhịp điệu
- Nghiên cứu đặc điểm ngôn ngữ
- Đào tạo phát âm/diễn thuyết

#### **Cách đo lường:**
- **Inter-Onset Intervals**: Khoảng cách giữa các điểm khởi đầu
- **Rhythm Ratio**: Tỷ lệ nhịp điệu
- **Stress Pattern**: Mẫu trọng âm
- **Pause Distribution**: Phân bố khoảng nghỉ

#### **Input & Output:**
```
INPUT:
- File âm thanh
- Tham số phân tích nhịp điệu

OUTPUT:
- Phân tích nhịp điệu:
  * Chỉ số đều đặn nhịp điệu
  * Mẫu trọng âm
  * Phân bố khoảng nghỉ
  * Tần suất nhịp điệu
- Biểu đồ:
  * Pattern nhịp điệu
  * Spectrogram với đánh dấu nhịp
- Phân loại: Regular/Irregular/Atypical
```

---

## Kiến Trúc Hệ Thống

### **Frontend:**
- **Streamlit**: Giao diện web tương tác
- **Matplotlib/Plotly**: Biểu đồ và trực quan hóa
- **Pandas**: Xử lý và hiển thị dữ liệu dạng bảng

### **Backend Audio Processing:**
- **OpenAI Whisper**: Transcription và word timestamps
- **Parselmouth (Praat)**: Phân tích prosody và voice quality
- **Librosa**: Xử lý âm thanh và feature extraction
- **NeMo Forced Aligner**: Alignment chính xác cao
- **PyDub**: Chuyển đổi format âm thanh

### **Core Modules:**
```
audio-analyzer/
├── openai_transcriber.py      # Whisper integration
├── stretch_analyzer.py        # Stretch analysis
├── velocity_analyzer.py       # Velocity analysis
├── volume_analyzer.py         # Volume analysis
├── rhythm_analyzer.py         # Rhythm analysis (future)
├── forcealign_transcriber.py  # ForceAlign integration
├── parselmouth_analyzer.py    # Praat integration (new)
└── app.py                     # Main Streamlit app
```

---

## Quy Trình Phân Tích

### **Bước 1: Tiền xử lý âm thanh**
1. Load file âm thanh (hỗ trợ nhiều format)
2. Chuyển đổi sampling rate về 16kHz/22kHz
3. Noise reduction và normalization
4. Phát hiện speech/silence segments

### **Bước 2: Transcription & Alignment**
1. Whisper transcription để có text
2. Forced alignment để có timestamps chính xác
3. Phoneme-level alignment (nếu cần)
4. Quality check và post-processing

### **Bước 3: Feature Extraction**
1. **Prosodic features**: F0, intensity, duration
2. **Spectral features**: MFCC, spectral centroid
3. **Temporal features**: onset detection, rhythm
4. **Voice quality**: jitter, shimmer, HNR

### **Bước 4: Metric Calculation**
1. **Stretch**: Duration per syllable analysis
2. **Velocity**: Words/syllables per second
3. **Volume**: RMS energy và dynamic range
4. **Rhythm**: Temporal pattern analysis

### **Bước 5: Visualization & Report**
1. Individual metric dashboards
2. Comparative analysis charts
3. Clinical interpretation
4. Export results (PDF, JSON, CSV)

---

## Tính Năng Nâng Cao

### **Real-time Analysis:**
- Live microphone input
- Streaming analysis
- Real-time feedback

### **Batch Processing:**
- Multiple file analysis
- Comparative reports
- Statistical analysis across sessions

### **Clinical Integration:**
- Patient database
- Progress tracking
- Therapy recommendations
- Clinical note generation

### **Multi-language Support:**
- English, Vietnamese, và các ngôn ngữ khác
- Language-specific norms
- Cross-linguistic analysis

---

## Ứng Dụng Thực Tế

### **Y tế:**
- Chẩn đoán rối loạn ngôn ngữ
- Theo dõi tiến trình điều trị
- Đánh giá sau tai biến/chấn thương
- Sàng lọc sớm ở trẻ em

### **Giáo dục:**
- Đào tạo kỹ năng thuyết trình
- Học ngôn ngữ thứ hai
- Feedback phát âm
- Đánh giá năng lực giao tiếp

### **Nghiên cứu:**
- Phonetics và prosody research
- Cross-linguistic studies
- Development studies
- Technology evaluation

### **Công nghiệp:**
- Voice assistant quality
- Speech synthesis evaluation
- Call center training
- Broadcasting/media

---

## Kết Luận

Hệ thống SBF cung cấp một giải pháp toàn diện cho việc phân tích giọng nói đa chiều, kết hợp các công nghệ AI hiện đại với các phương pháp phonetics truyền thống. Với 4 chỉ số cốt lõi (Stretch, Velocity, Volume, Rhythm), hệ thống có thể ứng dụng rộng rãi trong y tế, giáo dục, và nghiên cứu khoa học.

**Phiên bản hiện tại**: v1.0
**Ngày cập nhật**: 2024-09-27
**Tác giả**: AI Development Team
**Liên hệ**: [Email/Contact Information]