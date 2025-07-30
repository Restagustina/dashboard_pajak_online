import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from utils import load_data, save_data

# -------------------------------
# SET BACKGROUND
# -------------------------------
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        backdrop-filter: blur(7px); /* Efek blur */
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------------------
# KONFIGURASI AWAL
# -------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_PATH, "assets", "bg.jpg")
set_background(image_path)  # SET BACKGROUND di awal

# -------------------------------
# LOAD DATA
# -------------------------------
df_user, df_kendaraan, df_riwayat = load_data()
data_user = pd.read_excel("DASHBOARD_main/data_user.xlsx")

# -------------------------------
# SESSION STATE
# -------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&display=swap');

    .custom-title {
        font-size: 60px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        font-family: 'Anton', sans-serif;
        background: linear-gradient(to top left, yellow, white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .custom-subtitle {
        text-align: center;
        font-size: 18px;
        color: white;
        margin-top: 0px;
        margin-bottom: 30px; /* tambahkan jarak bawah sub title to input nik
        font-family: 'Arial', sans-serif;
        letter-spacing: 1px;
    }
    </style>

    <div class="custom-title">
        SIMANPA I
    </div>
    <div class="custom-subtitle">
        Sistem Informasi Pembayaran Pajak Kendaraan Palembang 1
    </div>
    """, unsafe_allow_html=True)

    input_nik = st.text_input("Masukkan NIK").strip()
    input_plat = st.text_input("Masukkan Plat").strip().upper()

    # Tombol Login biasa (biarkan default)
    login_clicked = st.button("Login", key="login_button")

    # HTML Tombol Custom untuk "Daftar Akun Baru"
    st.markdown("""
        <style>
        .custom-button {
            background-color: #d32f2f;
            color: white;
            padding: 0.5em 1em;
            font-size: 16px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }

        .custom-button:hover {
            background-color: #b71c1c;
            cursor: pointer;
        }

        .custom-button:active {
            background-color: #a30000;
            transform: scale(0.97);
        }
        </style>

        <form action="?daftar=true">
            <button class="custom-button" type="submit">Daftar Akun Baru</button>
        </form>
    """, unsafe_allow_html=True)

    if st.query_params.get("daftar") == "true":
        st.session_state.page = "register"
        st.rerun()

    # Login logic
    if login_clicked:
        user_match = data_user[data_user['NIK'] == input_nik]
        kendaraan_match = df_kendaraan[df_kendaraan['Plat'].str.upper() == input_plat]

        if not user_match.empty and not kendaraan_match.empty:
            st.session_state.user_data = {
                'NIK': input_nik,
                'Plat': input_plat,
                'Nama': user_match.iloc[0].get('Nama', ''),
                'Pajak': kendaraan_match.iloc[0].get('Pajak', '')
            }
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.error("❌ Data tidak ditemukan. Periksa kembali NIK dan Plat.")

    if st.query_params.get("daftar") == "true":
        st.session_state.page = "register"
        st.rerun()

# -------------------------------
# REGISTER PAGE
# -------------------------------
def register_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    .judul {
        font-family: 'Poppins', sans-serif;
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(to top left, yellow, white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    </style>

    <div class='judul'>Daftar Akun Baru</div>
""", unsafe_allow_html=True)

    with st.form("register_form"):
        nik = st.text_input("Masukkan NIK").strip()
        nama = st.text_input("Masukkan Nama Lengkap").strip()
        plat = st.text_input("Masukkan Plat Kendaraan").strip().upper()
        pajak = st.text_input("Masukkan Jumlah Pajak (Rp)").strip()

        submit = st.form_submit_button("Daftar")

    if submit:
        if nik and nama and plat and pajak:
            # Simpan ke Excel lewat utils.py
            new_user = pd.DataFrame([{"NIK": nik, "Nama": nama}])
            new_kendaraan = pd.DataFrame([{"NIK": nik, "Plat": plat, "Pajak": pajak}])

            save_data(new_user, new_kendaraan)
            st.success("✅ Akun berhasil didaftarkan. Silakan login.")
            st.session_state.page = "login"
            st.session_state.form_submitted = False
            st.rerun()
        else:
            st.error("❌ Harap lengkapi semua data.")

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
def dashboard_page():
    if not st.session_state.user_data:
        st.error("Anda belum login.")
        return

    user = st.session_state.user_data
    nama, nik, plat = user.get('Nama', ''), user.get('NIK', ''), user.get('Plat', '')

    st.write(f"Selamat datang, {nama}")
    st.title("📋 Menu")

    menu = st.sidebar.radio("Navigasi", ["Profil", "Info Pajak", "Bayar Pajak", "Riwayat Pembayaran", "Logout"])

    if menu == "Profil":
        st.subheader("👤 Profil Wajib Pajak")
        st.write(f"**NIK:** {nik}")
        st.write(f"**Nama:** {nama}")
        st.write(f"**Plat Nomor:** {plat}")

    elif menu == "Info Pajak":
        st.subheader("ℹ️ Info Pajak")
        st.write("Halaman ini akan menampilkan informasi pajak (nanti bisa diisi data PKB/SWDKLLJ dsb).")

    elif menu == "Bayar Pajak":
        st.subheader("💸 Simulasi Pembayaran Pajak")
        metode = st.selectbox("Pilih Metode Pembayaran", ["BRI", "Mandiri", "DANA", "OVO", "GoPay"])
        if st.button("Bayar Sekarang"):
            st.success(f"Pembayaran via {metode} berhasil (simulasi).")

    elif menu == "Riwayat Pembayaran":
        st.subheader("🧾 Riwayat Pembayaran")
        st.write("Belum ada riwayat pembayaran (simulasi data).")

    elif menu == "Logout":
        st.session_state.user_data = {}
        st.session_state.page = 'login'
        st.success("Logout berhasil.")
        st.rerun()

# -------------------------------
# ROUTING HALAMAN
# -------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "dashboard":
    dashboard_page()  
