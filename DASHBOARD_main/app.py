import streamlit as st
import pandas as pd
from datetime import date, timedelta
import os
import base64
from utils import load_data, save_data, update_status_lunas
import openpyxl
from streamlit.components.v1 import html
from st_aggrid import AgGrid, GridOptionsBuilder

# -------------------------------
# SESSION STATE & QUERY PARAM DETECTION
# -------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'login' not in st.session_state:
    st.session_state.login = False


# -------------------------------
# DETEKSI ?daftar=true
# -------------------------------
query_params = st.query_params
if query_params.get("daftar", [""])[0].lower() == "true":
    st.session_state.page = "register"
    st.query_params.clear()  # hapus param biar tidak rerun terus
    st.rerun()

# -------------------------------
# SET BACKGROUND
# -------------------------------
def set_background(image_path=None, color=None):
    css = ""
    
    # Jika menggunakan gambar
    if image_path:
        if not os.path.exists(image_path):
            st.warning("Gambar background tidak ditemukan.")
            return
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
            backdrop-filter: blur(7px);
        }}
        </style>
        """
    
    # Jika menggunakan warna saja (untuk dashboard)
    elif color:
        css = f"""
        <style>
        .stApp {{
            background-color: {color};
            background-image: none;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 2rem;
            backdrop-filter: blur(4px);
        }}
        </style>
        """
    
    if css:
        st.markdown(css, unsafe_allow_html=True)

# -------------------------------
# KONFIGURASI AWAL
# -------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_PATH, "assets", "bg.jpg")

# -------------------------------
# LOAD DATA
# -------------------------------
df_user, df_kendaraan, df_riwayat = load_data()

# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_page():
    set_background("DASHBOARD_main/assets/bg.jpg") #background
    if st.session_state.get("registration_success", False):
        st.success("✅ Akun berhasil didaftarkan. Silakan login.")
        st.session_state.registration_success = False  # reset di sini setelah ditampilkan

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

    # Tombol Login default
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

    .register-button {
        background: none;
        border: none;
        color: white;
        font-weight: bold;
        text-decoration: underline;
        cursor: pointer;
    }

    .register-button:hover {
        color: #ffcdd2;
    }
    </style>

    <div class="info-text">
        <span>Belum Punya Akun?</span>
    </div>
    """, unsafe_allow_html=True)

    # Tombol "Registrasi Now" (streamlit button terlihat seperti link)
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("Registrasi Now", key="register_now"):
            st.session_state.page = "register"
            st.rerun()


    # Login logic
    if login_clicked:
        user_match = df_user[df_user['NIK'] == input_nik]
        kendaraan_match = df_kendaraan[df_kendaraan['Plat'].str.upper() == input_plat]

        if not user_match.empty and not kendaraan_match.empty:
            st.session_state.user_data = {
                'NIK': input_nik,
                'Plat': input_plat,
                'Nama': user_match.iloc[0].get('Nama', ''),
                'Alamat': kendaraan_match.iloc[0].get('Alamat', ''),
                'Pajak': kendaraan_match.iloc[0].get('Pajak', '')
            }
            st.session_state.page = 'dashboard'
            st.rerun()
        else:
            st.error("❌ Data tidak ditemukan. Periksa kembali NIK dan Plat.")

 # Tombol fallback untuk hapus param ?daftar=true
    query_params = st.query_params
    if query_params.get("daftar", [""])[0].lower() == "true":
        if st.button("🔐 Kembali ke Halaman Login", use_container_width=True):
            st.query_params.clear()  # hapus param dari URL
            st.session_state.page = "login"
            st.rerun()

