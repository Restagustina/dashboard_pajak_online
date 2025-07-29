import streamlit as st
import pandas as pd
import os

# Dapatkan direktori absolut dari file utils.py
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Gabungkan dengan folder data
DATA_FOLDER = os.path.join(BASE_PATH, "DASHBOARD_main")

# Path lengkap ke file Excel
PATH_USER = os.path.join(DATA_FOLDER, "data_user.xlsx")
PATH_KENDARAAN = os.path.join(DATA_FOLDER, "data_kendaraan.xlsx")
PATH_RIWAYAT = os.path.join(DATA_FOLDER, "riwayat_pembayaran.xlsx")

@st.cache_data
def load_data():
    if os.path.exists(PATH_USER):
        df_user = pd.read_excel(PATH_USER, dtype=str)
    else:
        df_user = pd.DataFrame(columns=["NIK", "Nama"])

    if os.path.exists(PATH_KENDARAAN):
        df_kendaraan = pd.read_excel(PATH_KENDARAAN, dtype=str)
    else:
        df_kendaraan = pd.DataFrame(columns=["NIK", "Plat", "Pajak_Terhutang"])

    if os.path.exists(PATH_RIWAYAT):
        df_riwayat = pd.read_excel(PATH_RIWAYAT, dtype=str)
    else:
        df_riwayat = pd.DataFrame(columns=["NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah", "Metode"])

    return df_user, df_kendaraan, df_riwayat

def save_data(df_user, df_kendaraan, df_riwayat):
    df_user.to_excel(PATH_USER, index=False)
    df_kendaraan.to_excel(PATH_KENDARAAN, index=False)
    df_riwayat.to_excel(PATH_RIWAYAT, index=False)