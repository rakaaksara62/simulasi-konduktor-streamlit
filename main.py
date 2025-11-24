import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Rincian SAIFI SAIDI per Penyulang", layout="wide")

st.title("📊 Rincian Perhitungan SAIFI & SAIDI Per Penyulang")
st.markdown("""
Aplikasi ini membedah perhitungan keandalan per gardu induk (penyulang) untuk mencocokkan hasil 
dengan Naskah Publikasi.
""")

# --- 1. PENGATURAN INPUT DATA ---
st.sidebar.header("⚙️ Input Data & Metode")

# Opsi Metode Hitung Waktu
metode_hitung = st.sidebar.radio(
    "Pilih Metode Konversi Waktu (Untuk SAIDI):",
    ("Matematis Benar (Menit ÷ 60)", "Replikasi Jurnal (Menit jadi Koma)"),
    help="Jurnal menggunakan format '15.46' untuk 15 jam 46 menit, padahal seharusnya 15 + (46/60) jam."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Edit Data Penyulang")

# Data Persis dari Tabel 4.5 [cite: 159] dan Tabel 4.4 [cite: 140]
data_awal = {
    "Penyulang": ["GDN 01", "GDN 02", "GDN 03", "GDN 04", "GDN 05", "WBN 06", "BNL 08"],
    "Pelanggan (N)": [20561, 16329, 14795, 17352, 10204, 13424, 14363],
    "Gangguan (Kali)": [19, 6, 15, 22, 17, 9, 8],
    "Durasi (Jam)": [15, 5, 13, 38, 5, 0, 6],    # Dari kolom Jam Tabel 4.4
    "Durasi (Menit)": [46, 43, 35, 15, 12, 7, 29] # Dari kolom Menit Tabel 4.4
}

df_input = pd.DataFrame(data_awal)
df_edit = st.sidebar.data_editor(df_input, num_rows="dynamic")

# Hitung Total Pelanggan Sistem
total_pelanggan = df_edit["Pelanggan (N)"].sum()

# --- 2. PROSES PERHITUNGAN ---

# A. Hitung Durasi dalam Jam (Desimal)
if metode_hitung == "Matematis Benar (Menit ÷ 60)":
    # 46 menit = 0.76 jam
    df_edit["Durasi Desimal (Jam)"] = df_edit["Durasi (Jam)"] + (df_edit["Durasi (Menit)"] / 60)
else:
    # Mode Jurnal: 46 menit = .46 (Sesuai rumus di halaman 7 )
    df_edit["Durasi Desimal (Jam)"] = df_edit["Durasi (Jam)"] + (df_edit["Durasi (Menit)"] / 100)

# B. Hitung Kontribusi SAIFI per Penyulang
# Rumus Jurnal Hal 6[cite: 170]: (Frekuensi x PelangganPenyulang) / TotalPelangganSistem
df_edit["SAIFI (Kontribusi)"] = (df_edit["Gangguan (Kali)"] * df_edit["Pelanggan (N)"]) / total_pelanggan

# C. Hitung Kontribusi SAIDI per Penyulang
# Rumus Jurnal Hal 7: (Durasi x PelangganPenyulang) / TotalPelangganSistem
df_edit["SAIDI (Kontribusi)"] = (df_edit["Durasi Desimal (Jam)"] * df_edit["Pelanggan (N)"]) / total_pelanggan

# --- 3. MENAMPILKAN HASIL RINCIAN ---

st.subheader(f"1. Tabel Rincian Perhitungan (Total Pelanggan: {total_pelanggan:,.0f})")
st.markdown("Tabel ini merincikan nilai indeks yang disumbangkan oleh setiap penyulang, sesuai **Tabel 4.6** [cite: 217] dan **Tabel 4.10** [cite: 266] di jurnal.")

# Format tampilan tabel agar rapi (2 angka di belakang koma)
tabel_hasil = df_edit[["Penyulang", "Pelanggan (N)", "Gangguan (Kali)", "Durasi Desimal (Jam)", "SAIFI (Kontribusi)", "SAIDI (Kontribusi)"]].copy()

# Tampilkan Tabel
st.dataframe(
    tabel_hasil.style.format({
        "Pelanggan (N)": "{:,.0f}",
        "Durasi Desimal (Jam)": "{:.4f}",
        "SAIFI (Kontribusi)": "{:.2f}",
        "SAIDI (Kontribusi)": "{:.2f}"
    }), 
    use_container_width=True
)

# --- 4. HASIL AKHIR & PERBANDINGAN ---

saifi_total = df_edit["SAIFI (Kontribusi)"].sum()
saidi_total = df_edit["SAIDI (Kontribusi)"].sum()

st.subheader("2. Hasil Total Sistem")
col1, col2 = st.columns(2)

with col1:
    st.info(f"**SAIFI Total: {saifi_total:.2f}** kali/pelanggan/tahun")
    if metode_hitung == "Replikasi Jurnal (Menit jadi Koma)":
        st.caption("Hasil ini akan mendekati angka '14.02' di Tabel 4.6 jurnal[cite: 218].")
    else:
        st.caption("Hasil perhitungan matematis yang presisi.")

with col2:
    st.info(f"**SAIDI Total: {saidi_total:.2f}** jam/pelanggan/tahun")
    if metode_hitung == "Replikasi Jurnal (Menit jadi Koma)":
        st.caption("Hasil ini akan mendekati angka '11.03' di Tabel 4.10 jurnal[cite: 268].")
    else:
        st.caption("Perhatikan: Nilai ini lebih tinggi karena 46 menit dihitung 0,76 jam, bukan 0,46.")

# --- 5. VISUALISASI KONTRIBUSI ---
st.subheader("3. Grafik Kontribusi Penyulang")
tab_a, tab_b = st.tabs(["Kontribusi SAIFI", "Kontribusi SAIDI"])

with tab_a:
    fig_saifi = px.bar(df_edit, x="Penyulang", y="SAIFI (Kontribusi)", 
                       title="Penyumbang Frekuensi Pemadaman Tertinggi", text_auto='.2f')
    st.plotly_chart(fig_saifi, use_container_width=True)

with tab_b:
    fig_saidi = px.bar(df_edit, x="Penyulang", y="SAIDI (Kontribusi)", 
                       title="Penyumbang Durasi Pemadaman Terlama", text_auto='.2f')
    st.plotly_chart(fig_saidi, use_container_width=True)