# -------------------------------
# REGISTER PAGE
# -------------------------------
def register_page():
    set_background("DASHBOARD_main/assets/bg.jpg")
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
        # Gunakan tombol yang hanya tampil di register_page
        if st.button("🔐 Kembali ke Halaman Login", use_container_width=True, key="back_to_login_from_register"):
            st.session_state.page = "login"
            st.query_params.clear() # hapus query param ?daftar=true
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------
# DASHBOARD PAGE
# -------------------------------
def dashboard_page():
    if not st.session_state.user_data:
        st.error("Anda belum login.")
        return

    # Styling
    st.markdown("""
    <style>
    /* Warna teks utama jadi hitam */
    .stApp, .block-container, .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader {
        color: #000000 !important;
    }

    /* Sidebar gradasi */
    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #1976d2, #26a69a);
        color: white;
    }

    /* Sidebar hover effect */
    [data-testid="stSidebar"] ul {
        padding-left: 0;
    }

    [data-testid="stSidebar"] li:hover {
        background-color: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding-left: 8px;
        font-weight: bold;
        transition: 0.3s ease;
        cursor: pointer;
    }

    /* Konten utama */
    .main .block-container {
        background-color: #ffffff !important;
        padding: 2rem 3rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* Chip status */
    .chip {
        display: inline-block;
        padding: 4px 10px;
        margin-left: 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: white;
    }
    .chip.aktif {
        background-color: #4caf50;
    }
    .chip.menunggu {
        background-color: #ffc107;
        color: #000;
    }
    .chip.jatuh-tempo {
        background-color: #2196f3;
    }

    h1, h2 {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Ambil data user dari session
    user = st.session_state.user_data
    nama, nik, plat, alamat = user.get('Nama', ''), user.get('NIK', ''), user.get('Plat', ''), user.get('Alamat', '')

    # Header
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Anton&display=swap');

    /* Hilangkan padding atas bawaan Streamlit */
    div.block-container {
        padding-top: 0rem;
    }

    /* Logo SIMANPA I */
    .simanpa-logo {
        font-family: 'Anton', sans-serif;
        font-size: 96px;
        font-weight: bold;
        background: linear-gradient(to top left, #6B8E23, #C0FF00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: -50;
        padding-top: 30px;
    }

    /* Subtitle */
    .simanpa-subtitle {
        font-size: 14px;
        text-align: center;
        margin-top:-35px;
        color: #555;
        font-family: Arial, sans-serif;
    }
    </style>

    <div class="simanpa-logo">SIMANPA I</div>
    <div class="simanpa-subtitle">Sistem Informasi Pembayaran Pajak Kendaraan Palembang I</div>
    """, unsafe_allow_html=True)

    # Sidebar navigasi
    st.sidebar.markdown("## 🧭 Menu Navigasi")
    menu = st.sidebar.radio("Pilih Halaman", [
        "👤 Profil", 
        "📊 Statistik Saya",  
        "💳 Bayar Pajak",  
        "📜 Riwayat Pembayaran",  
        "🔚 Logout" 
    ])

    # Halaman Profil
    if menu == "👤 Profil":
        st.markdown("""
        <style>
        .stApp {
            background-color: lightgray; 
        }
        </style>
        """, unsafe_allow_html=True)

        html(f"""
            <style>
            .profil-box {{
                background-color: #eeeeee;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 2px;
                padding-left: 50px;
                padding-bottom: 50px;
                max-width: 600px;
                margin: auto;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                font-family: 'Arial', sans-serif;
            }}
            .profil-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .profil-table td {{
                padding: 8px 5px;
                vertical-align: top;
                font-size: 16px;
            }}
            .profil-table td.label {{
                font-weight: bold;
                width: 150px;
            }}
            </style>
            <div class="profil-box">
                <h4 style="text-align:center;">Data Profil</h4>
                <table class="profil-table">
                    <tr><td class="label">NIK</td><td>: {nik}</td></tr>
                    <tr><td class="label">Nama</td><td>: {nama}</td></tr>
                    <tr><td class="label">Plat Nomor</td><td>: {plat}</td></tr>
                    <tr><td class="label">Alamat</td><td>: {alamat}</td></tr>
                </table>
            </div>
        """, height=500)


    # Halaman Statistik Pajak User
    elif menu == "📊 Statistik Saya":
        st.markdown("""
        <style>
        .stApp {
            background-color: lightgray; 
        }
        </style>
        """, unsafe_allow_html=True)
         
        st.subheader("📊 Statistik Pajak Pribadi Anda")

        # Ambil NIK user yang sedang login
        nik_login = st.session_state.get("nik")

        # Filter riwayat berdasarkan NIK
        _, _, df_riwayat = load_data()
        df_user = df_riwayat[df_riwayat["NIK"] == nik]

        if df_user.empty:
            st.markdown(
                """
                <div style='
                    background-color: #fff3cd;
                    padding: 12px;
                    border-radius: 5px;
                    border-left: 6px solid #ffecb5;
                    color: #555;
                '>
                    ⚠️ Belum ada data pembayaran.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            # Konversi tanggal
            df_user["Tanggal_Bayar"] = pd.to_datetime(df_user["Tanggal_Bayar"], errors="coerce")

            # Total bayar
            total_bayar = df_user["Jumlah"].astype(float).sum()
            total_transaksi = df_user.shape[0]

            # Metode favorit
            metode_fav = df_user["Metode"].mode()[0] if not df_user["Metode"].mode().empty else "-"

            # Bulan paling sering bayar
            bulan_fav = df_user["Tanggal_Bayar"].dt.month_name().value_counts().idxmax()

            # Card Ringkasan
            st.markdown("""
                <style>
                .info-card {
                    background-color: #e7f3fe;
                    padding: 15px;
                    border-left: 6px solid #2196F3;
                    border-radius: 6px;
                    margin-bottom: 15px;
                    color: #004085;
                    font-size: 16px;
                }
                </style>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class='info-card'>
                    💰 <strong>Total Bayar:</strong> Rp {total_bayar:,.0f}
                </div>
                <div class='info-card'>
                    🧾 <strong>Jumlah Transaksi:</strong> {total_transaksi}
                </div>
                <div class='info-card'>
                    📱 <strong>Metode Favorit:</strong> {metode_fav}
                </div>
            """, unsafe_allow_html=True)

            # Grafik bulanan
            df_user["Bulan"] = df_user["Tanggal_Bayar"].dt.strftime('%B')
            bayar_per_bulan = df_user.groupby("Bulan")["Jumlah"].sum().reset_index()

            st.bar_chart(bayar_per_bulan.rename(columns={"Jumlah": "Total Pembayaran"}).set_index("Bulan"))

    # Halaman Bayar Pajak
    elif menu == "💳 Bayar Pajak": 
        st.markdown("""
        <style>
        .stApp {
            background-color: lightgray;
        }
        .judul-bayar {
            font-size: 14,5px;
            color: #555555;
            text-align: left;
            margin-top: 40px;
            margin-bottom: 5px;
            font-family: 'Arial', sans-serif;
        }
        label[data-testid="stWidgetLabel"] {
            color: black !important;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="judul-bayar">Silakan selesaikan pembayaran pajak kendaraan Anda di bawah ini.</div>', unsafe_allow_html=True)

        jumlah = st.number_input("Masukkan Jumlah Pembayaran", min_value=0, step=10000)
        metode = st.selectbox("Pilih Metode Pembayaran", ["Bank Rakyat Indonesia (BRI)", "Bank Mandiri", "Bank Negara Indonesia (BNI)", "Bank Tabungan Negara (BTN)", "OBank Central Asia (BCA)", "Bank Syariah Indonesia (BSI)", "GoPay", "SeaBank"])

        # Styling tombol Bayar Sekarang
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #444444;
                color: red;        
                font-weight: bold;
                border-radius: 5px;
                padding: 0.5em 1em;
                border: none;
            }

            div.stButton > button:first-child:hover {
                background-color: #666666; 
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("Bayar Sekarang"):
            try:
                waktu = pd.Timestamp.now().strftime("%d-%m-%Y %H:%M")

                df_user, df_kendaraan, df_riwayat = load_data()
                data_user = df_kendaraan[df_kendaraan["NIK"] == nik]

                if not data_user.empty:
                    nama = data_user.iloc[0]["Nama"]
                    plat = data_user.iloc[0]["Plat"]

                    new_row = pd.DataFrame([{
                        "NIK": str(nik),
                        "Plat": plat,
                        "Nama": nama,
                        "Tanggal_Bayar": waktu,
                        "Jumlah": jumlah,
                        "Metode": metode
                    }])

                    df_riwayat = pd.concat([df_riwayat, new_row], ignore_index=True)
                    df_riwayat.to_excel("DASHBOARD_main/riwayat_pembayaran.xlsx", index=False)

                    update_status_lunas(nik, plat)

                    # Clear cache sebelum membaca ulang
                    st.cache_data.clear()

                    # Reload dan tampilkan data terbaru
                    _, _, df_riwayat = load_data()
                    st.success(f"✅ Pembayaran sebesar Rp{jumlah:,} via {metode} berhasil pada {waktu}.")
                    st.write("🔍 Data terbaru di file:")
                    st.dataframe(df_riwayat)
                else:
                    st.warning("⚠️ Data kendaraan tidak ditemukan.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyimpan pembayaran: {e}")   


    # Halaman Riwayat Pembayaran
    elif menu == "📜 Riwayat Pembayaran": 
            st.markdown("""
            <style>
            .stApp {
                background-color: lightgray; 
            }
            </style>
            """, unsafe_allow_html=True)

            st.subheader("📜 Riwayat Pembayaran") 
            try:
                df_riwayat = pd.read_excel("DASHBOARD_main/riwayat_pembayaran.xlsx", dtype={"NIK": str})
                df_user = df_riwayat[df_riwayat["NIK"] == nik]

                if not df_user.empty:
                    st.markdown("""
                    <div style="
                        background-color: #d4edda;
                        padding: 1em;
                        border-radius: 5px;
                        color: #155724;
                        border-left: 5px solid #28a745;
                        font-weight: 500;
                        margin-bottom: 1em;
                    ">
                    ✅ Riwayat pembayaran ditemukan.
                    </div>
                    """, unsafe_allow_html=True)

                    gb = GridOptionsBuilder.from_dataframe(df_user)

                    # Auto width untuk semua kolom
                    gb.configure_default_column(autoWidth=True)

                    # Opsional: pagination + layout
                    gb.configure_grid_options(domLayout='normal')
                    gb.configure_pagination(paginationAutoPageSize=True)

                    # Tampilkan
                    AgGrid(
                        df_user,
                        gridOptions=gb.build(),
                        theme="balham",
                        fit_columns_on_grid_load=False
                    )

                else:
                    st.markdown("""
                    <div style="
                        background-color: #fff3cd;
                        padding: 1em;
                        border-radius: 5px;
                        color: #856404;
                        border-left: 5px solid #ffc107;
                        font-weight: 500;
                    ">
                    ⚠️ Belum ada riwayat pembayaran.
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Gagal membaca data riwayat: {e}")

    # Logout
    elif menu == "🔚 Log out": 
        st.session_state.user_data = {}
        st.session_state
        st.session_state.page = 'login'
        st.success("Logout berhasil.")
        st.rerun()

    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<center><small>© 2025 SIMANPA Samsat Palembang I</small></center>", unsafe_allow_html=True)

# -------------------------------
# ROUTING HALAMAN
# -------------------------------
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "register":
    register_page()
elif st.session_state.page == "dashboard":
    dashboard_page()  
