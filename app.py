import streamlit as st
import re
import random
from docx import Document
import time

# Sualları yığmaq funksiyası
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

st.set_page_config(page_title="İmtahan Rejimi", page_icon="📝")
st.title("📝 Öz İmtahanını Yoxla")

uploaded_file = st.file_uploader("📤 Word (.docx) faylını yüklə", type="docx")
mode = st.radio("📌 Rejim seç:", ["50 random sual", "Bütün suallar"], index=0)

if uploaded_file:
    suallar = parse_docx(uploaded_file)
    if not suallar:
        st.error("Sual tapılmadı. Fayl formatını yoxla.")
    else:
        if mode == "50 random sual":
            suallar = random.sample(suallar, min(50, len(suallar)))

        if "imtahan_basladi" not in st.session_state:
            st.session_state.imtahan_basladi = False
            st.session_state.suallar = suallar
            st.session_state.current = 0
            st.session_state.cavablar = [None] * len(suallar)
            st.session_state.duzgun = [s[1][0] for s in suallar]
            st.session_state.shuffle_variants = [random.sample(s[1], len(s[1])) for s in suallar]
            st.session_state.start_time = time.time()
            st.session_state.exam_ended = False

        if not st.session_state.imtahan_basladi:
            if st.button("🚀 İmtahana Başla"):
                st.session_state.imtahan_basladi = True
                st.experimental_rerun()
        else:
            if not st.session_state.exam_ended:
                idx = st.session_state.current
                if time.time() - st.session_state.start_time > 3600:
                    st.warning("⏰ Vaxt bitdi. İmtahan başa çatdı.")
                    st.session_state.exam_ended = True
                    st.experimental_rerun()
                else:
                    vaxt_qaldi = 3600 - int(time.time() - st.session_state.start_time)
                    deqiqe, saniye = divmod(vaxt_qaldi, 60)
                    st.markdown(f"⏳ Qalan vaxt: **{deqiqe:02}:{saniye:02}**")

                    sual_metni, _ = st.session_state.suallar[idx]
                    variantlar = st.session_state.shuffle_variants[idx]

                    st.markdown(f"**{idx+1}) {sual_metni}**")
                    secim = st.radio("Variantı seç:", variantlar, index=variantlar.index(st.session_state.cavablar[idx]) if st.session_state.cavablar[idx] else 0, key=idx)
                    st.session_state.cavablar[idx] = secim

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("⬅️ Əvvəlki sual", disabled=idx == 0):
                            st.session_state.current -= 1
                            st.experimental_rerun()
                    with col2:
                        if st.button("✅ İmtahanı Bitir"):
                            st.session_state.exam_ended = True
                            st.experimental_rerun()
                    with col3:
                        if st.button("➡️ Növbəti sual", disabled=idx == len(st.session_state.suallar) - 1):
                            st.session_state.current += 1
                            st.experimental_rerun()
            else:
                dogru_say = sum([1 for a, b in zip(st.session_state.cavablar, st.session_state.duzgun) if a == b])
                st.success("✅ İmtahan bitdi!")
                st.markdown(f"### Nəticə: {dogru_say}/{len(st.session_state.suallar)} doğru cavab ✅")

                with st.expander("📋 Sual-sual nəticələrini göstər"):
                    for i, (user_ans, correct_ans, q) in enumerate(zip(
                        st.session_state.cavablar,
                        st.session_state.duzgun,
                        st.session_state.suallar
                    )):
                        sual_metni = q[0]
                        status = "✅ Düzgün" if user_ans == correct_ans else "❌ Səhv"
                        st.markdown(f"**{i+1}) {sual_metni}**\n\nSənin cavabın: `{user_ans}` — Doğru cavab: `{correct_ans}` → {status}")

                if st.button("🔁 Yenidən başla"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.experimental_rerun()
