import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# === 1. Koneksi ke Google Sheets ===
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPE)
gc = gspread.authorize(creds)
SHEET_KEY = "1LzT6-aUyW19FygQxycEA820MSPNKXqKHe_7IWBG5FW0"

# === 2. Data MBTI ===
questions = {
    "E": [1,3,5,7,9,11], "I": [2,4,6,8,10,12],
    "S": [13,15,17,19,21,23], "N": [14,16,18,20,22,24],
    "T": [25,27,29,31,33,35], "F": [26,28,30,32,34,36],
    "J": [37,39,41,43,45,47], "P": [38,40,42,44,46,48]
}
text_questions = [f"Pernyataan {i}" for i in range(1, 49)]  # Pakai dummy singkat

desc_map = {
    "ISTJ": "Teliti dan logis.", "ISFJ": "Setia dan peduli.", "INFJ": "Visioner dan empatik.",
    "INTJ": "Strategis dan mandiri.", "ISTP": "Eksperimen praktis.", "ISFP": "Fleksibel dan kreatif.",
    "INFP": "Nilai dan empati.", "INTP": "Analitis dan logis.", "ESTP": "Spontan dan realistis.",
    "ESFP": "Ceria dan sosial.", "ENFP": "Ekspresif dan kreatif.", "ENTP": "Inovatif dan tajam.",
    "ESTJ": "Tegas dan efisien.", "ESFJ": "Ramah dan bertanggung jawab.", "ENFJ": "Karismatik dan inspiratif.",
    "ENTJ": "Ambisius dan strategis."
}

# === 3. UI Streamlit ===
st.set_page_config(page_title="MBTI Personality Test", page_icon="🧠", layout="wide")
st.title("🧩 Tes Kepribadian MBTI Mahasiswa")

# === 4. Handle Session Reset ===
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# === 5. Tampilkan Form jika belum submit ===
if not st.session_state.submitted:
    with st.form("form_mbti"):
        st.subheader("🧍 Identitas Responden")
        nama = st.text_input("Nama Lengkap")
        prodi = st.selectbox("Program Studi", ["", "Information Systems", "Computer Science", "Digital Business"])
        gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        semester = st.selectbox("Semester", ["", "1", "2", "3", "4", "5", "6", "7", "8"])

        st.subheader("📝 Pernyataan MBTI")
        answers = []
        for i, q in enumerate(text_questions, start=1):
            st.markdown(f"**{i}. {q}**")
            val = st.slider("", 1, 5, 3, key=f"Q{i}")
            answers.append(val)

        submit = st.form_submit_button("✅ Kirim Jawaban")

    if submit:
        if not nama or not prodi:
            st.error("⚠️ Harap isi nama dan program studi!")
        else:
            scores = {k: sum(answers[i-1] for i in v) for k, v in questions.items()}
            EI = "E" if scores["E"] > scores["I"] else "I"
            SN = "S" if scores["S"] > scores["N"] else "N"
            TF = "T" if scores["T"] > scores["F"] else "F"
            JP = "J" if scores["J"] > scores["P"] else "P"
            mbti = EI + SN + TF + JP
            deskripsi = desc_map.get(mbti, "Deskripsi tidak ditemukan.")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                worksheet = gc.open_by_key(SHEET_KEY).sheet1
                worksheet.append_row([timestamp, nama, prodi, gender, semester] + answers + [mbti, deskripsi])
                st.session_state.mbti = mbti
                st.session_state.nama = nama
                st.session_state.deskripsi = deskripsi
                st.session_state.submitted = True
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheet: {e}")

# === 6. Tampilkan Hasil ===
else:
    st.success(f"✅ Terima kasih, {st.session_state.nama}!")
    st.markdown(f"### 🧠 Hasil MBTI Anda: **{st.session_state.mbti}**")
    st.info(st.session_state.deskripsi)
    st.balloons()
