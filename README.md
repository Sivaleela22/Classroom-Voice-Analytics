# 🎓 Classroom Voice Analytics MVP

## 📌 Overview

This project is a prototype system developed as part of the MakerGhat AI/ML Internship pre-work assignment.
The goal is to convert classroom audio into meaningful insights such as transcription, interaction patterns, and engagement metrics.

---

## 🚀 Approach

The system is designed as a simple pipeline:

1. **Audio Input**

   * User uploads classroom audio (`.wav` / `.mp3`) through a Streamlit interface.

2. **Speech-to-Text (Transcription)**

   * The audio is processed using a pre-trained speech recognition model.
   * The model converts spoken classroom audio into text.
   * Supports Indic languages (e.g., Hindi).

3. **Text Processing**

   * The transcript is split into sentences using basic text processing techniques.
   * Each sentence is analyzed individually.

4. **Speaker Classification (Heuristic-Based)**

   * Sentences are classified as Teacher or Student using simple rules:

     * Questions → Teacher
     * Very short responses → Student
     * Longer explanations → Teacher

5. **Analysis & Metrics**

   * Extract interaction features like questions, responses, and talk distribution.
   * Compute engagement metrics.

6. **Visualization**

   * Results are displayed using a Streamlit dashboard:

     * Transcript
     * Metrics
     * Classroom summary

---

## 📊 Engagement Metrics

### 1. Teacher Dominance Ratio (TDR)

**Formula:**

```
TDR = teacher_sentences / total_sentences
```

**Meaning:**
Measures how much the session is dominated by the teacher.

---

### 2. Student Participation Indicator (SPI)

**Formula:**

```
SPI = student_sentences / total_sentences
```

**Meaning:**
Indicates how actively students are participating.

---

### 3. Interaction Count (IC)

**Formula:**

```
IC = questions_asked + student_responses
```

**Meaning:**
Represents total interactions between teacher and students.

---

### 4. Engagement Score (ES)

**Formula:**

```
ES = min(1.0, (IC / total_sentences) × 2)
```

**Meaning:**
Provides an overall estimate of classroom engagement (0–1 scale).

---

## 🛠️ Tools & Technologies Used

* **Python** – Core programming language
* **Streamlit** – Web interface for MVP demo
* **Whisper (OpenAI)** – Speech-to-text transcription model
* **FFmpeg** – Audio processing support
* **NumPy** – Basic numerical operations
* **Regex (re module)** – Text processing

---

## ⚙️ Assumptions

* Classroom audio is primarily teacher-led.
* Questions are mostly asked by the teacher.
* Short sentences (1–3 words) are treated as student responses.
* Silence duration is approximated (not precisely measured).
* Word count is used as a proxy for talk time.
* Approximate transcription accuracy is acceptable for this prototype.

---

## ⚠️ Limitations

* Speaker classification is heuristic-based (not a trained model).
* Student speech may be underrepresented if audio quality is low.
* Whisper transcription may contain minor errors (especially in noisy environments).
* No real-time transcription (batch processing only).
* Silence detection is estimated, not computed from audio signals.
* Performance may be slower for long audio files (CPU-based processing).

---

## 🎯 Conclusion

This project demonstrates a basic but functional pipeline for transforming classroom audio into actionable insights.
While simplified, it provides a strong foundation that can be extended with:

* Real-time transcription
* Advanced speaker diarization
* Improved engagement analytics

---

## 📷 Demo

* Screenshots / screen recording included in submission
* Streamlit app can be run locally using:

```
streamlit run app.py
```

---

## 👤 Author

**Sivaleela Jonnalagadda**

