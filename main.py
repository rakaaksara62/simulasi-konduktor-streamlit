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

st.set_page_config(page_title="Kalkulator SAIFI SAIDI Presisi", layout="wide")

st.title("🧮 Kalkulator SAIFI & SAIDI (Presisi Jurnal)")
st.markdown("""
Aplikasi ini menggunakan metode **Hitung Total dari Data Mentah** untuk mendapatkan angka yang persis sama dengan kesimpulan Jurnal (14,02 & 11,03),
sambil tetap menampilkan rincian per gardu tanpa pembulatan.
""")

# --- 1. PILIH METODE INPUT ---
st.sidebar.header("⚙️ Pengaturan Input")
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
    st.sidebar.info("Menggunakan durasi desimal sesuai halaman 7 jurnal (GDN 04 = 15.38, GDN 05 = 12.5).")
    data_durasi = {
        "Durasi (Ui)": [15.46, 5.43, 13.25, 15.38, 12.5, 7.00, 6.29]
    }
    df_input = pd.DataFrame({**data_base, **data_durasi})
    df_edit = st.sidebar.data_editor(df_input, num_rows="dynamic")
    
    # Kolom untuk hitung
    df_edit["Durasi Hitung"] = df_edit["Durasi (Ui)"]
    df_edit["Label Durasi"] = df_edit["Durasi (Ui)"].astype(str)

else:
    st.sidebar.info("Menggunakan konversi matematis (Menit/60).")
    data_waktu = {
        "Jam": [15, 5, 13, 38, 5, 7, 6],
        "Menit": [46, 43, 35, 15, 12, 0, 29]
    }
    df_input = pd.DataFrame({**data_base, **data_waktu})
    df_edit = st.sidebar.data_editor(df_input, num_rows="dynamic")
    
    # Hitung Durasi Matematis
    df_edit["Durasi Hitung"] = df_edit["Jam"] + (df_edit["Menit"] / 60)
    df_edit["Label Durasi"] = df_edit["Jam"].astype(str) + "j " + df_edit["Menit"].astype(str) + "m"

total_pelanggan = df_edit["Pelanggan (Ni)"].sum()

# --- 3. PROSES PERHITUNGAN ---

hasil_rows = []

# Variabel Akumulasi MENTAH (Float Presisi Tinggi)
# Kita menjumlahkan pembilang (Ni * λi) dulu baru dibagi total pelanggan di akhir
total_pembilang_saifi = 0
total_pembilang_saidi = 0

# Variabel Akumulasi DISPLAY (Untuk cek penjumlahan tabel)
sum_tabel_saifi = 0
sum_tabel_saidi = 0

for index, row in df_edit.iterrows():
    nama = row["Penyulang"]
    ni = row["Pelanggan (Ni)"]
    li = row["Frekuensi (λi)"]
    ui = row["Durasi Hitung"]
    label_durasi = row["Label Durasi"]
    
    # Hitung Pembilang Mentah
    pembilang_saifi = ni * li
    pembilang_saidi = ni * ui
    
    # Tambahkan ke Total Mentah Sistem
    total_pembilang_saifi += pembilang_saifi
    total_pembilang_saidi += pembilang_saidi
    
    # Hitung Kontribusi Individu (Untuk Tabel)
    kontribusi_saifi = pembilang_saifi / total_pelanggan
    kontribusi_saidi = pembilang_saidi / total_pelanggan
    
    # Potong Desimal untuk Tampilan Tabel
    saifi_str = potong_desimal(kontribusi_saifi)
    saidi_str = potong_desimal(kontribusi_saidi)
    
    # Akumulasi Tabel (Hanya untuk perbandingan)
    sum_tabel_saifi += float(saifi_str)
    sum_tabel_saidi += float(saidi_str)
    
    hasil_rows.append({
        "Penyulang": nama,
        "Pelanggan": f"{ni}",
        "Freq": f"{li}",
        "Durasi": label_durasi,
        "SAIFI (2 digit)": saifi_str,
        "SAIDI (2 digit)": saidi_str
    })

df_hasil = pd.DataFrame(hasil_rows)

# --- 4. HITUNG TOTAL SISTEM DARI DATA MENTAH ---
# Rumus: (Total Frekuensi * Pelanggan) / Total Pelanggan
# Ini menghindari error akibat pemotongan desimal di setiap baris
final_saifi_raw = total_pembilang_saifi / total_pelanggan
final_saidi_raw = total_pembilang_saidi / total_pelanggan

# Potong hasil akhir (Truncate)
final_saifi_display = potong_desimal(final_saifi_raw)
final_saidi_display = potong_desimal(final_saidi_raw)

# --- 5. TAMPILAN ---

st.subheader("1. Rincian Per Gardu (Dipotong)")
st.table(df_hasil)
st.caption(f"**Info:** Jika Anda menjumlahkan kolom tabel di atas secara manual, hasilnya adalah **{sum_tabel_saifi:.2f}** dan **{sum_tabel_saidi:.2f}**. Angka ini kurang akurat karena akumulasi pemotongan desimal.")

st.markdown("---")

st.subheader("2. Total Sistem (Akurat Sesuai Jurnal)")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total SAIFI", f"{final_saifi_display}", "Jurnal: 14.02")
    
    if float(final_saifi_display) <= 3.2:
        st.success("✅ SPLN (3.2): Memenuhi")
    else:
        st.error("❌ SPLN (3.2): Tidak Memenuhi")
        
    if float(final_saifi_display) <= 1.45:
        st.success("✅ IEEE (1.45): Memenuhi")
    else:
        st.error("❌ IEEE (1.45): Tidak Memenuhi")

with col2:
    st.metric("Total SAIDI", f"{final_saidi_display}", "Jurnal: 11.03")
    
    if float(final_saidi_display) <= 21.09:
        st.success("✅ SPLN (21.09): Memenuhi")
    else:
        st.error("❌ SPLN (21.09): Tidak Memenuhi")
        
    if float(final_saidi_display) <= 2.30:
        st.success("✅ IEEE (2.30): Memenuhi")
    else:
        st.error("❌ IEEE (2.30): Tidak Memenuhi")

st.info("""
**Mengapa hasilnya sekarang cocok (14.02 & 11.03)?**
Aplikasi kini menghitung Total Sistem dari **jumlah total gangguan dibagi total pelanggan** secara langsung, baru memotong desimal di akhir.
Ini berbeda dengan sebelumnya yang menjumlahkan angka-angka di tabel yang sudah terpotong (yang menghasilkan 14.00).
Metode langsung ini lebih presisi dan sesuai dengan angka kesimpulan di jurnal.
""")