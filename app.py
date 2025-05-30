import streamlit as st
import re
import random
from docx import Document
from datetime import datetime, timedelta

# Word-dan sualları oxuyan funksiya
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

# Streamlit interfeys
st.set_page_config(page_title="İmtahan Rejimi", page_icon="📝")
st.title("📝 Öz İmtahanını Yoxla")

uploaded_file = st.file_uploader("📤 Word (.docx) faylını yüklə", type="docx")
mode = st.radio("📌 Rejim seç:", ["50 random sual", "Bütün suallar"], index=0)

if uploaded_file:
    suallar = parse_docx(uploaded_file)
    if not suallar:
        st.error("❌ Sual tapılmadı. Fayl formatını yoxla.")
    else:
        if mode == "50 random sual":
            suallar = random.sample(suallar, min(50, len(suallar)))

        if "imtahan_basladi" not in st.session_state:
            st.session_state.imtahan_basladi = False
            st.session_state.suallar = suallar
            st.session_state.current = 0
            st.session_state.cavablar = []
            st.session_state.duzgun = []
            st.session_state.shuffled_variantlar = {}
            st.session_state.start_time = None

        if not st.session_state.imtahan_basladi:
            if st.button("🚀 İmtahana Başla"):
                st.session_state.imtahan_basladi = True
                st.session_state.start_time = datetime.now()
                st.experimental_rerun()
        else:
            vaxt_bitdi = False
            now = datetime.now()
            start = st.session_state.start_time
            delta = now - start

            qalan = timedelta(hours=1) - delta
            if qalan.total_seconds() <= 0:
                vaxt_bitdi = True
                st.session_state.current = len(st.session_state.suallar)

            if not vaxt_bitdi:
                # Qalan vaxtı göstər
                qalan_dk = int(qalan.total_seconds() // 60)
                qalan_san = int(qalan.total_seconds() % 60)
                st.info(f"⏰ Qalan vaxt: **{qalan_dk} dəq {qalan_san} san**")

            idx = st.session_state.current
            if idx < len(st.session_state.suallar):
                sual_metni, variantlar = st.session_state.suallar[idx]
                dogru_cavab = variantlar[0]

                if idx not in st.session_state.shuffled_variantlar:
                    shuffled = variantlar[:]
                    random.shuffle(shuffled)
                    st.session_state.shuffled_variantlar[idx] = shuffled
                else:
                    shuffled = st.session_state.shuffled_variantlar[idx]

                st.markdown(f"**{idx+1}) {sual_metni}**")
                secim = st.radio("Variantı seç:", shuffled, key=idx)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➡️ Növbəti sual"):
                        st.session_state.cavablar.append(secim)
                        st.session_state.duzgun.append(dogru_cavab)
                        st.session_state.current += 1
                        st.experimental_rerun()
                with col2:
                    if st.button("🛑 İmtahanı Bitir"):
                        st.session_state.current = len(st.session_state.suallar)
                        st.experimental_rerun()
            else:
                st.success("✅ İmtahan bitdi!")
                dogru_say = sum([1 for a, b in zip(st.session_state.cavablar, st.session_state.duzgun) if a == b])
                st.markdown(f"### Nəticə: {dogru_say}/{len(st.session_state.cavablar)} doğru cavab ✅")

                with st.expander("📋 Sual-sual nəticələrini göstər"):
                    for i, (user_ans, correct_ans, q) in enumerate(zip(
                        st.session_state.cavablar,
                        st.session_state.duzgun,
                        st.session_state.suallar[:len(st.session_state.cavablar)]
                    )):
                        sual_metni = q[0]
                        status = "✅ Düzgün" if user_ans == correct_ans else "❌ Səhv"
                        st.markdown(f"**{i+1}) {sual_metni}**\n\nSənin cavabın: `{user_ans}` — Doğru cavab: `{correct_ans}` → {status}")

                if st.button("🔁 Yenidən başla"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.experimental_rerun()