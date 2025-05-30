import streamlit as st
import random
import time

st.set_page_config(page_title="İmtahan Rejimi", page_icon="📝")

st.title("📝 İmtahan Rejimi")

if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "shuffled_options" not in st.session_state:
    st.session_state.shuffled_options = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "exam_finished" not in st.session_state:
    st.session_state.exam_finished = False

# Saatı göstər
elapsed = int(time.time() - st.session_state.start_time)
remaining = max(0, 3600 - elapsed)
mins, secs = divmod(remaining, 60)
st.sidebar.markdown(f"⏳ Qalan vaxt: **{mins:02d}:{secs:02d}**")

if remaining == 0:
    st.session_state.exam_finished = True

uploaded_file = st.file_uploader("Sualları yüklə (.txt formatında)", type=["txt"])

if uploaded_file and not st.session_state.questions:
    content = uploaded_file.read().decode("utf-8").split("\n")
    for i in range(0, len(content), 6):
        if i+5 < len(content):
            sual = content[i].strip()
            variantlar = [content[i+j].strip() for j in range(1, 5)]
            dogru = content[i+5].strip()
            st.session_state.questions.append({
                "sual": sual,
                "variantlar": variantlar,
                "dogru": dogru
            })

if st.session_state.questions and not st.session_state.exam_finished:
    idx = st.session_state.current_question
    sual_data = st.session_state.questions[idx]

    st.subheader(f"Sual {idx+1}: {sual_data['sual']}")

    if idx not in st.session_state.shuffled_options:
        shuffled = sual_data['variantlar'][:]
        random.shuffle(shuffled)
        st.session_state.shuffled_options[idx] = shuffled

    options = st.session_state.shuffled_options[idx]
    selected_option = st.session_state.answers.get(idx)
    selected = st.radio("Variantı seç:", options, index=options.index(selected_option) if selected_option in options else -1, key=f"q_{idx}")
    st.session_state.answers[idx] = selected

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ Əvvəlki sual", disabled=idx == 0):
            st.session_state.current_question -= 1
    with col2:
        if st.button("➡️ Növbəti sual", disabled=idx == len(st.session_state.questions) - 1):
            st.session_state.current_question += 1
    with col3:
        if st.button("✅ İmtahanı bitir"):
            st.session_state.exam_finished = True

elif st.session_state.exam_finished:
    st.success("✅ İmtahan bitdi!")
    dogru_say = 0
    for i, sual_data in enumerate(st.session_state.questions):
        if st.session_state.answers.get(i) == sual_data["dogru"]:
            dogru_say += 1
    st.write(f"📊 Doğru cavab sayı: **{dogru_say} / {len(st.session_state.questions)}**")
    st.write("🔁 Yenidən başlamaq üçün səhifəni yeniləyin.")