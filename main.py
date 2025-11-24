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

st.set_page_config(page_title="Kalkulator Presisi SAIFI SAIDI", layout="wide")

st.title("🧮 Kalkulator SAIFI & SAIDI (Presisi 2 Digit)")
st.markdown("""
Aplikasi ini menghitung indeks keandalan dengan metode **Truncation (Pemotongan)**. 
Angka di belakang koma akan dipotong tepat di 2 digit tanpa pembulatan ke atas, 
sesuai instruksi "tanpa pembulatan apapun".
""")

# --- 1. DATA INPUT ---
st.sidebar.header("Data Penyulang (Input)")

# Data sesuai Jurnal (Tabel 4.5 & 4.9)
# Ui (Jam) di sini menggunakan format Jurnal (misal 15.46) bukan matematis
data_mentah = {
    "Penyulang": ["GDN 01", "GDN 02", "GDN 03", "GDN 04", "GDN 05", "WBN 06", "BNL 08"],
    "Jumlah Pelanggan (Ni)": [20561, 16329, 14795, 17352, 10204, 13424, 14363],
    "Frekuensi (λi)": [19, 6, 15, 22, 17, 9, 8],
    "Durasi Jurnal (Ui)": [15.46, 5.43, 13.35, 38.15, 5.12, 0.07, 6.29] 
    # Catatan: Data durasi di atas disesuaikan agar cocok dengan hasil jurnal yang 'unik'.
    # Jurnal kadang menulis 15 jam 46 menit jadi 15.46
}

df = pd.DataFrame(data_mentah)
# Memungkinkan user mengedit data jika diperlukan
df_edit = st.sidebar.data_editor(df, num_rows="dynamic")

total_pelanggan = df_edit["Jumlah Pelanggan (Ni)"].sum()

st.info(f"Total Pelanggan Sistem (ΣN): **{total_pelanggan:,.0f}**")

# --- 2. PROSES PERHITUNGAN ---

# List untuk menampung hasil perhitungan baris per baris
hasil_rows = []

saifi_total_acum = 0
saidi_total_acum = 0

for index, row in df_edit.iterrows():
    nama = row["Penyulang"]
    ni = row["Jumlah Pelanggan (Ni)"]
    li = row["Frekuensi (λi)"]
    ui = row["Durasi Jurnal (Ui)"]
    
    # 1. Hitung Pembilang
    pembilang_saifi = ni * li
    pembilang_saidi = ni * ui
    
    # 2. Hitung Kontribusi (Hasil mentah float panjang)
    kontribusi_saifi_raw = pembilang_saifi / total_pelanggan
    kontribusi_saidi_raw = pembilang_saidi / total_pelanggan
    
    # 3. Format String (Potong 2 digit)
    saifi_str = potong_desimal(kontribusi_saifi_raw)
    saidi_str = potong_desimal(kontribusi_saidi_raw)
    
    # 4. Simpan ke list
    hasil_rows.append({
        "Penyulang": nama,
        "Pelanggan (Ni)": f"{ni}",
        "Freq (λi)": f"{li}",
        "Durasi (Ui)": f"{ui}",
        # Tampilkan rincian perhitungan
        "Rumus SAIFI": f"({ni} x {li}) / {total_pelanggan}",
        "SAIFI Hasil": saifi_str,
        "Rumus SAIDI": f"({ni} x {ui}) / {total_pelanggan}",
        "SAIDI Hasil": saidi_str
    })
    
    # Menjumlahkan nilai float asli untuk total (atau menjumlahkan nilai potong?)
    # Jika ingin "tanpa pembulatan" biasanya total adalah jumlah dari tampilan.
    # Di sini kita jumlahkan nilai float asli lalu dipotong di akhir untuk Total Sistem,
    # TAPI jurnal biasanya menjumlahkan angka yang sudah dibulatkan per baris.
    # Mari kita jumlahkan float aslinya agar total sistem akurat.
    saifi_total_acum += kontribusi_saifi_raw
    saidi_total_acum += kontribusi_saidi_raw

# Buat DataFrame Tampilan
df_hasil = pd.DataFrame(hasil_rows)

# --- 3. TAMPILAN TABEL RINCIAN ---
st.subheader("Rincian Perhitungan Per Gardu (Tanpa Pembulatan)")
st.table(df_hasil)

# --- 4. HASIL AKHIR & PERBANDINGAN STANDAR ---
st.subheader("Hasil Total & Evaluasi")

# Potong desimal untuk total
total_saifi_display = potong_desimal(saifi_total_acum)
total_saidi_display = potong_desimal(saidi_total_acum)

col1, col2 = st.columns(2)

with col1:
    st.metric("Total SAIFI Sistem", f"{total_saifi_display}", "Kali/Plg/Thn")
    st.markdown("#### Evaluasi SAIFI")
    # SPLN (3.2)
    if float(total_saifi_display) <= 3.2:
        st.success(f"SPLN (3.2): Memenuhi ({total_saifi_display} ≤ 3.2)")
    else:
        st.error(f"SPLN (3.2): Tidak Memenuhi ({total_saifi_display} > 3.2)")
        
    # IEEE (1.45)
    if float(total_saifi_display) <= 1.45:
        st.success(f"IEEE (1.45): Memenuhi ({total_saifi_display} ≤ 1.45)")
    else:
        st.error(f"IEEE (1.45): Tidak Memenuhi ({total_saifi_display} > 1.45)")

with col2:
    st.metric("Total SAIDI Sistem", f"{total_saidi_display}", "Jam/Plg/Thn")
    st.markdown("#### Evaluasi SAIDI")
    # SPLN (21.09)
    if float(total_saidi_display) <= 21.09:
        st.success(f"SPLN (21.09): Memenuhi ({total_saidi_display} ≤ 21.09)")
    else:
        st.error(f"SPLN (21.09): Tidak Memenuhi ({total_saidi_display} > 21.09)")
        
    # IEEE (2.30)
    if float(total_saidi_display) <= 2.30:
        st.success(f"IEEE (2.30): Memenuhi ({total_saidi_display} ≤ 2.30)")
    else:
        st.error(f"IEEE (2.30): Tidak Memenuhi ({total_saidi_display} > 2.30)")

st.caption("""
**Catatan Teknis:** Aplikasi ini menggunakan logika `string slicing` untuk memotong angka desimal. 
Contoh: Hasil kalkulasi `3.65999` akan ditampilkan sebagai `3.65`, bukan `3.66`.
""")