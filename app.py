import streamlit as st import docx import random from io import BytesIO

st.set_page_config(page_title="Test Generator", layout="wide") st.title("📘 Test Generator")

menu = ["📤 Variantları Qarışdır", "📝 İmtahan Hazırla"] choice = st.sidebar.radio("Seçim edin", menu)

def parse_docx(file): doc = docx.Document(file) questions = [] for para in doc.paragraphs: if para.text.strip().startswith("Sual") and any(opt in para.text for opt in ["A)", "B)", "C)", "D)"]): questions.append(para.text.strip()) return questions

def shuffle_variants(question): parts = question.split("A)") if len(parts) < 2: return question, "" q_text = parts[0].strip() variants_part = "A)" + parts[1] variants = variants_part.split("\n") if "\n" in variants_part else [v.strip() for v in variants_part.split(" ") if ")" in v]

if len(variants) < 4:
    return question, ""

correct = variants[0]
random.shuffle(variants)

new_q = q_text + "\n" + "\n".join(variants)
new_answer = "ABCD"[variants.index(correct)]
return new_q, new_answer

def create_shuffled_docx_and_answers(questions): new_doc = docx.Document() answers = [] for i, q in enumerate(questions, 1): shuffled_q, answer = shuffle_variants(q) new_doc.add_paragraph(f"{i}. {shuffled_q}") answers.append(f"{i}. {answer}") return new_doc, answers

if choice == "📤 Variantları Qarışdır": st.header("📤 Variantları Qarışdır") uploaded_file = st.file_uploader(".docx faylını yükləyin", type=["docx"]) mode = st.radio("Seçim növü", ["50 sual", "Bütün suallar"])

if uploaded_file:
    suallar = parse_docx(uploaded_file)
    if len(suallar) < 5:
        st.error("Faylda kifayət qədər uyğun sual tapılmadı.")
    else:
        if mode == "50 sual":
            secilmis = random.sample(suallar, min(50, len(suallar)))
        else:
            st.info(f"Faylda {len(suallar)} sual tapıldı.")
            col1, col2 = st.columns(2)
            with col1:
                start_q = st.number_input("Başlanğıc sual №", min_value=1, max_value=len(suallar), value=1)
            with col2:
                end_q = st.number_input("Sonuncu sual №", min_value=start_q, max_value=len(suallar), value=len(suallar))
            secilmis = suallar[start_q - 1:end_q]

        yeni_doc, cavablar = create_shuffled_docx_and_answers(secilmis)

        output_docx = BytesIO()
        yeni_doc.save(output_docx)
        output_docx.seek(0)

        output_answers = BytesIO()
        output_answers.write('\n'.join(cavablar).encode('utf-8'))
        output_answers.seek(0)

        st.success("✅ Sənədlər hazırdır!")
        st.download_button("📥 Qarışdırılmış suallar (.docx)", output_docx, "qarisdirilmis_suallar.docx")
        st.download_button("📥 Cavab açarı (.txt)", output_answers, "cavablar.txt")

elif choice == "📝 İmtahan Hazırla": st.header("📝 İmtahan Hazırla") uploaded_file = st.file_uploader(".docx faylını yükləyin", type=["docx"], key="exam") if uploaded_file: suallar = parse_docx(uploaded_file) if len(suallar) < 5: st.error("Faylda kifayət qədər uyğun sual tapılmadı.") else: st.info(f"Faylda {len(suallar)} sual tapıldı.") col1, col2 = st.columns(2) with col1: start_q = st.number_input("Başlanğıc sual №", min_value=1, max_value=len(suallar), value=1, key="start_exam") with col2: end_q = st.number_input("Sonuncu sual №", min_value=start_q, max_value=len(suallar), value=len(suallar), key="end_exam")

secilmis = suallar[start_q - 1:end_q]

        yeni_doc, cavablar = create_shuffled_docx_and_answers(secilmis)

        output_docx = BytesIO()
        yeni_doc.save(output_docx)
        output_docx.seek(0)

        output_answers = BytesIO()
        output_answers.write('\n'.join(cavablar).encode('utf-8'))
        output_answers.seek(0)

        st.success("✅ İmtahan sənədləri hazırdır!")
        st.download_button("📥 İmtahan sualları (.docx)", output_docx, "imtahan_suallari.docx")
        st.download_button("📥 Cavab açarı (.txt)", output_answers, "imtahan_cavablari.txt")