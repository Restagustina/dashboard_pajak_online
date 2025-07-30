import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from utils import load_data, save_data

# -------------------------------
# SET BACKGROUND
# -------------------------------
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        backdrop-filter: blur(7px); /* Efek blur */
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# -------------------------------
# KONFIGURASI AWAL
# -------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_PATH, "assets", "bg.jpg")
set_background(image_path)  # SET BACKGROUND di awal

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
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&display=swap');

    .custom-title {
        font-size: 60px;
        font-weight: bold;
        text-align: center;
        text-transform: uppercase;
        font-family: 'Anton', sans-serif;
        background: linear-gradient(to top left, yellow, white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .custom-subtitle {
        text-align: center;
        font-size: 18px;
        color: white;
        margin-top: 0px;
        margin-bottom: 30px; /* tambahkan jarak bawah sub title to input nik*/
        font-family: 'Arial', sans-serif;
        letter-spacing: 1px;
    }
    </style>

    <div class="custom-title">
        SIMANPA I
    </div>
    <div class="custom-subtitle">
        Sistem Informasi Pembayaran Pajak Kendaraan Palembang 1
    </div>
    """, unsafe_allow_html=True)

    input_nik = st.text_input("Masukkan NIK").strip()
    input_plat = st.text_input("Masukkan Plat").strip().upper()

    # Tombol Login biasa (biarkan default)
    login_clicked = st.button("Login", key="login_button")

    # Tombol Registrasi
    st.markdown("""
    <style>
    .info-text {
        text-align: center;
        margin-top: 20px;
        font-size: 15px;
        font-family: 'Arial', sans-serif;
    }

    .info-text span {
        color: white;
        margin-right: 8px;
    }

    .register-link {
        color: white; /* ubah warna jadi putih */
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 5px;
        font-weight: bold;
        text-decoration: none;
        transition: color 0.3s ease;
    }

    .register-link:hover {
        color: #ffcdd2; /* efek hover jadi merah muda */
    }
    </style>

    <div class="info-text">
        <span>Belum Punya Akun?</span>
        <a href="?daftar=true" class="register-link">Registrasi Now</a>
    </div>
""", unsafe_allow_html=True)


    # Login logic
    if login_clicked:
        user_match = df_user[df_user['NIK'] == input_nik]
        kendaraan_match = df_kendaraan[df_kendaraan['Plat'].str.upper() == input_plat]

        if not user_match.empty and not kendaraan_match.empty:
            st.session_state.user_data = {
                'NIK': input_nik,
                'Plat': input_plat,
                'Nama': user_match.iloc[0].get('Nama', ''),
                'Pajak': kendaraan_match.iloc[0].get('Pajak', '')
            }
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.error("❌ Data tidak ditemukan. Periksa kembali NIK dan Plat.")

    if st.query_params.get("daftar") == "true":
        st.session_state.page = "register"
        st.rerun()

# -------------------------------
# REGISTER PAGE
# -------------------------------
from datetime import date, timedelta
import pandas as pd
import streamlit as st

def register_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    .judul {
        font-family: 'Poppins', sans-serif;
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(to top left, yellow, white);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    </style>

    <div class='judul'>Daftar Akun Baru</div>
    """, unsafe_allow_html=True)

    if 'registration_success' not in st.session_state:
        st.session_state.registration_success = False

    if not st.session_state.registration_success:
        with st.form("register_form"):
            nik = st.text_input("Masukkan NIK").strip()
            nama = st.text_input("Masukkan Nama Lengkap").strip()
            alamat = st.text_input("Masukkan Alamat").strip()
            plat = st.text_input("Masukkan Plat Kendaraan").strip().upper()
            pajak = st.number_input("Masukkan Jumlah Pajak (Rp)", min_value=0)
            default_tempo = date.today() + timedelta(days=365)
            tanggal_jatuh_tempo = st.date_input("Masukkan Tanggal Jatuh Tempo", value=default_tempo)

            submit = st.form_submit_button("Daftar")

        if submit:
            # Validasi input
            if not nik or not nama or not alamat or not plat or pajak <= 0:
                st.error("❌ Harap lengkapi semua data dengan benar.")
                return
            
            if len(nik) != 16 or not nik.isdigit():
                st.error("❌ NIK harus terdiri dari 16 digit angka.")
                return

            if nik in df_user['NIK'].values:
                st.error("❌ NIK sudah terdaftar. Silakan login atau gunakan NIK lain.")
                return

            if plat in df_kendaraan['Plat'].values:
                st.error("❌ Plat kendaraan sudah terdaftar.")
                return

            # Simpan data
            new_user = pd.DataFrame([{"NIK": nik, "Nama": nama}])
            new_kendaraan = pd.DataFrame([{
                "NIK": nik,
                "Plat": plat,
                "Nama": nama,
                "Alamat": alamat,
                "Pajak_Terhutang": pajak,
                "Tanggal_Jatuh_Tempo": tanggal_jatuh_tempo,
                "Pajak": pajak
            }])

            save_data(new_user, new_kendaraan)

            # Tampilkan halaman sukses
            st.session_state.registration_success = True
            st.rerun()

    # ---------------------
    # Jika sukses daftar
    # ---------------------
    else:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.success("✅ Akun berhasil didaftarkan. Silakan login.")
        if st.button("🔐 Kembali ke Halaman Login", use_container_width=True):
            st.session_state.page = "login"
            st.session_state.registration_success = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
def dashboard_page():
    if not st.session_state.user_data:
        st.error("Anda belum login.")
        return

    user = st.session_state.user_data
    nama, nik, plat = user.get('Nama', ''), user.get('NIK', ''), user.get('Plat', '')

    st.write(f"Selamat datang, {nama}")
    st.title("📋 Menu")

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
# ROUTING HALAMAN
# -------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "dashboard":
    dashboard_page()  
