import re

# ── Question indicators (Hindi + English) ────────────────────────────────────
# NOTE: 'ना' removed from here — it is a student ack word, not a question word.
# Keeping it here caused student responses to be wrongly tagged as Teacher.
QUESTION_INDICATORS = [
    # Hindi question words
    'क्या', 'कैसे', 'कितना', 'कितने', 'कितनी', 'कब', 'कहाँ', 'कहां',
    'कौन', 'किसने', 'किसको', 'क्यों', 'क्यूं',
    # Hindi question phrases
    'बताओ', 'बताइए', 'बताना है', 'है ना', 'है न',
    'पूछूंगी', 'पूछेंगे', 'बोलो', 'बोलिए', 'समझे', 'समझे?',
    'बता सकते', 'बता दो', 'कोन बताएगा', 'कौन बताएगा',
    # English
    'what', 'why', 'how', 'when', 'where', 'who', 'which',
    'can you', 'do you', 'did you', 'is it', 'are you', 'will you'
]

# Student acknowledgement / short-answer words
STUDENT_ACK = {
    'हाँ', 'हां', 'हान', 'नहीं', 'जी', 'जी हाँ', 'जी नहीं',
    'चार', 'पाँच', 'तीन', 'दो', 'एक', 'छह', 'सात',
    'yes', 'no', 'ok', 'okay', 'sir', "ma'am", 'haan', 'nahi',
    'ठीक', 'सही', 'समझा', 'समझी', 'पता', 'नहीं पता',
    'ना',   # moved from QUESTION_INDICATORS — it's an acknowledgement, not a question
}

# Discourse markers used to break long Hindi clauses
CLAUSE_BREAK_WORDS = {'ठीक', 'लेकिन', 'इसलिए', 'क्योंकि', 'मतलब'}
CLAUSE_BREAK_LONG  = {'अब', 'फिर', 'तो', 'और'}


def split_sentences(text: str) -> list:
    """
    Smart sentence splitter for Hindi classroom transcripts.

    Step 1: Split on hard punctuation (? ! . । newline)
    Step 2: Break long chunks (>15 words) on Hindi clause markers
            to surface individual questions and statements.
    """
    # Hard punctuation split
    chunks = re.split(r'[?!\n।]|(?<!\d)\.(?!\d)', text)
    result = []

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk or len(chunk) < 4:
            continue
        words = chunk.split()
        if len(words) <= 15:
            result.append(chunk)
            continue

        # Break long chunks on clause markers
        current = []
        for word in words:
            current.append(word)
            if word in CLAUSE_BREAK_WORDS and len(current) >= 8:
                result.append(' '.join(current))
                current = []
            elif word in CLAUSE_BREAK_LONG and len(current) >= 12:
                result.append(' '.join(current))
                current = []
        if current:
            result.append(' '.join(current))

    return [s.strip() for s in result if len(s.strip()) > 3]


def is_question(sentence: str) -> bool:
    """
    Detect questions in Hindi/English transcripts.
    Checks punctuation, question words, and teaching phrases.
    Uses whole-word matching for single-word indicators to avoid false positives.
    """
    s = sentence.strip()
    if not s:
        return False
    if s.endswith('?'):
        return True

    s_lower = s.lower()
    words_in_sentence = set(s_lower.split())

    for indicator in QUESTION_INDICATORS:
        if ' ' in indicator:
            # Multi-word phrase — substring check
            if indicator in s_lower:
                return True
        else:
            # Single word — whole-word match only
            if indicator in words_in_sentence:
                return True
    return False


def is_student_response(sentence: str) -> bool:
    """
    Detect student responses using three rules:

    Rule 1: Entire sentence is made of acknowledgement words → Student
            e.g. "जी हाँ", "ok sir", "नहीं"

    Rule 2: Sentence is very short (≤3 words) → likely a one/two word answer
            Tightened from original ≤4 to reduce false positives on teacher phrases.

    Rule 3: Short sentence (≤6 words) that STARTS with an ack word → Student
            e.g. "हाँ दीदी समझ गया", "नहीं पता मुझे"
    """
    words = sentence.strip().split()
    if not words:
        return False

    # Rule 1: Pure acknowledgement sentence
    if all(w in STUDENT_ACK for w in words):
        return True

    # Rule 2: Very short sentence
    if len(words) <= 3:
        return True

    # Rule 3: Short sentence beginning with ack word
    if len(words) <= 6 and words[0] in STUDENT_ACK:
        return True

    return False