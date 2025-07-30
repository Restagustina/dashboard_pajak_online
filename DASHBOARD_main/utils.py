import os
import streamlit as st
import pandas as pd

# Path utama
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = BASE_PATH  # sudah di dalam folder DASHBOARD_main

# Path ke file Excel
PATH_USER = os.path.join(DATA_FOLDER, "data_user.xlsx")
PATH_KENDARAAN = os.path.join(DATA_FOLDER, "data_kendaraan.xlsx")
PATH_RIWAYAT = os.path.join(DATA_FOLDER, "riwayat_pembayaran.xlsx")

# Untuk debug lokal (hapus jika sudah produksi)
print("BASE_PATH:", BASE_PATH)
print("DATA_FOLDER:", DATA_FOLDER)
print("PATH_USER:", PATH_USER)

@st.cache_data
def load_data():
    if os.path.exists(PATH_USER):
        df_user = pd.read_excel(PATH_USER, dtype=str)
    else:
        df_user = pd.DataFrame(columns=["NIK", "Nama"])

    if os.path.exists(PATH_KENDARAAN):
        df_kendaraan = pd.read_excel(PATH_KENDARAAN, dtype=str)
    else:
        df_kendaraan = pd.DataFrame(columns=[
            "NIK", "Plat", "Nama", "Alamat", "Pajak_Terhutang",
            "Tanggal_Jatuh_Tempo", "Pajak"
        ])

    if os.path.exists(PATH_RIWAYAT):
        df_riwayat = pd.read_excel(PATH_RIWAYAT, dtype=str)
    else:
        df_riwayat = pd.DataFrame(columns=["NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah", "Metode"])

    return df_user, df_kendaraan, df_riwayat


def save_data(new_user, new_kendaraan):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    df_user, df_kendaraan, _ = load_data()

    # Tambah dan hindari duplikat berdasarkan NIK dan Plat
    df_user = pd.concat([df_user, new_user], ignore_index=True)
    df_user = df_user.drop_duplicates(subset=["NIK"], keep="last")

    df_kendaraan = pd.concat([df_kendaraan, new_kendaraan], ignore_index=True)
    df_kendaraan = df_kendaraan.drop_duplicates(subset=["Plat"], keep="last")

    df_user.to_excel(PATH_USER, index=False)
    df_kendaraan.to_excel(PATH_KENDARAAN, index=False)

    # Buat riwayat pembayaran jika belum ada
    if not os.path.exists(PATH_RIWAYAT):
        df_riwayat = pd.DataFrame(columns=["NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah", "Metode"])
        df_riwayat.to_excel(PATH_RIWAYAT, index=False)