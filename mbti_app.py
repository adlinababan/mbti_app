import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# === 1. Setup koneksi Google Sheet ===
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPE)
gc = gspread.authorize(creds)

# Gunakan ID Google Sheet
SHEET_KEY = "1LzT6-aUyW19FygQxycEA820MSPNKXqKHe_7IWBG5FW0"
worksheet = gc.open_by_key(SHEET_KEY).sheet1

st.title("🧩 MBTI Personality Test Mahasiswa")

# === 2. Form Identitas ===
with st.form("identitas_form"):
    st.subheader("🪪 Data Diri Mahasiswa")
    nama = st.text_input("Nama Lengkap")
    prodi = st.selectbox("Program Studi", ["", "Informatika", "Sistem Informasi", "Teknologi Informasi", "Manajemen", "Akuntansi", "Bisnis Digital"])
    gender = st.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    semester = st.selectbox("Semester", ["", "1", "2", "3", "4", "5", "6", "7", "8"])
    submitted = st.form_submit_button("Lanjut ke Tes MBTI")

if submitted and nama and prodi:
    st.session_state["nama"] = nama
    st.session_state["prodi"] = prodi
    st.session_state["gender"] = gender
    st.session_state["semester"] = semester
    st.session_state["start_test"] = True
    st.success("✅ Data tersimpan, silakan lanjut mengisi pertanyaan MBTI!")

# === 3. Tes MBTI (48 pertanyaan Likert 1–5) ===
if st.session_state.get("start_test", False):

    st.subheader("🧠 Jawab Setiap Pertanyaan")
    st.info("Skala: 1 = Sangat Tidak Setuju ... 5 = Sangat Setuju")

    questions = {
        "E": [1,3,5,7,9,11], "I": [2,4,6,8,10,12],
        "S": [13,15,17,19,21,23], "N": [14,16,18,20,22,24],
        "T": [25,27,29,31,33,35], "F": [26,28,30,32,34,36],
        "J": [37,39,41,43,45,47], "P": [38,40,42,44,46,48]
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

    answers = []
    for i, q in enumerate(text_questions, start=1):
        ans = st.slider(f"{i}. {q}", 1, 5, 3)
        answers.append(ans)

    if st.button("✅ Kirim Jawaban"):
        # Hitung skor
        scores = {k: sum(answers[i-1] for i in v) for k, v in questions.items()}
        EI = "E" if scores["E"] > scores["I"] else "I"
        SN = "S" if scores["S"] > scores["N"] else "N"
        TF = "T" if scores["T"] > scores["F"] else "F"
        JP = "J" if scores["J"] > scores["P"] else "P"
        mbti = EI + SN + TF + JP

        desc_map = {
            "ISTJ": "Teliti, logis, dan bertanggung jawab.",
            "ISFJ": "Setia, sabar, dan penuh perhatian.",
            "INFJ": "Visioner, idealistik, dan empatik.",
            "INTJ": "Strategis, mandiri, dan rasional.",
            "ISTP": "Praktis, tangguh, dan logis.",
            "ISFP": "Fleksibel, lembut, dan kreatif.",
            "INFP": "Idealistik, empatik, dan penuh makna.",
            "INTP": "Logis, penasaran, dan analitis.",
            "ESTP": "Spontan, energik, dan realistis.",
            "ESFP": "Ceria, ekspresif, dan sosial.",
            "ENFP": "Antusias, imajinatif, dan inspiratif.",
            "ENTP": "Inovatif, suka debat, dan visioner.",
            "ESTJ": "Tegas, terorganisir, dan efisien.",
            "ESFJ": "Ramah, peduli, dan bertanggung jawab.",
            "ENFJ": "Karismatik, empatik, dan memotivasi.",
            "ENTJ": "Pemimpin alami, ambisius, dan rasional."
        }

        deskripsi = desc_map.get(mbti, "Deskripsi tidak ditemukan.")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ Tulis ke Google Sheet
        worksheet.append_row([
            timestamp,
            st.session_state["nama"],
            st.session_state["prodi"],
            st.session_state["gender"],
            st.session_state["semester"]
        ] + answers + [mbti, deskripsi])

        st.success(f"✅ Hasil MBTI Anda: **{mbti}**")
        st.info(deskripsi)
        st.balloons()
