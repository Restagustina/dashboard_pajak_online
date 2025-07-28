import pandas as pd
from datetime import datetime

def cek_login(nik, plat):
    df = pd.read_csv("DASHBOARD(main)/data_kendaraan.csv")
    match = df[(df['NIK'] == nik) & (df['Plat'].str.upper() == plat.upper())]
    return not match.empty

def get_info_kendaraan(nik, plat):
    df = pd.read_csv("DASHBOARD(main)/data_kendaraan.csv")
    match = df[(df['NIK'] == nik) & (df['Plat'].str.upper() == plat.upper())]
    if not match.empty:
        return match.iloc[0]
    return None

def simpan_riwayat(data):
    path = "riwayat_pembayaran.csv"
    try:
        df_riwayat = pd.read_csv(path)
    except FileNotFoundError:
        df_riwayat = pd.DataFrame(columns=["NIK", "Plat", "Nama", "Tanggal_Bayar", "Jumlah"])

    new_row = {
        "NIK": data["NIK"],
        "Plat": data["Plat"],
        "Nama": data["Nama"],
        "Tanggal_Bayar": datetime.today().strftime('%Y-%m-%d'),
        "Jumlah": data["Pajak_Terhutang"]
    }

    df_riwayat = pd.concat([df_riwayat, pd.DataFrame([new_row])], ignore_index=True)
    df_riwayat.to_csv(path, index=False)
