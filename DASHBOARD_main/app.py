import pandas as pd
from datetime import datetime
import os
import streamlit as st
from utils import load_data, save_data 

import base64  # karena pakai base64 di fungsi `set_background`

# --- path gambar ---
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_PATH, "assets", "samsatplg1.jpg")

# --- Fungsi background dengan transparansi ---
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main > div {{
            background-color: rgba(255, 255, 255, 0.20);  /* transparansi konten */
            padding: 2rem;
            border-radius: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Jalankan fungsi background ---
set_background(image_path)

# -------------------------------
# LOAD DATA
# -------------------------------
df_user, df_kendaraan, df_riwayat = load_data()

# -------------------------------
# SESSION STATE
# -------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# -------------------------------
# HALAMAN LOGIN
# -------------------------------
def login_page():
    st.markdown("<h3 style='color:blue'> SAMSAT PALEMBANG 1</h3>", unsafe_allow_html=True)

    nik = st.text_input("Masukkan NIK")
    plat = st.text_input("Masukkan Plat Nomor")

    # Tombol login (pakai st.button biasa)
    login_clicked = st.button("Login")

    # Tombol daftar (pakai HTML + st.markdown untuk warna merah)
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
            ">
        </form>
    """
    daftar_clicked = st.markdown(daftar_html, unsafe_allow_html=True)

    # Proses login
    if login_clicked:
        user_match = df_user[df_user['NIK'] == nik]
        kendaraan_match = df_kendaraan[df_kendaraan['Plat'] == plat]

        if not user_match.empty and not kendaraan_match.empty:
            st.session_state.user_data = {
                'NIK': nik,
                'Plat': plat,
                'Nama': user_match.iloc[0]['Nama'],
                'Pajak': kendaraan_match.iloc[0]['Pajak']
            }
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.error("❌ Data tidak ditemukan. Periksa kembali NIK dan Plat.")

    # Tangkap klik tombol HTML dengan deteksi submit manual
    if st.session_state.get("page") != "register" and st.session_state.get("form_submitted", False) is False:
        if st.query_params:  # Deteksi URL berubah karena klik submit
            st.session_state.page = "register"
            st.session_state.form_submitted = True
            st.rerun()

# -------------------------------
# HALAMAN REGISTER (opsional)
# -------------------------------
def register_page():
    st.markdown("<h3 style='color:red'> Belum Punya Akun? Daftar </h3>", unsafe_allow_html=True)

    nik = st.text_input("Masukkan NIK")
    nama = st.text_input("Masukkan Nama")
    plat = st.text_input("Masukkan Plat Nomor")
    pajak = st.number_input("Masukkan Jumlah Pajak", min_value=0)

    if st.button("Daftar"):
        if nik and nama and plat:
            new_user = pd.DataFrame([{
                'NIK': nik,
                'Nama': nama
            }])
            new_kendaraan = pd.DataFrame([{
                'Plat': plat,
                'NIK': nik,
                'Pajak': pajak
            }])

            # Simpan ke file
            save_data(new_user, new_kendaraan)

            st.success("Pendaftaran berhasil! Silakan login.")
            st.session_state.page = "login"
            st.rerun()
        else:
            st.error("Harap isi semua kolom.")

    if st.button("Kembali ke Login"):
        st.session_state.page = "login"
        st.rerun()

# -------------------------------
# HALAMAN DASHBOARD
# -------------------------------
def dashboard_page():
    if 'user_data' not in st.session_state or not st.session_state.user_data:
        st.error("Anda belum login.")
        return

    user = st.session_state.user_data
    nama = user.get('Nama', 'Wajib Pajak')
    nik = user.get('NIK', '')
    plat = user.get('Plat', '')

    st.write(f"Selamat datang, {nama}")
    st.title("📋 Menu")

    # Sidebar navigasi
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
# MAIN LOGIC
# -------------------------------
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'dashboard':
    dashboard_page()