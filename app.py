import streamlit as st
import re
import random
from docx import Document
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# Sual parsing funksiyası
def parse_docx(file):
    doc = Document(file)
    sual_nusunesi = re.compile(r"^\s*\d+[\.\)]\s+")
    variant_nusunesi = re.compile(r"^\s*[A-Ea-e]\)\s+(.*)")

    paragraphlar = list(doc.paragraphs)
    i = 0
    sual_bloklari = []

    while i < len(paragraphlar):
        metn = paragraphlar[i].text.strip()
        if sual_nusunesi.match(metn):
            sual_metni = sual_nusunesi.sub('', metn)
            i += 1
            variantlar = []
            while i < len(paragraphlar):
                text = paragraphlar[i].text.strip()
                uygun = variant_nusunesi.match(text)
                if uygun:
                    variantlar.append(uygun.group(1).strip())
                    i += 1
                elif text and not sual_nusunesi.match(text) and len(variantlar) < 5:
                    variantlar.append(text)
                    i += 1
                else:
                    break
            if len(variantlar) == 5:
                sual_bloklari.append((sual_metni, variantlar))
        else:
            i += 1
    return sual_bloklari

# Avtomatik yenilənmə (timer üçün)
st_autorefresh(interval=1000, key="auto_refresh")

# Streamlit başlıq və giriş
st.set_page_config(page_title="İmtahan Rejimi", page_icon="📝")
st.title("📝 Öz İmtahanını Yoxla")

uploaded_file = st.file_uploader("📤 Word (.docx) faylını yüklə", type="docx")
mode = st.radio("📌 Rejim seç:", ["50 random sual", "Bütün suallar"], index=0)

if uploaded_file:
    if "initialized" not in st.session_state:
        suallar = parse_docx(uploaded_file)
        if mode == "50 random sual":
            suallar = random.sample(suallar, min(50, len(suallar)))

        st.session_state.suallar = suallar
        st.session_state.current = 0
        st.session_state.cavablar = [None] * len(suallar)
        st.session_state.duzgun = [s[1][0] for s in suallar]
        st.session_state.shuffled_variants = [random.sample(s[1], len(s[1])) for s in suallar]
        st.session_state.imtahan_basladi = False
        st.session_state.start_time = None
        st.session_state.initialized = True

    if not st.session_state.imtahan_basladi:
        if st.button("🚀 İmtahana Başla"):
            st.session_state.imtahan_basladi = True
            st.session_state.start_time = datetime.now()
    else:
        total_time = timedelta(hours=1)
        time_left = total_time - (datetime.now() - st.session_state.start_time)
        
        if time_left.total_seconds() <= 0:
            st.warning("⏰ Vaxt bitdi! İmtahan başa çatdı.")
            st.session_state.imtahan_basladi = False
            show_results = True
        else:
            st.markdown(f"⏳ **Qalan vaxt:** {str(time_left).split('.')[0]}")
            idx = st.session_state.current
            sual_metni, variantlar = st.session_state.suallar[idx]
            shuffled = st.session_state.shuffled_variants[idx]

            st.markdown(f"**{idx+1}) {sual_metni}**")
            secim = st.radio("Variantı seç:", shuffled, key=f"sual_{idx}", index=shuffled.index(st.session_state.cavablar[idx]) if st.session_state.cavablar[idx] else 0)

            st.session_state.cavablar[idx] = secim

            col1, col2, col3 = st.columns(3)

            if col1.button("⬅️ Geri qayıt", disabled=(idx == 0)):
                st.session_state.current = max(0, idx - 1)

            if col2.button("✅ İmtahanı Bitir"):
                st.session_state.imtahan_basladi = False

            if col3.button("➡️ Növbəti sual", disabled=(idx == len(st.session_state.suallar) - 1)):
                st.session_state.current = min(len(st.session_state.suallar) - 1, idx + 1)

if "imtahan_basladi" in st.session_state and not st.session_state.imtahan_basladi:
    suallar = st.session_state.suallar
    cavablar = st.session_state.cavablar
    duzgun = st.session_state.duzgun

    dogru_say = sum([1 for a, b in zip(cavablar, duzgun) if a == b])
    st.success(f"✅ İmtahan bitdi! Nəticə: {dogru_say}/{len(suallar)} doğru cavab")

    with st.expander("📋 Sual-sual nəticələrini göstər"):
        for i, (user_ans, correct_ans, q) in enumerate(zip(cavablar, duzgun, suallar)):
            sual_metni = q[0]
            status = "✅ Düzgün" if user_ans == correct_ans else "❌ Səhv"
            st.markdown(f"**{i+1}) {sual_metni}**\n\nSənin cavabın: `{user_ans}` — Doğru cavab: `{correct_ans}` → {status}")

    if st.button("🔁 Yenidən başla"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()