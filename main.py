import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("⚡ Simulasi Pengaruh Penggantian Konduktor 20 kV terhadap Drop Tegangan dan Efisiensi Energi")
st.write("Berdasarkan Jurnal: *Analisis Pengaruh Penggantian Konduktor pada SUTM 20 kV terhadap Drop Tegangan di PT. PLN UP3 Bangkinang*")

st.sidebar.header("🔧 Input Parameter")

# Input umum
I = st.sidebar.number_input("Arus Beban (A)", 50, 1000, 200)
L = st.sidebar.number_input("Panjang Saluran (km)", 1.0, 50.0, 15.0)
V_nominal = 20.0  # kV nominal

st.sidebar.markdown("### Sebelum Penggantian")
R_before = st.sidebar.number_input("Resistansi Konduktor Sebelum (Ω/km)", 0.01, 1.0, 0.206)

st.sidebar.markdown("### Setelah Penggantian")
R_after = st.sidebar.number_input("Resistansi Konduktor Sesudah (Ω/km)", 0.01, 1.0, 0.135)

# Data pelanggan & gangguan
st.sidebar.markdown("### Data Pelanggan & Gangguan")
N_total = st.sidebar.number_input("Total Pelanggan", 1, 50000, 10000)
U1 = st.sidebar.number_input("Durasi Gangguan 1 (jam)", 0.0, 10.0, 2.0)
N1 = st.sidebar.number_input("Jumlah Pelanggan Terdampak Gangguan 1", 0, 10000, 1000)
U2 = st.sidebar.number_input("Durasi Gangguan 2 (jam)", 0.0, 10.0, 1.5)
N2 = st.sidebar.number_input("Jumlah Pelanggan Terdampak Gangguan 2", 0, 10000, 2000)
U3 = st.sidebar.number_input("Durasi Gangguan 3 (jam)", 0.0, 10.0, 3.0)
N3 = st.sidebar.number_input("Jumlah Pelanggan Terdampak Gangguan 3", 0, 10000, 1500)

# Fungsi perhitungan
def drop_voltage(I, R, L):
    return 2 * I * R * L / 1000  # kV

def power_loss(I, R, L):
    return (I**2 * R * L )/100
    

def reliability_index(U1, N1, U2, N2, U3, N3, N_total):
    SAIDI = (U1*N1 + U2*N2 + U3*N3) / N_total
    SAIFI = (N1 + N2 + N3) / N_total
    return SAIDI, SAIFI

# Hitung hasil
Vdrop_before = drop_voltage(I, R_before, L)
Ploss_before = power_loss(I, R_before, L)
Vdrop_after = drop_voltage(I, R_after, L)
Ploss_after = power_loss(I, R_after, L)
SAIDI_before, SAIFI_before = reliability_index(U1, N1, U2, N2, U3, N3, N_total)

# Asumsi setelah penggantian gangguan menurun 40%
SAIDI_after = SAIDI_before * 0.4
SAIFI_after = SAIFI_before * 0.6

# Tabel hasil
data = {
    "Parameter": ["Drop Tegangan (kV)", "Rugi Daya (kW)", "SAIDI (jam/pelanggan)", "SAIFI (frekuensi/pelanggan)"],
    "Sebelum": [Vdrop_before, Ploss_before, SAIDI_before, SAIFI_before],
    "Sesudah": [Vdrop_after, Ploss_after, SAIDI_after, SAIFI_after],
}
df = pd.DataFrame(data)

st.subheader("📊 Hasil Simulasi")
st.dataframe(df.style.format(
    subset=["Sebelum", "Sesudah"], 
    formatter=lambda x: "{:.3f}".format(x).rstrip('0').rstrip('.')
))

# Tambahkan penjelasan SAIDI dan SAIFI
st.markdown("""
**Keterangan:**
- **SAIDI (System Average Interruption Duration Index)** adalah **rata-rata durasi gangguan listrik per pelanggan** dalam satuan jam/pelanggan.  
  Semakin kecil nilainya, semakin andal sistem distribusi karena pelanggan mengalami gangguan lebih singkat.
- **SAIFI (System Average Interruption Frequency Index)** adalah **rata-rata frekuensi gangguan listrik per pelanggan** dalam satuan kali/pelanggan.  
  Nilai SAIFI yang kecil menandakan sistem lebih stabil dan pelanggan lebih jarang mengalami pemadaman listrik.
""")

# Grafik perbandingan
df_plot = df.set_index("Parameter")

# Ambil warna tema dengan fallback aman
bg_color = st.get_option("theme.backgroundColor") or "#0E1117"
text_color = st.get_option("theme.textColor") or "#FAFAFA"

fig, ax = plt.subplots(facecolor=bg_color)
ax.set_facecolor(bg_color)

df_plot.plot(kind='bar', ax=ax, color=["tomato", "skyblue"])

ax.set_title("Perbandingan Sebelum & Sesudah Penggantian Konduktor", color=text_color)
ax.set_ylabel("Nilai", color=text_color)
ax.tick_params(colors=text_color)
ax.yaxis.label.set_color(text_color)
ax.xaxis.label.set_color(text_color)

st.pyplot(fig)


# Interpretasi hasil
improvement_v = (Vdrop_before - Vdrop_after) / Vdrop_before * 100
improvement_p = (Ploss_before - Ploss_after) / Ploss_before * 100

st.markdown(f"""
### 📈 Interpretasi:
- Penurunan **drop tegangan** sebesar **{improvement_v:.1f}%**
- Penurunan **rugi daya** sebesar **{improvement_p:.1f}%**
- Peningkatan efisiensi distribusi dan kualitas tegangan pada ujung saluran
""")

# ----------------------------------------------------------------
# Footer: identitas kelompok
# ----------------------------------------------------------------
st.markdown("""
---
### 👥 **By Kelompok Distribusi 20kV**
- **Raka Khairan Taqi Aksara**  
- **Kaisya Ruby Edya**  
- **Nita Nirmala**
""")
