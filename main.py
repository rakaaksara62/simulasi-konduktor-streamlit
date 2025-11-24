import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Kalkulator SAIFI & SAIDI", layout="wide")

st.title("⚡ Analisis Keandalan: SAIFI & SAIDI")
st.markdown("""
Aplikasi ini berfokus menghitung indeks **SAIFI** (Frekuensi Pemadaman) dan **SAIDI** (Durasi Pemadaman) 
berdasarkan data penyulang, serta mengevaluasinya terhadap standar **SPLN** dan **IEEE**.
Data awal diambil dari studi kasus Rayon Sedayu (2017).
""")

# --- SIDEBAR: INPUT DATA ---
st.sidebar.header("🎛️ Input Data Gangguan")
st.sidebar.write("Sesuaikan data di bawah ini:")

# Data Awal (Sesuai Naskah Publikasi Tabel 4.5 & 4.9)
default_data = {
    "Penyulang": ["GDN 01", "GDN 02", "GDN 03", "GDN 04", "GDN 05", "WBN 06", "BNL 08"],
    "Jumlah Pelanggan (Ni)": [20561, 16329, 14795, 17352, 10204, 13424, 14363],
    "Frekuensi Gangguan (λi)": [19, 6, 15, 22, 17, 9, 8],
    "Durasi Total (Ui) [Jam]": [15.77, 5.72, 13.58, 38.25, 5.2, 0.12, 6.48] 
}

df = pd.DataFrame(default_data)

# Widget Editor Data
edited_df = st.sidebar.data_editor(df, num_rows="dynamic")

# --- BAGIAN 1: PERHITUNGAN INDEKS ---
st.header("1. Hasil Perhitungan Sistem")

# Rumus Total Pelanggan
total_pelanggan = edited_df["Jumlah Pelanggan (Ni)"].sum()

# Kalkulasi Kontribusi per Penyulang
metrics_df = edited_df.copy()
metrics_df["Ni x λi"] = metrics_df["Jumlah Pelanggan (Ni)"] * metrics_df["Frekuensi Gangguan (λi)"]
metrics_df["Ni x Ui"] = metrics_df["Jumlah Pelanggan (Ni)"] * metrics_df["Durasi Total (Ui) [Jam]"]

# Perhitungan SAIFI & SAIDI Sistem (Rumus Total)
# SAIFI = Total (Ni * λi) / Total Pelanggan
# SAIDI = Total (Ni * Ui) / Total Pelanggan
saifi_sistem = metrics_df["Ni x λi"].sum() / total_pelanggan
saidi_sistem = metrics_df["Ni x Ui"].sum() / total_pelanggan

# Tampilkan Metrics Utama
col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan", f"{total_pelanggan:,.0f}")
col2.metric("SAIFI Sistem", f"{saifi_sistem:.2f}", "Kali/Pelanggan/Tahun")
col3.metric("SAIDI Sistem", f"{saidi_sistem:.2f}", "Jam/Pelanggan/Tahun")

st.markdown("---")

# --- BAGIAN 2: EVALUASI STANDAR ---
st.header("2. Evaluasi Terhadap Standar")

col_spln, col_ieee = st.columns(2)

# Standar SPLN 68-2: 1986 [Sumber: Dokumen Hal 6 & 8]
with col_spln:
    st.subheader("Standar SPLN 68-2: 1986")
    st.caption("Target: SAIFI ≤ 3.2 | SAIDI ≤ 21.09")
    
    # Logika Status
    status_saifi_spln = "✅ MEMENUHI" if saifi_sistem <= 3.2 else "❌ TIDAK MEMENUHI"
    status_saidi_spln = "✅ MEMENUHI" if saidi_sistem <= 21.09 else "❌ TIDAK MEMENUHI"
    
    st.write(f"**SAIFI:** {status_saifi_spln} (Batas: 3.2)")
    st.write(f"**SAIDI:** {status_saidi_spln} (Batas: 21.09)")

# Standar IEEE Std 1366-2003 [Sumber: Dokumen Hal 7 & 9]
with col_ieee:
    st.subheader("Standar IEEE Std 1366-2003")
    st.caption("Target: SAIFI ≤ 1.45 | SAIDI ≤ 2.30")
    
    # Logika Status
    status_saifi_ieee = "✅ MEMENUHI" if saifi_sistem <= 1.45 else "❌ TIDAK MEMENUHI"
    status_saidi_ieee = "✅ MEMENUHI" if saidi_sistem <= 2.30 else "❌ TIDAK MEMENUHI"
    
    st.write(f"**SAIFI:** {status_saifi_ieee} (Batas: 1.45)")
    st.write(f"**SAIDI:** {status_saidi_ieee} (Batas: 2.30)")

# --- BAGIAN 3: VISUALISASI ---
st.subheader("Grafik Perbandingan")

tab1, tab2 = st.tabs(["Grafik SAIFI", "Grafik SAIDI"])

with tab1:
    fig_saifi = go.Figure()
    # Bar Nilai Aktual
    fig_saifi.add_trace(go.Bar(
        x=["Sistem Aktual"], 
        y=[saifi_sistem], 
        name="Nilai Aktual", 
        marker_color='#3498db',
        text=[f"{saifi_sistem:.2f}"],
        textposition='auto'
    ))
    # Garis Batas SPLN
    fig_saifi.add_hline(y=3.2, line_dash="dash", line_color="green", annotation_text="Batas SPLN (3.2)")
    # Garis Batas IEEE
    fig_saifi.add_hline(y=1.45, line_dash="dash", line_color="red", annotation_text="Batas IEEE (1.45)")
    
    fig_saifi.update_layout(title="Posisi SAIFI Aktual vs Standar", yaxis_title="Kali/Tahun")
    st.plotly_chart(fig_saifi, use_container_width=True)

with tab2:
    fig_saidi = go.Figure()
    # Bar Nilai Aktual
    fig_saidi.add_trace(go.Bar(
        x=["Sistem Aktual"], 
        y=[saidi_sistem], 
        name="Nilai Aktual", 
        marker_color='#e67e22',
        text=[f"{saidi_sistem:.2f}"],
        textposition='auto'
    ))
    # Garis Batas SPLN
    fig_saidi.add_hline(y=21.09, line_dash="dash", line_color="green", annotation_text="Batas SPLN (21.09)")
    # Garis Batas IEEE
    fig_saidi.add_hline(y=2.30, line_dash="dash", line_color="red", annotation_text="Batas IEEE (2.30)")
    
    fig_saidi.update_layout(title="Posisi SAIDI Aktual vs Standar", yaxis_title="Jam/Tahun")
    st.plotly_chart(fig_saidi, use_container_width=True)