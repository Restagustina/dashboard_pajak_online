import pandas as pd

def load_user_data():
    return pd.read_excel("DASHBOARD(main)/data_user.xlsx")

def cek_login(nik, plat):
    df = load_user_data()
    user = df[(df['NIK'] == nik) & (df['Plat'] == plat)]
    return user if not user.empty else None

def daftar_akun(nik, plat, nama, alamat):
    df = load_user_data()
    if ((df['NIK'] == nik) & (df['Plat'] == plat)).any():
        return False
    new_user = pd.DataFrame([{
        "NIK": nik,
        "Plat": plat,
        "Nama": nama,
        "Alamat": alamat,
        "Pajak_Terhutang": 500000,
        "Tanggal_Jatuh_Tempo": "2025-08-30"
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_excel("DASHBOARD(main)/data_user.xlsx", index=False)
    return True