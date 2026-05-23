import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Power-Institutional Map Analysis (PIOM)")

# ==========================================
# PROFIL PENGEMBANG DI SIDEBAR
# ==========================================
st.sidebar.image("yuhka.jpg", caption="Yuhka Sundaya", use_container_width=True)
st.sidebar.markdown("### **Dikembangkan oleh:**")
st.sidebar.markdown("#### **Yuhka Sundaya**")
st.sidebar.caption("Ekonomi Pembangunan Unisba @2026")
st.sidebar.write("---")

# ==========================================
# LOGIKA STRUKTUR DATA (FIXED RERUN BUG)
# ==========================================
if "actors" not in st.session_state:
    st.session_state.actors = []

# Daftarkan semua nama matriks relasi
matrix_names = ["matrix_collaboration", "matrix_influence", "matrix_conflict", "matrix_power"]

# Fungsi sinkronisasi ukuran matriks hanya jika jumlah aktor berubah
def sync_matrices():
    actors = st.session_state.actors
    n = len(actors)
    
    # 1. Sinkronisasi Matriks Atribut
    if "matrix_atribut" not in st.session_state:
        st.session_state.matrix_atribut = pd.DataFrame(
            {"Tipe Lembaga": ["Formal"] * n, "Peran Utama": ["Regulator"] * n},
            index=actors
        )
    else:
        old_attr = st.session_state.matrix_atribut
        new_attr = pd.DataFrame({"Tipe Lembaga": ["Formal"] * n, "Peran Utama": ["Regulator"] * n}, index=actors)
        for r in old_attr.index:
            if r in new_attr.index:
                new_attr.loc[r] = old_attr.loc[r]
        st.session_state.matrix_atribut = new_attr

    # 2. Sinkronisasi Matriks Relasional (CICP)
    for name in matrix_names:
        # Tentukan default value berdasarkan jenis matriks
        default_val = 0
        
        if name not in st.session_state:
            st.session_state[name] = pd.DataFrame(np.full((n, n), default_val), index=actors, columns=actors)
        else:
            old_df = st.session_state[name]
            # Jika susunan aktor berubah, buat rangka baru dan salin data lama
            if not old_df.index.equals(pd.Index(actors)):
                new_df = pd.DataFrame(default_val, index=actors, columns=actors)
                for r in old_df.index:
                    for c in old_df.columns:
                        if r in new_df.index and c in new_df.columns:
                            new_df.loc[r, c] = old_df.loc[r, c]
                st.session_state[name] = new_df

# Jalankan sinkronisasi data awal
sync_matrices()

# ==========================================
# 2. MANAJEMEN AKTOR (SIDEBAR)
# ==========================================
st.sidebar.header("1. Manajemen Aktor")
with st.sidebar.form("add_actor_form", clear_on_submit=True):
    new_actor = st.text_input("Nama Aktor Baru:")
    submit_actor = st.form_submit_button("Tambah Aktor")
    if submit_actor and new_actor:
        if new_actor not in st.session_state.actors:
            st.session_state.actors.append(new_actor)
            sync_matrices()  # Sinkronisasikan struktur matriks saat aktor ditambah
            st.rerun()

st.sidebar.write("**Daftar Aktor Aktif:**")
if len(st.session_state.actors) == 0:
    st.sidebar.info("Belum ada aktor. Silakan tambah di atas.")
else:
    for act in st.session_state.actors:
        st.sidebar.markdown(f"- {act}")

# ==========================================
# 3. ANTARMUKA NAVIGASI MATRIKS UTAMA
# ==========================================
tabs = st.tabs([
    "2. Matriks Aktor (Atribut)", 
    "3. Matriks Collaboration", 
    "4. Matriks Influence", 
    "5. Matriks Conflict", 
    "6. Matriks Power",
    "7. Analisis Power & Public Choice"
])

cicp_full_options = list(range(-5, 6))
cicp_positive_options = list(range(0, 6))
cicp_negative_options = list(range(-5, 1))

if len(st.session_state.actors) == 0:
    for i in range(6):
        with tabs[i]:
            st.info("Silakan masukkan minimal satu nama aktor di menu samping (sidebar) terlebih dahulu.")
