import os
import streamlit as st
import pandas as pd
import random
from fpdf import FPDF
import datetime

# Path utama
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = BASE_PATH  # sudah di dalam folder DASHBOARD_main

# Path ke file Excel
PATH_USER = os.path.join(DATA_FOLDER, "data_user.xlsx")
PATH_KENDARAAN = os.path.join(DATA_FOLDER, "data_kendaraan.xlsx")
PATH_RIWAYAT = os.path.join(DATA_FOLDER, "riwayat_pembayaran.xlsx")
PATH_STATUS = os.path.join(DATA_FOLDER, "status_pengiriman.xlsx")

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
            return pd.DataFrame(columns=["NIK", "Plat", "Nama", "Password"])

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

def buat_status_pengiriman(nik, plat, ekspedisi):
    """
    Simulasi pembuatan status pengiriman dan nomor resi.
    """
    nomor_resi = f"RESI{random.randint(100000, 999999)}"
    
    df = pd.read_excel(PATH_KENDARAAN, dtype=str).fillna("")
    
    # Tambahkan kolom 'Status_Pengiriman' dan 'No_Resi' jika belum ada
    if 'Status_Pengiriman' not in df.columns:
        df['Status_Pengiriman'] = ''
    if 'No_Resi' not in df.columns:
        df['No_Resi'] = ''
    if 'Ekspedisi' not in df.columns:
        df['Ekspedisi'] = ''
    
    mask = (df['NIK'] == nik) & (df['Plat'] == plat)
    df.loc[mask, 'Status_Pengiriman'] = 'Diproses'
    df.loc[mask, 'No_Resi'] = nomor_resi
    df.loc[mask, 'Ekspedisi'] = ekspedisi

    df.to_excel(PATH_KENDARAAN, index=False)
    return nomor_resi

def update_status_pengiriman_otomatis():
    df = pd.read_excel(PATH_KENDARAAN, dtype={"NIK": str})

    now = pd.Timestamp.now()

    # Pastikan kolom yang dibutuhkan ada
    if "Status_Pengiriman" in df.columns and "Tanggal_Bayar" in df.columns:
        for i, row in df.iterrows():
            if row["Status_Pengiriman"] == "Diproses":
                try:
                    tanggal_bayar = pd.to_datetime(row["Tanggal_Bayar"], format="%d-%m-%Y %H:%M", errors='coerce')
                    if pd.notnull(tanggal_bayar) and (now - tanggal_bayar).days >= 2:
                        df.at[i, "Status_Pengiriman"] = "Terkirim"
                except:
                    continue

        # Simpan ulang
        df.to_excel(PATH_KENDARAAN, index=False)

def buat_pdf_resi(nik, nama, plat, ekspedisi, nomor_resi, alamat):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="BUKTI PENGIRIMAN DOKUMEN KENDARAAN", ln=True, align="C")
    pdf.ln(10)

    data = [
        ("NIK", nik),
        ("Nama", nama),
        ("Plat Kendaraan", plat),
        ("Jasa Pengiriman", ekspedisi),
        ("Nomor Resi", nomor_resi),
        ("Alamat Tujuan", alamat),
        ("Tanggal Cetak", datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
    ]

    for label, value in data:
        pdf.cell(50, 10, txt=f"{label}", ln=0)
        pdf.cell(100, 10, txt=f": {value}", ln=1)

    pdf.ln(10)
    pdf.cell(0, 10, txt="Terima kasih telah menggunakan layanan SIMANPA I.", ln=True)

    return pdf.output(dest='S').encode('latin-1')  # PDF in bytes