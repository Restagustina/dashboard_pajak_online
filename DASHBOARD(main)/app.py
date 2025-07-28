import streamlit as st
import pandas as pd
from utils import cek_login, get_info_kendaraan, simpan_riwayat

st.set_page_config(page_title="e-Pajak Samsat Palembang I", layout="centered")
st.title("🧾 e-Pajak Samsat Palembang I (Prototype)")

# Login
if 'login' not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.subheader("🔐 Login Wajib Pajak")
    nik = st.text_input("Masukkan NIK")
    plat = st.text_input("Masukkan Plat Nomor Kendaraan (misal: BG1234XY)")

    if st.button("Login"):
        if cek_login(nik, plat):
            st.success("Login berhasil!")
            st.session_state.login = True
            st.session_state.nik = nik
            st.session_state.plat = plat
        else:
            st.error("Data tidak ditemukan. Periksa kembali NIK dan plat.")
else:
    # Info Pajak
    st.subheader("📋 Informasi Pajak Kendaraan")
    data = get_info_kendaraan(st.session_state.nik, st.session_state.plat)

    if data is not None:
        st.write(f"**Nama:** {data['Nama']}")
        st.write(f"**Alamat:** {data['Alamat']}")
        st.write(f"**Pajak Terhutang:** Rp{int(data['Pajak_Terhutang']):,}".replace(",", "."))
        st.write(f"**Jatuh Tempo:** {data['Tanggal_Jatuh_Tempo']}")

        if st.button("Bayar Sekarang"):
            st.success("✅ Pembayaran berhasil (simulasi)")
            simpan_riwayat(data)

    # Riwayat
    st.subheader("📜 Riwayat Pembayaran Anda")
    try:
        df = pd.read_csv("riwayat_pembayaran.csv")
        df_user = df[df['NIK'] == st.session_state.nik]
        st.dataframe(df_user)
    except FileNotFoundError:
        st.info("Belum ada riwayat pembayaran.")