else:
    # --- TAB 2: MATRIKS AKTOR (ATRIBUT) ---
    with tabs[0]:
        st.subheader("Matriks Profil & Atribut Aktor")
        edited_attr = st.data_editor(st.session_state.matrix_atribut, use_container_width=True, key="editor_attr")
        st.session_state.matrix_atribut = edited_attr

    # --- TAB 3: COLLABORATION ---
    with tabs[1]:
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        df_collab = st.session_state.matrix_collaboration
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in df_collab.columns}
        edited_collab = st.data_editor(df_collab, column_config=config_collab, use_container_width=True, key="editor_collab")
        st.session_state.matrix_collaboration = edited_collab

    # --- TAB 4: INFLUENCE ---
    with tabs[2]:
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        df_inf = st.session_state.matrix_influence
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_inf.columns}
        edited_inf = st.data_editor(df_inf, column_config=config_inf, use_container_width=True, key="editor_inf")
        st.session_state.matrix_influence = edited_inf

    # --- TAB 5: CONFLICT ---
    with tabs[3]:
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        df_conf = st.session_state.matrix_conflict
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in df_conf.columns}
        edited_conf = st.data_editor(df_conf, column_config=config_conf, use_container_width=True, key="editor_conf")
        st.session_state.matrix_conflict = edited_conf

    # --- TAB 6: POWER ---
    with tabs[4]:
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        df_pow = st.session_state.matrix_power
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_pow.columns}
        edited_pow = st.data_editor(df_pow, column_config=config_pow, use_container_width=True, key="editor_pow")
        st.session_state.matrix_power = edited_pow

    # --- TAB 7: OUTPUT ANALISIS PUBLIC CHOICE (BUCHANAN-TULLOCK) ---
    with tabs[5]:
        st.subheader("Analisis Peta Kekuasaan & Pilihan Publik (Public Choice)")
        st.markdown("Mengacu pada kerangka pemikiran **James Buchanan & Gordon Tullock** (*The Calculus of Consent*), grafik di bawah ini memetakan posisi aktor berdasarkan akumulasi Otoritas Formal Kekuasaan (Power) vs Kapasitas Lobi/Sektoral (Influence).")
        
        m_inf = st.session_state.matrix_influence
        m_pow = st.session_state.matrix_power
        
        summary_data = []
        for actor in st.session_state.actors:
            mean_inf_out = m_inf.loc[actor].mean()
            mean_pow_out = m_pow.loc[actor].mean()
            
            if mean_inf_out >= 0 and mean_pow_out >= 0:
                kuadran = "Kuadran I: The Ruling Coalition (Pusat Kendali Politik)"
            elif mean_inf_out >= 0 and mean_pow_out < 0:
                kuadran = "Kuadran II: The Rent-Seekers / Lobbyists (Pemburu Rente)"
            elif mean_inf_out < 0 and mean_pow_out >= 0:
                kuadran = "Kuadran III: The Constitutional Agents (Birokrat Murni)"
            else:
                kuadran = "Kuadran IV: The Disfranchised Public (Publik Marjinal)"
                
            summary_data.append({
                "Aktor": actor,
                "Influence Score (X)": round(mean_inf_out, 2),
                "Power Score (Y)": round(mean_pow_out, 2),
                "Tipologi Kelembagaan": kuadran
            })
            
        df_summary = pd.DataFrame(summary_data)
        
        st.write("**Tabel Indeks Agregat Aktor:**")
        st.dataframe(df_summary, use_container_width=True)
        
        st.write("---")
        st.write("**Grafik Peta Kuadran Ekonomi Politik:**")
        
        fig = px.scatter(
            df_summary, 
            x="Influence Score (X)", 
            y="Power Score (Y)", 
            text="Aktor",
            color="Tipologi Kelembagaan",
            range_x=[-5.5, 5.5],
            range_y=[-5.5, 5.5],
            labels={"Influence Score (X)": "Kapasitas Pengaruh & Lobi (Influence)", "Power Score (Y)": "Otoritas Konstitusional (Power)"},
            title="Peta Kuadran Aktor (Tradisi Virginia School of Public Choice)"
        )
        
        fig.add_shape(type="line", x0=-5.5, y0=0, x1=5.5, y1=0, line=dict(color="gray", width=1, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=-5.5, x1=0, y1=5.5, line=dict(color="gray", width=1, dash="dash"))
        
        fig.update_traces(marker=dict(size=12), textposition='top center')
        fig.update_layout(height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        
        st.plotly_chart(fig, use_container_width=True)
