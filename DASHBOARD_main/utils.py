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

# Debug path
print("BASE_PATH:", BASE_PATH)
print("PATH_USER:", PATH_USER)
print("PATH_KENDARAAN:", PATH_KENDARAAN)
print("PATH_RIWAYAT:", PATH_RIWAYAT)

@st.cache_data(ttl=1)  # Tambahkan ttl agar cache cepat refresh 1 detik
def load_data(data_type):
    """
    Load data tertentu ('user', 'kendaraan', atau 'riwayat') dari file Excel.
    Return 1 DataFrame sesuai permintaan.
    """
    if data_type == "user":
        if os.path.exists(PATH_USER):
            return pd.read_excel(PATH_USER, dtype=str).fillna("").applymap(str.strip)
        else:
            return pd.DataFrame(columns=["NIK", "Plat"])

    elif data_type == "kendaraan":
        if os.path.exists(PATH_KENDARAAN):
            return pd.read_excel(PATH_KENDARAAN, dtype=str).fillna("").applymap(str.strip)
        else:
            return pd.DataFrame(columns=[
                "NIK", "Plat", "Nama", "Alamat", "Pajak_Terhutang",
                "Tanggal_Jatuh_Tempo", "Pajak", "Nomor_Rangka", "Merek", "Model", "Warna"
            ])

    elif data_type == "riwayat":
        if os.path.exists(PATH_RIWAYAT):
            return pd.read_excel(PATH_RIWAYAT, dtype=str).fillna("").applymap(str.strip)
        else:
            return pd.DataFrame(columns=[
                "NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah", "Metode"
            ])

    else:
        raise ValueError(f"Tipe data tidak dikenal: {data_type}")

def load_all_data():
    return (
        load_data("user"),
        load_data("kendaraan"),
        load_data("riwayat")
    )

def save_data(new_user, new_kendaraan):
    """
    Simpan data user dan kendaraan baru ke file Excel.
    Hindari duplikat berdasarkan NIK (user) dan Plat (kendaraan).
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)

    df_user, df_kendaraan, _ = load_all_data()

    # Tambah dan hindari duplikat berdasarkan NIK dan Plat
    df_user = pd.concat([df_user, new_user], ignore_index=True)
    df_user = df_user.drop_duplicates(subset=["NIK"], keep="last")

    df_kendaraan = pd.concat([df_kendaraan, new_kendaraan], ignore_index=True)
    df_kendaraan = df_kendaraan.drop_duplicates(subset=["Plat"], keep="last")

    # Simpan ulang
    df_user.to_excel(PATH_USER, index=False)
    df_kendaraan.to_excel(PATH_KENDARAAN, index=False)

    # Buat riwayat pembayaran
    if not os.path.exists(PATH_RIWAYAT):
        df_riwayat = pd.DataFrame(columns=[
            "NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah", "Metode",
            "Nama_Penerima", "No_HP", "Alamat", "Jasa_Pengiriman"
        ])
        df_riwayat.to_excel(PATH_RIWAYAT, index=False)

    # Hapus cache agar bisa dibaca ulang
    st.cache_data.clear()


def update_status_lunas(nik, plat):
    """
    Update status kendaraan menjadi 'LUNAS' setelah pembayaran.
    """
    if not os.path.exists(PATH_KENDARAAN):
         return

    df_kendaraan = pd.read_excel(PATH_KENDARAAN, dtype=str).fillna("").applymap(str.strip)

    # Tambahkan kolom 'Status' jika belum ada
    if 'Status' not in df_kendaraan.columns:
        df_kendaraan['Status'] = ''

    mask = (df_kendaraan['NIK'] == nik) & (df_kendaraan['Plat'] == plat)
    df_kendaraan.loc[mask, 'Status'] = 'LUNAS'

    df_kendaraan.to_excel(PATH_KENDARAAN, index=False)
    st.cache_data.clear()
