# ===================================================
# 🌐 MBTI Personality Test Web App (Streamlit + GSheet)
# ===================================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
from google.auth.exceptions import RefreshError
from gspread.exceptions import APIError


# === 1. Koneksi ke Google Sheets ===
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],  # TANPA dict()
    scopes=SCOPE
)

gc = gspread.authorize(creds)

# === 2. Buka Spreadsheet menggunakan KEY ===
SHEET_KEY = "1LzT6-aUyW19FygQxycEA820MSPNKXqKHe_7IWBG5FW0"

# try:
#     worksheet = gc.open_by_key("1LzT6-aUyW19FygQxycEA820MSPNKXqKHe_7IWBG5FW0").sheet1
#     st.success("✅ Terhubung ke Google Sheet dengan sukses!")
# except Exception as e:
#     st.error(f"❌ Gagal terhubung: {e}")

# === 2. Pertanyaan MBTI ===
questions = {
    "E": [1,3,5,7,9,11],
    "I": [2,4,6,8,10,12],
    "S": [13,15,17,19,21,23],
    "N": [14,16,18,20,22,24],
    "T": [25,27,29,31,33,35],
    "F": [26,28,30,32,34,36],
    "J": [37,39,41,43,45,47],
    "P": [38,40,42,44,46,48]
}

text_questions = [
    "Saya merasa berenergi setelah berbicara dengan banyak orang.",
    "Saya lebih nyaman bekerja sendirian daripada dalam kelompok besar.",
    "Saya senang berbagi ide secara spontan di kelas.",
    "Saya lebih suka mendengarkan dulu sebelum berbicara.",
    "Saya menikmati suasana ramai dan aktif di kampus.",
    "Saya cenderung menyimpan pikiran saya sendiri.",
    "Saya senang memimpin diskusi atau kegiatan kelompok.",
    "Saya butuh waktu sendiri setelah berinteraksi dengan banyak orang.",
    "Saya sering memulai percakapan dengan orang baru.",
    "Saya lebih fokus saat bekerja di tempat yang tenang.",
    "Saya merasa nyaman tampil di depan umum.",
    "Saya sering merasa lelah setelah kegiatan sosial yang padat.",
    "Saya lebih percaya pada pengalaman nyata daripada teori.",
    "Saya tertarik pada ide dan konsep baru yang belum terbukti.",
    "Saya memperhatikan detail dalam setiap tugas.",
    "Saya lebih suka berpikir tentang kemungkinan masa depan daripada fakta sekarang.",
    "Saya lebih memahami materi melalui contoh konkret.",
    "Saya sering membayangkan berbagai skenario alternatif.",
    "Saya lebih suka instruksi yang jelas dan langkah demi langkah.",
    "Saya mudah menangkap pola atau makna tersembunyi.",
    "Saya lebih nyaman dengan hal-hal yang praktis.",
    "Saya sering punya intuisi tentang sesuatu sebelum ada buktinya.",
    "Saya lebih suka tugas dengan hasil nyata daripada konsep abstrak.",
    "Saya menikmati berpikir kreatif dan spekulatif.",
    "Saya membuat keputusan berdasarkan logika dan analisis.",
    "Saya mempertimbangkan dampak emosional terhadap orang lain.",
    "Saya lebih menghargai keadilan dibanding belas kasihan.",
    "Saya mudah memahami perasaan orang lain.",
    "Saya menilai sesuatu berdasarkan kebenaran objektif.",
    "Saya menghindari membuat orang lain tersinggung.",
    "Saya lebih percaya pada data dan fakta.",
    "Saya sering menyesuaikan keputusan demi menjaga hubungan baik.",
    "Saya merasa nyaman memberi kritik langsung.",
    "Saya merasa tidak enak jika keputusan saya membuat orang lain kecewa.",
    "Saya lebih fokus pada efisiensi daripada keharmonisan tim.",
    "Saya berusaha memahami alasan emosional di balik tindakan seseorang.",
    "Saya suka membuat rencana dan jadwal sebelum bekerja.",
    "Saya lebih suka mengikuti alur situasi daripada perencanaan ketat.",
    "Saya merasa puas ketika semua tugas selesai jauh sebelum tenggat waktu.",
    "Saya sering menunda pekerjaan hingga mendekati batas waktu.",
    "Saya suka menandai to-do list dan menepati target.",
    "Saya fleksibel terhadap perubahan mendadak.",
    "Saya lebih suka struktur yang jelas dan aturan yang pasti.",
    "Saya menikmati spontanitas dan ide baru di tengah proses kerja.",
    "Saya lebih tenang jika segalanya sudah direncanakan.",
    "Saya sering menemukan ide baru di menit-menit terakhir.",
    "Saya berorientasi pada hasil dan penyelesaian tugas.",
    "Saya sering bekerja sesuai mood atau inspirasi."
]

