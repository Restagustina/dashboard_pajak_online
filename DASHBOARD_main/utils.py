# ============================
# IMPORT DAN INISIALISASI
# ============================
import os
import streamlit as st
import pandas as pd
import random
from fpdf import FPDF
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://vyhdnlzjmzoatchtihgj.supabase.co") 
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ5aGRubHpqbXpvYXRjaHRpaGdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NzE4ODAsImV4cCI6MjA3MDA0Nzg4MH0.HUBVYVPAMCwHITtMwGYx_9_t9drkVPhtRatwU30CjSo")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set zona waktu WIB (Waktu Indonesia Barat)
wib = timezone(timedelta(hours=7))

# ============================
# FUNGSI LOAD DATA
# ============================
@st.cache_data(ttl=1)  # Tambahkan ttl agar cache cepat refresh 1 detik
def load_data(data_type):
    """
    Load data tertentu dari Supabase berdasarkan data_type.
    Return 1 DataFrame sesuai permintaan.
    """
    mapping = {
        "user": ("users", ["nik", "plat", "nama", "password"]),
        "kendaraan": ("kendaraan", [
            "nik", "plat", "nama", "alamat",
            "tanggal_jatuh_tempo", "pajak", "norangka", "merek", "model", "warna"
        ]),
        "riwayat": ("riwayat_pembayaran", [
            "nik", "plat", "nama", "tanggal_bayar", "jumlah", "metode"
        ]),
        "pengiriman": ("status_pengiriman", [
            "nik", "plat", "nama", "alamat", "tanggal_pengiriman",
            "ekspedisi", "no_resi", "status_pengiriman", "estimasi_terkirim"
        ]),
    }

    if data_type not in mapping:
        raise ValueError(f"Tipe data tidak dikenal: {data_type}")

    table_name, columns = mapping[data_type]
    response = supabase.table(table_name).select("*").execute()
    data = response.data

    return pd.DataFrame(data) if data else pd.DataFrame(columns=columns)

# ============================
# FUNGSI LOAD SEMUA DATA
# ============================
def load_all_data():
    return (
        load_data("user"),
        load_data("kendaraan"),
        load_data("riwayat"),
        load_data("pengiriman")
    )

# ============================
# FUNGSI SIMPAN DATA USER & KENDARAAN
# ============================
def insert_user(nik, plat, nama, password):
    supabase.table("users").insert({
        "nik": nik,
        "plat": plat,
        "nama": nama,
        "password": password
    }).execute()
    st.cache_data.clear()

def insert_kendaraan(**kwargs):
    supabase.table("kendaraan").insert(kwargs).execute()
    st.cache_data.clear()

# ============================
# FUNGSI UPDATE STATUS LUNAS SETELAH PEMBAYARAN
# ============================
def update_status_lunas(nik, plat):
    """
    Update status kendaraan menjadi 'LUNAS' di Supabase setelah pembayaran.
    """
    supabase.table("kendaraan").update({"status": "LUNAS"}).match({
        "nik": nik,
        "plat": plat
    }).execute()

    st.cache_data.clear()

# ============================
# FUNGSI BUAT STATUS PENGIRIMAN BARU
# ============================
def buat_status_pengiriman(nik, plat, ekspedisi):
    """
    Buat entri baru status pengiriman di Supabase.
    """
    nomor_resi = f"RESI{random.randint(100000, 999999)}"
    status = "Diproses"
    tanggal_pengiriman = datetime.now(wib).strftime("%d-%m-%Y %H:%M")
    estimasi_terkirim = (datetime.now(wib) + timedelta(days=2)).strftime("%d-%m-%Y %H:%M")

    df_kendaraan = load_data("kendaraan")

    # Cari kendaraan berdasarkan NIK dan Plat
    kendaraan = df_kendaraan[(df_kendaraan["nik"] == nik) & (df_kendaraan["plat"] == plat)]
    if kendaraan.empty:
        return None  # Tidak ditemukan

    row = kendaraan.iloc[0]

    # Siapkan data untuk disimpan
    data_baru = {
        "nik": nik,
        "plat": plat,
        "nama": row["nama"],
        "alamat": row["alamat"],
        "tanggal_pengiriman": tanggal_pengiriman,
        "ekspedisi": ekspedisi,
        "no_resi": nomor_resi,
        "status_pengiriman": status,
        "estimasi_terkirim": estimasi_terkirim
    }

    # Hapus data lama (jika ada) berdasarkan nik & plat
    supabase.table("status_pengiriman").delete().match({
        "nik": nik,
        "plat": plat
    }).execute()

    # Insert data baru
    supabase.table("status_pengiriman").insert(data_baru).execute()
    st.cache_data.clear()

    return nomor_resi

# ============================
# FUNGSI UPDATE STATUS PENGIRIMAN OTOMATIS
# ============================
def update_status_pengiriman_otomatis():
    """
    Update otomatis status pengiriman menjadi 'Terkirim' jika sudah lewat 2 hari dari tanggal_pengiriman.
    """
    df = load_data("pengiriman")
    now = pd.Timestamp.now(tz=wib)

    updates = []
    for _, row in df.iterrows():
        if row.get("status_pengiriman") == "Diproses":
            try:
                tanggal_kirim = pd.to_datetime(row.get("tanggal_pengiriman"), format="%d-%m-%Y %H:%M", errors='coerce')
                if pd.notnull(tanggal_kirim) and (now - tanggal_kirim).days >= 2:
                    updates.append({
                        "nik": row["nik"],
                        "plat": row["plat"],
                        "status_pengiriman": "Terkirim"
                    })
            except:
                continue

    # Lakukan update di Supabase
    for u in updates:
        supabase.table("status_pengiriman").update({
            "status_pengiriman": u["status_pengiriman"]
        }).match({
            "nik": u["nik"],
            "plat": u["plat"]
        }).execute()

    st.cache_data.clear()

# ============================
# FUNGSI CETAK PDF RESI PENGIRIMAN
# ============================
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
        ("Tanggal Cetak", datetime.now(wib).strftime("%d-%m-%Y %H:%M")) 
    ]

    for label, value in data:
        pdf.cell(50, 10, txt=f"{label}", ln=0)
        pdf.cell(100, 10, txt=f": {value}", ln=1)

    pdf.ln(10)
    pdf.cell(0, 10, txt="Terima kasih telah menggunakan layanan SIMANPA I.", ln=True)

    return pdf.output(dest='S').encode('latin-1')  # PDF in bytes

# ============================
# FUNGSI CEK JATUH TEMPO
# ============================
def hitung_jatuh_tempo(riwayat_user):
    if riwayat_user.empty:
        return None, None, None  # Belum pernah bayar

    # Ambil pembayaran terakhir
    riwayat_user = riwayat_user.sort_values(by="tanggal_bayar", ascending=False)
    terakhir_bayar = pd.to_datetime(riwayat_user.iloc[0]["tanggal_bayar"])
    jatuh_tempo = terakhir_bayar + timedelta(days=365)
    hari_tersisa = (jatuh_tempo - datetime.today()).days

    return terakhir_bayar.date(), jatuh_tempo.date(), hari_tersisa