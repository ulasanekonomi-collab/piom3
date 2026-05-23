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
# 1. INISIALISASI STATE UTAMA (AMANKAN MEMORI)
# ==========================================
if "actors" not in st.session_state:
    st.session_state.actors = []

matrix_keys = ["matrix_atribut", "matrix_collaboration", "matrix_influence", "matrix_conflict", "matrix_power"]

def create_empty_df(matrix_name, actors):
    n = len(actors)
    if matrix_name == "matrix_atribut":
        return pd.DataFrame({"Tipe Lembaga": ["Formal"] * n, "Peran Utama": ["Regulator"] * n}, index=actors)
    else:
        return pd.DataFrame(0, index=actors, columns=actors)

def update_matrix_structure():
    actors = st.session_state.actors
    for key in matrix_keys:
        if key not in st.session_state:
            st.session_state[key] = create_empty_df(key, actors)
        else:
            old_df = st.session_state[key]
            new_df = create_empty_df(key, actors)
            for r in old_df.index:
                if r in new_df.index:
                    if key == "matrix_atribut":
                        new_df.loc[r] = old_df.loc[r]
                    else:
                        for c in old_df.columns:
                            if c in new_df.columns:
                                new_df.loc[r, c] = old_df.loc[r, c]
            st.session_state[key] = new_df

if len(st.session_state.actors) > 0 and "matrix_power" not in st.session_state:
    update_matrix_structure()

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
            update_matrix_structure()
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

def save_changes(key_name, editor_state_name):
    if editor_state_name in st.session_state and st.session_state[editor_state_name]["edited_rows"]:
        updates = st.session_state[editor_state_name]["edited_rows"]
        df = st.session_state[key_name]
        for row_idx, col_data in updates.items():
            row_name = df.index[int(row_idx)] if isinstance(row_idx, (int, str)) and int(row_idx) < len(df) else df.index[row_idx]
            for col_name, val in col_data.items():
                df.loc[row_name, col_name] = val
        st.session_state[key_name] = df

if len(st.session_state.actors) == 0:
    for i in range(6):
        with tabs[i]:
            st.info("Silakan masukkan minimal satu nama aktor di menu samping (sidebar) terlebih dahulu.")
else:
    # --- TAB 2: MATRIKS ATRIBUT ---
    with tabs[0]:
        st.subheader("Matriks Profil & Atribut Aktor")
        edited_attr = st.data_editor(
            st.session_state.matrix_atribut, use_container_width=True, key="editor_attr_state",
            on_change=save_changes, args=("matrix_atribut", "editor_attr_state")
        )
        st.session_state.matrix_atribut = edited_attr

    # --- TAB 3: COLLABORATION ---
    with tabs[1]:
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        df_collab = st.session_state.matrix_collaboration
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in df_collab.columns}
        edited_collab = st.data_editor(
            df_collab, column_config=config_collab, use_container_width=True, key="editor_collab_state",
            on_change=save_changes, args=("matrix_collaboration", "editor_collab_state")
        )
        st.session_state.matrix_collaboration = edited_collab

    # --- TAB 4: INFLUENCE ---
    with tabs[2]:
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        df_inf = st.session_state.matrix_influence
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_inf.columns}
        edited_inf = st.data_editor(
            df_inf, column_config=config_inf, use_container_width=True, key="editor_inf_state",
            on_change=save_changes, args=("matrix_influence", "editor_inf_state")
        )
        st.session_state.matrix_influence = edited_inf

    # --- TAB 5: CONFLICT ---
    with tabs[3]:
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        df_conf = st.session_state.matrix_conflict
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in df_conf.columns}
        edited_conf = st.data_editor(
            df_conf, column_config=config_conf, use_container_width=True, key="editor_conf_state",
            on_change=save_changes, args=("matrix_conflict", "editor_conf_state")
        )
        st.session_state.matrix_conflict = edited_conf

    # --- TAB 6: POWER ---
    with tabs[4]:
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        df_pow = st.session_state.matrix_power
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_pow.columns}
        edited_pow = st.data_editor(
            df_pow, column_config=config_pow, use_container_width=True, key="editor_pow_state",
            on_change=save_changes, args=("matrix_power", "editor_pow_state")
        )
        st.session_state.matrix_power = edited_pow

    # --- TAB 7: OUTPUT ANALISIS PUBLIC CHOICE (REKALIBRASI SUM-DEGREE) ---
    with tabs[5]:
        st.subheader("Analisis Peta Kekuasaan & Pilihan Publik (Public Choice)")
        st.markdown("Mengacu pada kerangka pemikiran **James Buchanan & Gordon Tullock** (*The Calculus of Consent*), grafik memetakan posisi aktor berdasarkan akumulasi Total Otoritas Formal (Power) vs Kapasitas Lobi/Sektoral (Influence).")
        
        m_inf = st.session_state.matrix_influence
        m_pow = st.session_state.matrix_power
        
        summary_data = []
        for actor in st.session_state.actors:
            # Menggunakan .sum() agar akumulasi nilainya mencerminkan bobot total dominasi relasi
            sum_inf_out = m_inf.loc[actor].sum()
            sum_pow_out = m_pow.loc[actor].sum()
            
            # Pengkondisian kuadran berbasis nilai total kumulatif 0
            if sum_inf_out > 0 and sum_pow_out > 0:
                kuadran = "Kuadran I: The Ruling Coalition (Pusat Kendali Politik)"
            elif sum_inf_out >= 0 and sum_pow_out <= 0:
                kuadran = "Kuadran II: The Rent-Seekers / Lobbyists (Pemburu Rente)"
            elif sum_inf_out <= 0 and sum_pow_out > 0:
                kuadran = "Kuadran III: The Constitutional Agents (Birokrat Murni)"
            else:
                kuadran = "Kuadran IV: The Disfranchised Public (Publik Marjinal)"
                
            summary_data.append({
                "Aktor": actor,
                "Total Influence (X)": int(sum_inf_out),
                "Total Power (Y)": int(sum_pow_out),
                "Tipologi Kelembagaan": kuadran
            })
            
        df_summary = pd.DataFrame(summary_data)
        
        st.write("**Tabel Indeks Agregat Ekonomi Politik:**")
        st.dataframe(df_summary, use_container_width=True)
        
        st.write("---")
        st.write("**Grafik Peta Kuadran Ekonomi Politik (CICP-Model):**")
        
        # Batas dinamis grafik menyesuaikan jumlah aktor agar grid visualnya proporsional
        max_bound = max(abs(df_summary["Total Influence (X)"].max()), abs(df_summary["Total Influence (X)"].min()),
                        abs(df_summary["Total Power (Y)"].max()), abs(df_summary["Total Power (Y)"].min()), 5) + 2
        
        fig = px.scatter(
            df_summary, x="Total Influence (X)", y="Total Power (Y)", text="Aktor",
            color="Tipologi Kelembagaan", range_x=[-max_bound, max_bound], range_y=[-max_bound, max_bound],
            labels={"Total Influence (X)": "Total Kapasitas Pengaruh & Lobi (Influence)", "Total Power (Y)": "Total Otoritas Konstitusional (Power)"},
            title="Peta Kuadran Aktor (Tradisi Virginia School of Public Choice)"
        )
        
        fig.add_shape(type="line", x0=-max_bound, y0=0, x1=max_bound, y1=0, line=dict(color="gray", width=1, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=-max_bound, x1=0, y1=max_bound, line=dict(color="gray", width=1, dash="dash"))
        
        fig.update_traces(marker=dict(size=14), textposition='top center')
        fig.update_layout(height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        
        st.plotly_chart(fig, use_container_width=True)
