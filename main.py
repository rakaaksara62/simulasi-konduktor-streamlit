import streamlit as st
import pandas as pd

# Fungsi untuk memotong desimal secara ketat tanpa pembulatan (Truncate)
def potong_desimal(nilai):
    """
    Mengambil tepat 2 angka di belakang koma tanpa pembulatan.
    Contoh: 3.659 -> 3.65 (Bukan 3.66)
    """
    s = str(float(nilai))
    if "." in s:
        kepala, ekor = s.split(".")
        # Ambil 2 digit pertama ekor, atau tambahkan 0 jika kurang
        ekor_fix = (ekor + "00")[:2]
        return f"{kepala}.{ekor_fix}"
    return f"{s}.00"

st.set_page_config(page_title="Kalkulator SAIFI SAIDI Fleksibel", layout="wide")

st.title("🧮 Kalkulator SAIFI & SAIDI (Fleksibel)")
st.markdown("""
Aplikasi ini memungkinkan Anda memilih metode input:
1. **Sesuai Rumus Jurnal**: Input desimal langsung (Contoh: 15 jam 46 menit ditulis `15.46`).
2. **Input Jam & Menit**: Konversi matematis yang benar (`Jam + Menit/60`).
""")

# --- 1. PILIH METODE ---
st.sidebar.header("⚙️ Pengaturan")
metode_input = st.sidebar.radio(
    "Pilih Metode Input Durasi:",
    ["Sesuai Rumus Jurnal (Desimal)", "Input Jam & Menit (Matematis)"]
)

# --- 2. SIAPKAN DATA ---

# Data Pelanggan & Frekuensi (Sama untuk kedua metode)
data_base = {
    "Penyulang": ["GDN 01", "GDN 02", "GDN 03", "GDN 04", "GDN 05", "WBN 06", "BNL 08"],
    "Pelanggan (Ni)": [20561, 16329, 14795, 17352, 10204, 13424, 14363],
    "Frekuensi (λi)": [19, 6, 15, 22, 17, 9, 8],
}

if metode_input == "Sesuai Rumus Jurnal (Desimal)":
    st.sidebar.info("Mode ini menggunakan angka desimal seperti yang tertulis di rumus halaman 7 jurnal.")
    # Data Durasi (Desimal) - DISESUAIKAN DENGAN PERMINTAAN USER
    # GDN 04 = 15.38 (Sesuai User)
    # GDN 05 = 12.5 (Sesuai User)
    data_durasi = {
        "Durasi (Ui)": [15.46, 5.43, 13.25, 15.38, 12.5, 7.00, 6.29]
    }
    # Gabungkan
    df_input = pd.DataFrame({**data_base, **data_durasi})
    
    # Editor
    df_edit = st.sidebar.data_editor(df_input, num_rows="dynamic")
    
    # Kolom yang dipakai untuk hitung
    df_edit["Durasi Hitung"] = df_edit["Durasi (Ui)"]
    df_edit["Label Durasi"] = df_edit["Durasi (Ui)"].astype(str)

else:
    st.sidebar.info("Mode ini menghitung durasi secara matematis (Menit dibagi 60).")
    # Data Jam & Menit (Sesuai Tabel 4.4 Fisik)
    # GDN 04 di tabel fisik tertulis 38 jam 15 menit, tapi user bisa ubah sendiri jika mau
    data_waktu = {
        "Jam": [15, 5, 13, 38, 5, 7, 6],
        "Menit": [46, 43, 35, 15, 12, 0, 29]
    }
    df_input = pd.DataFrame({**data_base, **data_waktu})
    
    # Editor
    df_edit = st.sidebar.data_editor(df_input, num_rows="dynamic")
    
    # Hitung Durasi Matematis
    df_edit["Durasi Hitung"] = df_edit["Jam"] + (df_edit["Menit"] / 60)
    df_edit["Label Durasi"] = df_edit["Jam"].astype(str) + "j " + df_edit["Menit"].astype(str) + "m"


total_pelanggan = df_edit["Pelanggan (Ni)"].sum()

# --- 3. PROSES PERHITUNGAN (TRUNCATE 2 DIGIT) ---

hasil_rows = []

# Variabel akumulasi (manual sum dari hasil potong)
saifi_display_sum = 0.0
saidi_display_sum = 0.0

for index, row in df_edit.iterrows():
    nama = row["Penyulang"]
    ni = row["Pelanggan (Ni)"]
    li = row["Frekuensi (λi)"]
    ui = row["Durasi Hitung"]
    label_durasi = row["Label Durasi"]
    
    # Rumus Kontribusi: (Ni * Nilai) / Total Pelanggan
    kontribusi_saifi_raw = (ni * li) / total_pelanggan
    kontribusi_saidi_raw = (ni * ui) / total_pelanggan
    
    # Potong Desimal (String Manipulation)
    saifi_str = potong_desimal(kontribusi_saifi_raw)
    saidi_str = potong_desimal(kontribusi_saidi_raw)
    
    # Akumulasi untuk Total
    saifi_display_sum += float(saifi_str)
    saidi_display_sum += float(saidi_str)
    
    hasil_rows.append({
        "Penyulang": nama,
        "Pelanggan": f"{ni}",
        "Freq": f"{li}",
        "Durasi": label_durasi,
        "SAIFI (2 digit)": saifi_str,
        "SAIDI (2 digit)": saidi_str
    })

df_hasil = pd.DataFrame(hasil_rows)

# --- 4. TAMPILAN TABEL ---
st.subheader(f"1. Rincian Perhitungan ({metode_input})")
st.table(df_hasil)

# --- 5. HASIL TOTAL & EVALUASI ---
st.subheader("2. Total Sistem")

col1, col2 = st.columns(2)

# Format tampilan total (2 desimal)
total_saifi_str = f"{saifi_display_sum:.2f}"
total_saidi_str = f"{saidi_display_sum:.2f}"

with col1:
    st.metric("Total SAIFI", f"{total_saifi_str}", "Kali/Plg/Thn")
    # Evaluasi SAIFI
    if saifi_display_sum <= 3.2:
        st.success("✅ SPLN (3.2): Memenuhi")
    else:
        st.error("❌ SPLN (3.2): Tidak Memenuhi")
        
    if saifi_display_sum <= 1.45:
        st.success("✅ IEEE (1.45): Memenuhi")
    else:
        st.error("❌ IEEE (1.45): Tidak Memenuhi")

with col2:
    st.metric("Total SAIDI", f"{total_saidi_str}", "Jam/Plg/Thn")
    # Evaluasi SAIDI
    if saidi_display_sum <= 21.09:
        st.success("✅ SPLN (21.09): Memenuhi")
    else:
        st.error("❌ SPLN (21.09): Tidak Memenuhi")
        
    if saidi_display_sum <= 2.30:
        st.success("✅ IEEE (2.30): Memenuhi")
    else:
        st.error("❌ IEEE (2.30): Tidak Memenuhi")

st.caption("""
**Catatan:** * **Mode Sesuai Rumus**: Menggunakan input manual (GDN 04 = 15.38, GDN 05 = 12.5) dan pemotongan desimal agar hasil cocok dengan jurnal.
* **Mode Jam & Menit**: Menggunakan konversi waktu yang matematis. Hasil mungkin berbeda dengan jurnal jika data asli jurnal mengandung kesalahan konversi.
""")