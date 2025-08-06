# SIMANPA I - Sistem Informasi Pajak Kendaraan Palembang I
Proyek ini adalah aplikasi web berbasis Python + Streamlit untuk mempermudah pembayaran pajak kendaraan secara daring.

## 🚀 Fitur Utama
- ✅ Registrasi dan Login berbasis NIK & Plat Nomor
- 📄 Profil kendaraan & Info Pajak
- 💳 Simulasi Pembayaran (BRI, Mandiri, DANA, dll)
- 📜 Riwayat Pembayaran
- 🚚 Status Pengiriman Dokumen
- 🧠 Analisis Sentimen Komentar Publik terhadap SIGNAL menggunakan IndoBERT

## 🗂️ Struktur Folder
├── DASHBOARD_main/ # Folder utama aplikasi Streamlit
│ ├── assets/ # Gambar & background
│ ├── app.py # Tampilan utama
│ ├── utils.py # Fungsi bantu: load/save data, cetak resi
│ ├── data_user.xlsx # Data pengguna
│ ├── data_kendaraan.xlsx # Data kendaraan
│ ├── riwayat_pembayaran.xlsx # Riwayat pembayaran
│ └── status_pengiriman.xlsx # Data status kirim dokumen
│
├── Sentimen Analisis/ # Folder terpisah untuk analisis sentimen
│ ├── sentimen.ipynb # Notebook analisis komentar
│ ├── sentimen_signal.csv # Data komentar mentah
│ └── hasil_analisis_sentimen.csv # Hasil klasifikasi IndoBERT


## Teknologi yang Digunakan
- Python
- Streamlit
- Pandas & OpenPyXL
- FPDF (untuk cetak resi PDF)
- IndoBERT (analisis sentimen)

## Deploy
Aplikasi ini dapat diakses melalui:
👉 [streamlit.io](https://dashboardpajakonline-npapp95tg4xndqgpjgops5g.streamlit.app/) 

## Developer
Resta Gustina  
Mahasiswa Kerja Praktik di UPTB Samsat Palembang I 

## Catatan
- Proyek ini menggunakan penyimpanan lokal (Excel), bukan database online.
- Analisis sentimen dilakukan untuk menanggapi permasalahan SIGNAL secara data-driven.
