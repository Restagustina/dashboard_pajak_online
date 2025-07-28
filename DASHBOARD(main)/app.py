import streamlit as st
import pandas as pd
from utils import cek_login, daftar_akun

st.set_page_config("e-Pajak Samsat Palembang I", layout="wide")
st.title("🧾 e-Pajak Samsat Palembang I")

# Inisialisasi sesi
if "login" not in st.session_state:
    st.session_state.login = False
if "user" not in st.session_state:
    st.session_state.user = None

# ⛔ LOGOUT
def logout():
    st.session_state.login = False
    st.session_state.user = None

# 🟡 LOGIN PAGE
def login_page():
    st.subheader("🔐 Login Wajib Pajak")
    nik = st.text_input("Masukkan NIK")
    plat = st.text_input("Masukkan Plat Nomor (misal: BG1234XY)")
    if st.button("Login"):
        user = cek_login(nik, plat)
        if user is not None:
            st.session_state.login = True
            st.session_state.user = user.iloc[0]
            st.success("Login berhasil!")
        else:
            st.error("Data tidak ditemukan. Periksa kembali.")

    st.markdown("---")
    st.subheader("🆕 Belum punya akun?")
    if st.button("Daftar"):
        st.session_state.daftar = True

# 🟢 REGISTRASI PAGE
def daftar_page():
    st.subheader("📥 Daftar Akun Baru")
    nik = st.text_input("NIK")
    plat = st.text_input("Plat Kendaraan")
    nama = st.text_input("Nama")
    alamat = st.text_input("Alamat")
    if st.button("Buat Akun"):
        if daftar_akun(nik, plat, nama, alamat):
            st.success("Berhasil daftar. Silakan login.")
            st.session_state.daftar = False
        else:
            st.warning("Akun sudah ada.")

# 🔵 DASHBOARD PAGE
def dashboard_page():
    menu = st.sidebar.selectbox("📋 Menu", ["Profil", "Info Pajak", "Bayar Pajak", "Riwayat", "Logout"])

    if menu == "Profil":
        st.subheader("👤 Profil Anda")
        st.write(f"**Nama:** {st.session_state.user['Nama']}")
        st.write(f"**Alamat:** {st.session_state.user['Alamat']}")
        st.write(f"**NIK:** {st.session_state.user['NIK']}")
        st.write(f"**Plat:** {st.session_state.user['Plat']}")

    elif menu == "Info Pajak":
        st.subheader("📄 Informasi Pajak Kendaraan")
        st.write(f"**Pajak Terhutang:** Rp{int(st.session_state.user['Pajak_Terhutang']):,}")
        st.write(f"**Jatuh Tempo:** {st.session_state.user['Tanggal_Jatuh_Tempo']}")

    elif menu == "Bayar Pajak":
        st.subheader("💳 Simulasi Pembayaran")
        metode = st.selectbox("Pilih Metode Pembayaran", ["BRI", "Mandiri", "DANA", "OVO"])
        if st.button("Bayar Sekarang"):
            st.success(f"Simulasi pembayaran berhasil dengan {metode}")
            # Simpan ke riwayat jika mau

    elif menu == "Riwayat":
        st.subheader("📜 Riwayat Pembayaran Anda")
        st.info("Belum ada riwayat pembayaran (simulasi).")

    elif menu == "Logout":
        logout()
        st.experimental_rerun()

# 🌐 Routing Halaman
if "daftar" not in st.session_state:
    st.session_state.daftar = False

if not st.session_state.login:
    if st.session_state.daftar:
        daftar_page()
    else:
        login_page()
else:
    dashboard_page()
