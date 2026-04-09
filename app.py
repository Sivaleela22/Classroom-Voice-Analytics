import streamlit as st
import os
from transcribe import transcribe_audio
from analysis import analyze_classroom

st.set_page_config(page_title="Classroom Voice Analytics", layout="wide")

st.title("🎓 Classroom Voice Analytics MVP")
st.caption("MakerGhat AI/ML Internship – Pre-Work | Upload classroom audio to get insights")
st.divider()

uploaded_file = st.file_uploader(
    "Upload Classroom Audio",
    type=["wav", "mp3", "m4a", "ogg"],
    help="Supports WAV, MP3, M4A, OGG"
)

if uploaded_file is not None:
    ext = os.path.splitext(uploaded_file.name)[1]
    file_path = f"temp_audio{ext}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if os.path.getsize(file_path) == 0:
        st.error("❌ Uploaded file is empty.")
    else:
        st.audio(file_path)

        # ── Get audio duration ────────────────────────────────────────────────
        audio_duration = None
        try:
            from mutagen import File as MutagenFile
            af = MutagenFile(file_path)
            if af is not None:
                audio_duration = af.info.length
        except Exception:
            pass  # duration is optional; estimates still work without it

        # Show audio duration if detected
        if audio_duration:
            total_m, total_s = divmod(int(audio_duration), 60)
            st.caption(f"🎵 Audio duration detected: **{total_m}m {total_s:02d}s**")

        # ── Task 1: Transcription ─────────────────────────────────────────────
        st.subheader("📝 Task 1 — Transcript")
        with st.spinner("Transcribing audio..."):
            transcript = transcribe_audio(file_path)

        if transcript.startswith("ERROR"):
            st.error(f"Transcription failed: {transcript}")
            st.stop()

        st.success("✅ Transcription complete!")
        with st.expander("View Full Transcript", expanded=True):
            st.write(transcript)

        # ── Task 2: Classroom Analysis ────────────────────────────────────────
        st.subheader("📊 Task 2 — Basic Classroom Analysis")

        results = analyze_classroom(transcript, audio_duration_sec=audio_duration)

        # --- Teacher vs Student speech ---
        st.markdown("#### 🗣️ Teacher vs Student Speech")
        col1, col2 = st.columns(2)
        col1.metric("🧑‍🏫 Teacher Sentences", f"{results['teacher_ratio']:.0%}",
                    f"{results['teacher_words']} words")
        col2.metric("🙋 Student Sentences", f"{results['student_participation']:.0%}",
                    f"{results['student_words']} words")

        # Talk time bar
        t_pct = results["teacher_ratio"] * 100
        s_pct = results["student_participation"] * 100
        st.markdown(
            f"""<div style="height:18px; border-radius:9px; overflow:hidden; display:flex; margin:8px 0 4px;">
              <div style="width:{t_pct:.0f}%; background:#1a56db;"></div>
              <div style="width:{s_pct:.0f}%; background:#057a55;"></div>
            </div>
            <div style="display:flex; gap:20px; font-size:13px;">
              <span style="color:#1a56db;">■ Teacher {t_pct:.0f}%</span>
              <span style="color:#057a55;">■ Student {s_pct:.0f}%</span>
            </div>""",
            unsafe_allow_html=True
        )

        # --- Talk time ---
        st.markdown("#### ⏱️ Talk Time Estimate")
        st.caption(
            "Speech time split proportionally by word count. "
            "Silence fixed at 15% of audio. "
            "Teacher time + Student time + Silence = Total audio duration."
        )
        col3, col4, col5 = st.columns(3)
        col3.metric("🧑‍🏫 Teacher Talk Time", results["teacher_time_fmt"])
        col4.metric("🙋 Student Talk Time",   results["student_time_fmt"])
        col5.metric("🔇 Silence / Pause",     results["silence_fmt"])

        # Show that the three values add up to total duration
        if audio_duration:
            total_accounted = (
                results["teacher_time_sec"] +
                results["student_time_sec"] +
                results["silence_duration_sec"]
            )
            total_m, total_s = divmod(int(audio_duration), 60)
            acc_m,   acc_s   = divmod(total_accounted, 60)
            st.caption(
                f"✅ Total accounted: {acc_m}m {acc_s:02d}s "
                f"(audio length: {total_m}m {total_s:02d}s)"
            )

        # --- Questions & Responses ---
        st.markdown("#### ❓ Questions & Responses")
        col6, col7 = st.columns(2)
        col6.metric("Questions Asked",   results["questions"],
                    help="Detected using Hindi/English question keywords + phrases")
        col7.metric("Student Responses", results["responses"],
                    help="Short sentences / acknowledgement words")

        # --- Sentence breakdown ---
        st.markdown("#### 📋 Sentence-by-Sentence Breakdown")
        labeled = results["labeled_sentences"]
        for speaker, sentence in labeled:
            icon  = "🧑‍🏫" if speaker == "Teacher" else "🙋"
            color = "#1a56db" if speaker == "Teacher" else "#057a55"
            st.markdown(
                f'<div style="padding:6px 10px; margin:3px 0; border-left:3px solid {color}; font-size:14px;">'
                f'<b style="color:{color}">{icon} {speaker}</b>: {sentence}</div>',
                unsafe_allow_html=True
            )

        # ── Task 3: Engagement Metrics ────────────────────────────────────────
        st.subheader("📈 Task 3 — Engagement Metrics")

        with st.expander("📐 Metric Formulas & Explanations", expanded=True):
            st.markdown("""
| Metric | Formula | Meaning |
|--------|---------|---------|
| **Teacher Dominance Ratio (TDR)** | `teacher_sentences / total_sentences` | How teacher-led the session is (0–1) |
| **Student Participation Indicator (SPI)** | `student_sentences / total_sentences` | How much students contributed (0–1) |
| **Interaction Count (IC)** | `questions_asked + student_responses` | Total back-and-forth exchanges |
| **Engagement Score (ES)** | `min(1.0, (IC / total_sentences) × 2)` | Overall session liveliness (0–1) |
""")

        col8, col9, col10, col11 = st.columns(4)
        col8.metric("TDR",               f"{results['teacher_ratio']:.2f}")
        col9.metric("SPI",               f"{results['student_participation']:.2f}")
        col10.metric("IC",               results["interaction_count"])
        col11.metric("Engagement Score", f"{results['engagement_score']:.2f}")

        # ── Task 4: Classroom Summary ─────────────────────────────────────────
        st.subheader("📋 Task 4 — Classroom Summary")

        tdr   = results["teacher_ratio"]
        spi   = results["student_participation"]
        ic    = results["interaction_count"]
        es    = results["engagement_score"]
        total = results["total_sentences"]

        if tdr >= 0.75:
            style  = "**teacher-dominated**"
            advice = "Consider asking more open-ended questions to encourage student participation."
        elif spi >= 0.40:
            style  = "**highly interactive**"
            advice = "Great balance of teacher instruction and student engagement!"
        else:
            style  = "**moderately interactive**"
            advice = "Some student participation detected. More prompting could help."

        eng_label = (
            "🟢 High" if es >= 0.6 else
            "🟡 Moderate" if es >= 0.3 else
            "🔴 Low"
        ) + " engagement"

        st.markdown(f"""
> This classroom session is {style}.
> The teacher spoke in approximately **{tdr:.0%}** of segments (talk time: **{results['teacher_time_fmt']}**),
> while students contributed **{spi:.0%}** (talk time: **{results['student_time_fmt']}**).
> Estimated silence/pause duration: **{results['silence_fmt']}**.
>
> A total of **{results['questions']} questions** were detected, with **{results['responses']} student responses**,
> giving an **Interaction Count of {ic}** across **{total} total sentences**.
>
> **Engagement level:** {eng_label} (score: {es:.2f})
>
> 💡 *{advice}*
""")

    if os.path.exists(file_path):
        os.remove(file_path)