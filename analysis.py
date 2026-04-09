from utils import split_sentences, is_question, is_student_response


def classify_speaker(sentence: str) -> str:
    """
    Classify a sentence as Teacher or Student.

    FIX: Student response check now runs BEFORE question check.
    Previously, question check ran first — so student ack words like 'ना',
    'नहीं' (which were in QUESTION_INDICATORS) caused student lines to be
    wrongly tagged as Teacher.

    Priority order:
      1. Pure student response (ack words / very short)  → Student
      2. Contains a question indicator                   → Teacher
      3. Long sentence (>12 words)                       → Teacher
      4. Medium-short sentence (≤8 words)                → Student
      5. Default                                         → Teacher
    """
    # Step 1: Check student FIRST (this is the key bug fix)
    if is_student_response(sentence):
        return "Student"

    # Step 2: Then check for teacher question
    if is_question(sentence):
        return "Teacher"

    # Step 3: Word count heuristics
    word_count = len(sentence.split())
    if word_count > 12:
        return "Teacher"
    if word_count <= 8:
        return "Student"

    return "Teacher"


def estimate_talk_time(sentences: list, total_duration_seconds: float = None):
    """
    Estimate talk time per speaker using word count as a proxy.

    FIX: teacher_time + student_time + silence_time now always equals
    total_duration_seconds exactly.

    Previously the three values were computed independently using separate
    ratios (0.85 for speech, 0.15 for silence), which could drift apart
    when student_words = 0 or word counts were uneven.

    Corrected approach:
      silence_duration = total_duration * 0.15        (fixed 15% slice)
      speech_duration  = total_duration * 0.85        (remaining 85%)
      teacher_time     = (teacher_words / total_words) * speech_duration
      student_time     = (student_words / total_words) * speech_duration
      → teacher_time + student_time + silence_duration == total_duration ✓

    Average speaking rate assumed: ~120 words/min (2 words/sec)
    """
    WORDS_PER_SECOND = 2.0    # ~120 wpm, average classroom pace
    SILENCE_RATIO    = 0.15   # 15% of audio assumed to be silence/pause

    teacher_words = 0
    student_words = 0

    for speaker, sentence in sentences:
        wc = len(sentence.split())
        if speaker == "Teacher":
            teacher_words += wc
        else:
            student_words += wc

    total_words = teacher_words + student_words

    if total_duration_seconds and total_duration_seconds > 0:
        # Fixed 3-part split that always sums to total_duration_seconds
        silence_duration = total_duration_seconds * SILENCE_RATIO
        speech_duration  = total_duration_seconds - silence_duration  # = 85%

        if total_words > 0:
            teacher_time = (teacher_words / total_words) * speech_duration
            student_time = (student_words / total_words) * speech_duration
        else:
            # No words at all — give all speech time to teacher, student = 0
            teacher_time = speech_duration
            student_time = 0.0

        # Verification: teacher_time + student_time + silence_duration == total_duration_seconds

    else:
        # No audio duration provided — estimate purely from word count
        teacher_time     = teacher_words / WORDS_PER_SECOND
        student_time     = student_words / WORDS_PER_SECOND
        silence_duration = (total_words / WORDS_PER_SECOND) * SILENCE_RATIO

    return {
        "teacher_words":        teacher_words,
        "student_words":        student_words,
        "teacher_time_sec":     round(teacher_time),
        "student_time_sec":     round(student_time),
        "silence_duration_sec": round(silence_duration),
        "teacher_time_fmt":     _fmt_time(teacher_time),
        "student_time_fmt":     _fmt_time(student_time),
        "silence_fmt":          _fmt_time(silence_duration),
    }


def _fmt_time(seconds: float) -> str:
    """Convert seconds to mm:ss string."""
    seconds = max(0, int(seconds))
    m, s = divmod(seconds, 60)
    return f"{m}m {s:02d}s"


def analyze_classroom(text: str, audio_duration_sec: float = None) -> dict:
    """
    Full classroom analysis pipeline.

    Metrics produced:
    ─────────────────────────────────────────────────────────────────
    1.  Teacher vs Student speech  — heuristic sentence classification
    2.  Teacher talk-time          — word-count proportion of audio
    3.  Student talk-time          — word-count proportion of audio
    4.  Questions asked            — keyword + punctuation detection
    5.  Student response count     — short sentence / ack word detection
    6.  Silence duration           — 15% of total audio duration
    7.  Teacher Dominance Ratio    = teacher_sentences / total_sentences
    8.  Student Participation      = student_sentences / total_sentences
    9.  Interaction Count          = questions + responses
    10. Engagement Score           = min(1.0, (IC / total_sentences) × 2)
    ─────────────────────────────────────────────────────────────────
    """
    sentences = split_sentences(text)

    if not sentences:
        return _empty_result()

    teacher_sentences = []
    student_sentences = []
    questions  = 0
    responses  = 0
    labeled_sentences = []

    for s in sentences:
        speaker = classify_speaker(s)
        labeled_sentences.append((speaker, s))

        if speaker == "Teacher":
            teacher_sentences.append(s)
            if is_question(s):
                questions += 1
        else:
            student_sentences.append(s)
            responses += 1

    total           = len(sentences)
    teacher_ratio   = len(teacher_sentences) / total
    student_ratio   = len(student_sentences) / total
    ic              = questions + responses
    engagement_score = min(1.0, (ic / total) * 2) if total else 0.0

    talk_time = estimate_talk_time(labeled_sentences, audio_duration_sec)

    return {
        # Core analysis
        "teacher_ratio":         round(teacher_ratio, 3),
        "student_participation": round(student_ratio, 3),
        "questions":             questions,
        "responses":             responses,
        "total_sentences":       total,
        # Talk time
        "teacher_words":         talk_time["teacher_words"],
        "student_words":         talk_time["student_words"],
        "teacher_time_fmt":      talk_time["teacher_time_fmt"],
        "student_time_fmt":      talk_time["student_time_fmt"],
        "silence_fmt":           talk_time["silence_fmt"],
        "teacher_time_sec":      talk_time["teacher_time_sec"],
        "student_time_sec":      talk_time["student_time_sec"],
        "silence_duration_sec":  talk_time["silence_duration_sec"],
        # Engagement metrics
        "interaction_count":     ic,
        "engagement_score":      round(engagement_score, 3),
        # Full breakdown
        "labeled_sentences":     labeled_sentences,
    }


def _empty_result():
    return {
        "teacher_ratio": 0.0, "student_participation": 0.0,
        "questions": 0, "responses": 0, "total_sentences": 0,
        "teacher_words": 0, "student_words": 0,
        "teacher_time_fmt": "0m 00s", "student_time_fmt": "0m 00s",
        "silence_fmt": "0m 00s",
        "teacher_time_sec": 0, "student_time_sec": 0, "silence_duration_sec": 0,
        "interaction_count": 0, "engagement_score": 0.0,
        "labeled_sentences": []
    }