# === 3. Deskripsi MBTI ===
desc_map = {
    "ISTJ": "The Inspector – Teliti, logis, bertanggung jawab, dan berorientasi pada fakta. Menyukai struktur dan keteraturan.",
    "ISFJ": "The Defender – Setia, penuh perhatian, dan sabar. Suka membantu dan melindungi orang lain dengan cara yang praktis.",
    "INFJ": "The Advocate – Idealistik, visioner, dan berempati.",
    "INTJ": "The Architect – Strategis, analitis, dan mandiri. Punya visi besar.",
    "ISTP": "The Virtuoso – Logis, tangguh, dan suka bereksperimen secara praktis.",
    "ISFP": "The Adventurer – Lembut, fleksibel, dan kreatif.",
    "INFP": "The Mediator – Idealistik, empatik, dan berorientasi nilai.",
    "INTP": "The Thinker – Analitis, penasaran, dan logis.",
    "ESTP": "The Dynamo – Energik, spontan, dan realistis.",
    "ESFP": "The Performer – Ceria, sosial, dan penuh semangat.",
    "ENFP": "The Campaigner – Antusias, kreatif, dan ekspresif.",
    "ENTP": "The Debater – Inovatif, argumentatif, dan tajam.",
    "ESTJ": "The Executive – Terorganisir, tegas, dan efisien.",
    "ESFJ": "The Consul – Ramah, peduli, dan bertanggung jawab.",
    "ENFJ": "The Protagonist – Karismatik, empatik, dan inspiratif.",
    "ENTJ": "The Commander – Tegas, berwawasan luas, dan ambisius."
}

# === 4. UI Streamlit ===
st.set_page_config(page_title="MBTI Personality Test", page_icon="🧠", layout="wide")

st.title("🧩 Tes Kepribadian MBTI Mahasiswa")
st.markdown("Isi form berikut untuk mengetahui tipe kepribadian MBTI Anda berdasarkan 48 pertanyaan.")

# === 5. Form Identitas ===
with st.form("form_mbti"):
    st.subheader("🧍 Identitas Responden")
    nama = st.text_input("Nama Lengkap")
    prodi = st.selectbox("Program Studi", ["", "Information Systems", "Computer Science", "Digital Business", "International Trade", "Design Communication Visual"])
    gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    semester = st.selectbox("Semester", ["", "1", "2", "3", "4", "5", "6", "7", "8"])

    st.subheader("📝 Pernyataan MBTI")
    answers = []
    for i, q in enumerate(text_questions, start=1):
        st.markdown(f"**{i}. {q}**")
        val = st.slider("", 1, 5, 3, key=f"Q{i}")
        answers.append(val)
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    
  submit = st.form_submit_button("✅ Kirim Jawaban")

 if submit:
    if not nama or not prodi:
        st.error("⚠️ Harap isi nama dan program studi!")
    else:
        # Hitung dan simpan hasil
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
            st.session_state.submitted = True  # set flag sukses
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheet: {e}")

        # === Tampilkan hasil ===
         if st.session_state.submitted:
        st.success("✅ Terima kasih telah mengisi tes!")
        st.markdown(f"### 🧠 Hasil MBTI Anda: **{mbti}**")
        st.info(deskripsi)
        st.balloons()







