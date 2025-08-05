import streamlit as st
import pandas as pd
from datetime import timedelta, timezone
import os
import base64
from utils import load_data, load_all_data, save_data, update_status_lunas, buat_status_pengiriman, buat_pdf_resi
from streamlit.components.v1 import html
import calendar
import plotly.express as px

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
df_user, df_kendaraan, df_riwayat, df_pengiriman = load_all_data()

# -------------------------------
# LOGIN PAGE
# -------------------------------
def login_page():
    set_background("DASHBOARD_main/assets/bg.jpg") #background
    if st.session_state.get("registration_success", False):
        st.success("✅ Akun berhasil didaftarkan. Silakan login.")
        st.session_state.registration_success = False  # reset setelah ditampilkan

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

    # Input login
    input_nik = st.text_input("Masukkan NIK").strip()
    input_plat = st.text_input("Masukkan Plat").strip().upper()
    input_password = st.text_input("Masukkan Password", type="password")

    # Tombol Login default
    login_clicked = st.button("Login", key="login_button")
    if login_clicked:
        df_user, df_kendaraan, _, _ = load_all_data()

        # Cek apakah NIK & Password valid dari df_user
        user_match = df_user[
            (df_user["NIK"] == input_nik) &
            (df_user["Password"] == input_password)
        ]
        
        # Cek apakah Plat cocok dengan NIK dari df_kendaraan
        kendaraan_match = df_kendaraan[
            (df_kendaraan["Plat"].str.upper() == input_plat) &
            (df_kendaraan["NIK"] == input_nik)
         ]
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
            st.error("❌ NIK, Plat, atau Password salah. Silakan periksa kembali.")
            
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
            norangka = st.text_input("Nomor Rangka Kendaraan")
            merek = st.text_input("Merek / Type Kendaraan")
            model = st.text_input("Model Kendaraan (contoh: Sepeda Motor)")
            warna = st.selectbox("Warna Kendaraan", ["Hitam", "Putih", "Merah", "Biru", "Abu-abu", "Kuning"])
            pajak = st.number_input("Masukkan Jumlah Pajak (Rp)", min_value=0)
            default_tempo = date.today() + timedelta(days=365)
            tanggal_jatuh_tempo = st.date_input("Masukkan Tanggal Jatuh Tempo", value=default_tempo)
            password = st.text_input("Buat Password", type="password", help="Gunakan huruf besar, huruf kecil, angka, dan minimal 6 karakter.")
            
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

            # Validasi password (minimal 6 karakter, huruf besar, huruf kecil, angka)
            import re
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{6,}$', password):
                st.error("❌ Password harus mengandung huruf besar, huruf kecil, angka, dan minimal 6 karakter.")
                return

            # Simpan data
            new_user = pd.DataFrame([{"NIK": nik, "Nama": nama, "Password": password}])
            new_kendaraan = pd.DataFrame([{
                "NIK": nik,
                "Nama": nama,
                "Alamat": alamat,
                "Plat": plat,
                "Nomor_Rangka": norangka,
                "Merek": merek,
                "Model": model,
                "Warna": warna,
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
        "📊 Dashboard",  
        "💳 Bayar Pajak",  
        "📜 Riwayat Pembayaran",   
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

        df_kendaraan = load_data("kendaraan")
        kendaraan = df_kendaraan[df_kendaraan['NIK'] == nik].iloc[0]

        norangka = kendaraan['Nomor_Rangka']
        merek = kendaraan['Merek']
        model = kendaraan['Model']
        warna = kendaraan['Warna']
        pajak = float(kendaraan['Pajak_Terhutang']) 
        tempo = kendaraan['Tanggal_Jatuh_Tempo']

        html(f"""
            <style>
            .profil-box {{
                background-color: #eeeeee;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 20px 40px;
                max-width: 700px;
                margin: auto;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                font-family: 'Segoe UI', sans-serif;
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
                width: 180px;
                color: #333;
            }}
            </style>
            <div class="profil-box">
                <h4 style="text-align:center; background-color:#D9EAF7; padding:10px; border-radius:5px;">
                    Data Profil Wajib Pajak
                </h4>
                <table class="profil-table">
                    <tr><td class="label">NIK</td><td>: {nik}</td></tr>
                    <tr><td class="label">Nama</td><td>: {nama}</td></tr>
                    <tr><td class="label">Plat Nomor</td><td>: {plat}</td></tr>
                    <tr><td class="label">Alamat</td><td>: {alamat}</td></tr>
                    <tr><td class="label">Nomor Rangka</td><td>: {norangka}</td></tr>
                    <tr><td class="label">Merek</td><td>: {merek}</td></tr>
                    <tr><td class="label">Model</td><td>: {model}</td></tr>
                    <tr><td class="label">Warna</td><td>: {warna}</td></tr>
                    <tr><td class="label">Pajak Terhutang</td><td>: Rp {pajak:,.0f}</td></tr>
                    <tr><td class="label">Tanggal Jatuh Tempo</td><td>: {tempo}</td></tr>
                </table>
            </div>
        """, height=600)

    # Halaman Statistik Pajak User
    elif menu == "📊 Dashboard":
        st.markdown("""
        <style>
        .stApp {
            background-color: lightgray; 
        }
        </style>
        """, unsafe_allow_html=True)
         
        st.subheader("📊 Statistik Pajak Pribadi Anda")

        # Filter riwayat berdasarkan NIK
        df_riwayat = load_data("riwayat")
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
            df_user["Tanggal_Bayar"] = pd.to_datetime(df_user["Tanggal_Bayar"], errors="coerce", dayfirst=True)

            # Total bayar
            total_bayar = df_user["Jumlah"].astype(float).sum()
            total_transaksi = df_user.shape[0]

            # Metode favorit
            metode_fav = df_user["Metode"].mode()[0] if not df_user["Metode"].mode().empty else "-"

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

            # Visualisasi Data
            with st.expander("📊 Statistik"):
                # ========= Bar Chart: Pembayaran per Bulan =========
                df_user["Bulan"] = df_user["Tanggal_Bayar"].dt.strftime('%B')
                bayar_per_bulan = df_user.groupby("Bulan")["Jumlah"].sum().reset_index()
                bayar_per_bulan["Bulan"] = pd.Categorical(
                    bayar_per_bulan["Bulan"], categories=calendar.month_name[1:], ordered=True
                )
                bayar_per_bulan = bayar_per_bulan.sort_values("Bulan")

                st.subheader("📅 Total Pembayaran per Bulan")
                st.bar_chart(bayar_per_bulan.set_index("Bulan"))

                # ========= Line Chart: Tren Pembayaran =========
                df_user_sorted = df_user.sort_values("Tanggal_Bayar")
                df_trend = df_user_sorted.groupby("Tanggal_Bayar")["Jumlah"].sum().reset_index()

                st.subheader("📈 Tren Pembayaran Pajak")
                st.line_chart(df_trend.rename(columns={"Tanggal_Bayar": "Tanggal"}).set_index("Tanggal"))

                # ========= Histogram: Distribusi Jumlah Pembayaran =========
                st.subheader("🔢 Histogram Jumlah Pembayaran")
                fig_hist = px.histogram(df_user, x="Jumlah", nbins=10, title="Distribusi Jumlah Pembayaran")
                st.plotly_chart(fig_hist, use_container_width=True)

                # ========= Pie Chart: Metode Pembayaran =========
                st.subheader("🥧 Distribusi Metode Pembayaran")
                metode_counts = df_user["Metode"].value_counts().reset_index()
                metode_counts.columns = ["Metode", "Jumlah"]
                fig_pie = px.pie(metode_counts, names="Metode", values="Jumlah", title="Metode Pembayaran yang Digunakan")
                st.plotly_chart(fig_pie, use_container_width=True)

    # Halaman Bayar Pajak
    elif menu == "💳 Bayar Pajak": 
        st.markdown("""
        <style>
        .stApp {
            background-color: lightgray;
        }
        .judul-bayar {
            font-size: 14.5px;
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
        metode = st.selectbox("Pilih Metode Pembayaran", ["Bank Rakyat Indonesia (BRI)", "Bank Mandiri", "Bank Negara Indonesia (BNI)", "Bank Tabungan Negara (BTN)", "Bank Central Asia (BCA)", "Bank Syariah Indonesia (BSI)", "GoPay", "SeaBank"])

        # === Input Data Pengiriman Dokumen ===
        st.markdown('<div class="judul-bayar">📦 Lengkapi Data Pengiriman Dokumen</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            nama_penerima = st.text_input("Nama Penerima Dokumen")
            no_hp = st.text_input("No. HP Penerima")
        with col2:
            jasa = st.selectbox("Jasa Pengiriman", ["JNE", "J&T", "Pos Indonesia", "SiCepat", "GO-SEND"])
        alamat = st.text_area("Alamat Lengkap Tujuan")

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
            if not nama_penerima or not no_hp or not alamat or not jasa:
                st.warning("⚠️ Harap lengkapi semua data pengiriman dokumen sebelum membayar.")
            else:
                try:
                    # Set zona waktu WIB (Waktu Indonesia Barat)
                    wib = timezone(timedelta(hours=7))
                    waktu = pd.Timestamp.now(wib).strftime("%d-%m-%Y %H:%M")

                    df_user, df_kendaraan, df_riwayat, df_pengiriman  = load_all_data()
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
                            "Metode": metode,
                            "Nama_Penerima": nama_penerima,
                            "No_HP": no_hp,
                            "Alamat": alamat,
                            "Jasa_Pengiriman": jasa
                            }])

                        # Simpan riwayat pembayaran
                        df_riwayat = pd.concat([df_riwayat, new_row], ignore_index=True)
                        df_riwayat.to_excel("DASHBOARD_main/riwayat_pembayaran.xlsx", index=False)

                        # Update status pembayaran jadi Lunas
                        update_status_lunas(nik, plat)
                        # Buat status pengiriman & nomor resi
                        resi = buat_status_pengiriman(nik, plat, ekspedisi=jasa)
                        st.info(f"📦 Dokumen Anda akan dikirim via {jasa}.\n\nNomor Resi: `{resi}`")

                        # Menu Cetak Resi
                        pdf_bytes = buat_pdf_resi(nik, nama, plat, jasa, resi, alamat)

                        # Custom CSS khusus untuk tombol download PDF
                        custom_button_css = """
                        <style>
                        div.stDownloadButton > button:first-child {
                            background-color: #4CAF50;
                            color: white;
                            font-weight: bold;
                            border-radius: 8px;
                            padding: 0.6em 1.2em;
                            border: none;
                            transition: background-color 0.3s ease;
                        }
                        div.stDownloadButton > button:first-child:hover {
                            background-color: #45a049;
                        }
                        </style>
                        """
                        st.markdown(custom_button_css, unsafe_allow_html=True)

                        # Tombol Download PDF
                        st.download_button(
                            label="📄 Cetak Resi (PDF)",
                            data=pdf_bytes,
                            file_name=f"resi_{plat}_{resi}.pdf",
                            mime="application/pdf"
                        )


                        # Clear cache sebelum membaca ulang
                        st.cache_data.clear()
                        df_riwayat = load_data("riwayat")

                        # Tampilkan notifikasi sukses
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #d4edda;
                                padding: 10px;
                                border-left: 6px solid #28a745;
                                border-radius: 5px;
                            ">
                                <span style="color:#155724; font-weight:bold;">
                                    ✅ Pembayaran sebesar Rp{jumlah:,} via {metode} berhasil pada {waktu}.
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
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

                    # html_table = df_user.to_html(index=False, escape=False)
                    html_table = df_user.to_html(index=False, escape=False, classes="tabel-user")

                    # Styling CSS
                    tabel_style = """
                    <style>
                        table.tabel-user {
                            width: 100%;
                            border-collapse: collapse;
                            margin-bottom: 1em;
                            font-size: 10px;
                            table-layout: fixed;
                        }
                        table.tabel-user th, table.tabel-user td {
                            border: 1px solid #ccc;
                            padding: 10px;
                            text-align: left;
                            word-wrap: break-word;
                            overflow-wrap: break-word;
                        }
                        table.tabel-user th {
                            background-color: lightblue;
                            color: #333;
                        }
                        table.tabel-user td {
                            background-color: #f7f7f7;
                        }
                        table.tabel-user tr:nth-child(even) td {
                            background-color: #e6f2ff;
                        }
                        /* Kolom khusus: batasi lebar */
                        table.tabel-user td:nth-child(1),  /* NIK */
                        table.tabel-user td:nth-child(2),  /* Plat */
                        table.tabel-user td:nth-child(5),  /* Jumlah */
                        table.tabel-user td:nth-child(7),  /* No_HP */
                        table.tabel-user td:nth-child(8),  /* Alamat */
                        table.tabel-user td:nth-child(9)   /* Jasa_Pengiriman */
                        {
                            max-width: 120px;
                            white-space: normal;
                        }
                    </style>
                    """

                    # Tampilkan tabel
                    st.markdown(tabel_style, unsafe_allow_html=True)
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # =========================
                    # 🔄 Status Pengiriman
                    # =========================
                    df_pengiriman = pd.read_excel("DASHBOARD_main/status_pengiriman.xlsx", dtype={"NIK": str})
                    df_pengguna_pengiriman = df_pengiriman[(df_pengiriman["NIK"] == nik)]

                    if not df_pengguna_pengiriman.empty:
                        st.markdown("### 📦 Status Pengiriman Dokumen")

                        st.markdown("""
                        <style>
                        .status-card {
                            background-color: #eeeeee;
                            border: 1px solid #ccc;
                            border-radius: 8px;
                            padding: 15px;
                            margin-bottom: 20px;
                            max-width: 700px;
                            margin-left: auto;
                            margin-right: auto;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            font-family: 'Arial', sans-serif;
                        }

                        /* Tambahkan border */
                        .status-table {
                            width: 100%;
                            border-collapse: collapse;
                            border: 1px solid #999;  /* Tambahkan border ke seluruh tabel */
                        }

                        .status-table td {
                            padding: 6px 4px;
                            vertical-align: top;
                            font-size: 16px;
                            border: 1px solid #999;  /* Garis untuk tiap sel */
                        }

                        .status-table td.label {
                            font-weight: bold;
                            width: 180px;
                        }

                        .status-tag {
                            color: white;
                            padding: 4px 10px;
                            border-radius: 5px;
                            font-weight: bold;
                        }
                        </style>
                        """, unsafe_allow_html=True)


                        for _, row in df_pengguna_pengiriman.sort_values("Tanggal_Bayar", ascending=False).iterrows():
                            status = row["Status_Pengiriman"]
                            tanggal_kirim = row["Tanggal_Bayar"]
                            estimasi = (pd.to_datetime(tanggal_kirim, format="%d-%m-%Y %H:%M") + pd.Timedelta(days=2)).strftime("%d-%m-%Y")
                            resi = row["No_Resi"]
                            ekspedisi = row["Ekspedisi"]

                            if status == "Terkirim":
                                warna_status = "#28a745"  # hijau
                            elif status == "Diproses":
                                warna_status = "#ffc107"  # kuning
                            else:
                                warna_status = "#6c757d"  # abu

                            st.markdown(f"""
                            <div class="status-card">
                                <table class="status-table">
                                    <tr><td class="label">📦 Jasa Pengiriman</td><td>: {ekspedisi}</td></tr>
                                    <tr><td class="label">🧾 Nomor Resi</td><td>: <code>{resi}</code></td></tr>
                                    <tr><td class="label">📤 Tanggal Kirim</td><td>: {tanggal_kirim}</td></tr>
                                    <tr><td class="label">📅 Estimasi Tiba</td><td>: {estimasi}</td></tr>
                                    <tr><td class="label">📌 Status</td>
                                        <td>: <span class="status-tag" style="background-color:{warna_status};">{status}</span></td></tr>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)

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
    if st.sidebar.button("🔚Logout"):
        st.session_state.clear()
        st.session_state.page = "login"
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