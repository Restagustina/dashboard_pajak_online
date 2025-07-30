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
        backdrop-filter: blur(4px); /* Efek blur */
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
        margin-top: -5px;
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
    login_clicked = st.button("Login")

    daftar_html = """
        <form action="" method="post">
            <input type="submit" value="Daftar Akun Baru"
            style="
                background-color: #e53935;
                color: white;
                padding: 0.5em 1em;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                margin-top: 10px;
                cursor: pointer;
            "></form>
    """
    st.markdown(daftar_html, unsafe_allow_html=True)

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

    if st.query_params and not st.session_state.form_submitted:
        st.session_state.page = "register"
        st.session_state.form_submitted = True
        st.rerun()

# -------------------------------
# REGISTER PAGE
# -------------------------------
import streamlit as st
import base64

def register_page():
    st.set_page_config(layout="centered")

    # Load background image & encode to base64
    with open("assets/bg.jpg", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()

    # CSS style sama persis seperti login
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&display=swap');

    .custom-title {{
        font-size: 60px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        font-family: 'Anton', sans-serif;
        background: linear-gradient(to right, yellow, white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}

    .custom-subtitle {{
        text-align: center;
        font-size: 16px;
        color: white;
        margin-top: -10px;
        margin-bottom: 30px;
    }}

    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        backdrop-filter: blur(4px);
    }}

    .stTextInput > div > div > input {{
        background-color: rgba(33, 33, 33, 0.9);
        color: white;
    }}

    .stButton>button {{
        background-color: #dc3545;
        color: white;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        margin-top: 20px;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    # Judul
    st.markdown('<div class="custom-title">SIMANPA I</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-subtitle">Sistem Informasi Pembayaran Pajak Kendaraan Online</div>', unsafe_allow_html=True)

    # Form Registrasi
    nama = st.text_input("Masukkan Nama Lengkap")
    nik = st.text_input("Masukkan NIK")
    plat = st.text_input("Masukkan Plat Nomor")
    password = st.text_input("Masukkan Password", type="password")
    konfirmasi = st.text_input("Konfirmasi Password", type="password")

    if st.button("Daftar"):
        if password != konfirmasi:
            st.error("Password dan konfirmasi tidak sama.")
        elif nama and nik and plat:
            # Simpan data ke Excel (atau database)
            st.success("Pendaftaran berhasil! Silakan login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.warning("Semua kolom harus diisi.")

    # Tombol kembali
    if st.button("Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()

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
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'dashboard':
    dashboard_page()