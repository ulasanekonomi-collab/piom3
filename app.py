import streamlit as st
import pandas as pd
import numpy as np

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

# 1. INISIALISASI SESSION STATE (DEFAULT AKTOR KOSONG)
if "actors" not in st.session_state:
    st.session_state.actors = []

# Fungsi untuk membuat/memperbarui matriks relasi
def get_matrix(matrix_name, default_val=0):
    actors = st.session_state.actors
    n = len(actors)
    if matrix_name not in st.session_state:
        st.session_state[matrix_name] = pd.DataFrame(
            np.full((n, n), default_val), index=actors, columns=actors
        )
    else:
        # Sinkronisasi jika ada penambahan aktor baru
        old_df = st.session_state[matrix_name]
        new_df = pd.DataFrame(default_val, index=actors, columns=actors)
        for r in old_df.index:
            for c in old_df.columns:
                if r in new_df.index and c in new_df.columns:
                    new_df.loc[r, c] = old_df.loc[r, c]
        st.session_state[matrix_name] = new_df
    return st.session_state[matrix_name]

# 2. MANAJEMEN AKTOR (INPUT)
st.sidebar.header("1. Manajemen Aktor")
with st.sidebar.form("add_actor_form", clear_on_submit=True):
    new_actor = st.text_input("Nama Aktor Baru:")
    submit_actor = st.form_submit_button("Tambah Aktor")
    if submit_actor and new_actor:
        if new_actor not in st.session_state.actors:
            st.session_state.actors.append(new_actor)
            st.rerun()

st.sidebar.write("**Daftar Aktor Aktif:**")
if len(st.session_state.actors) == 0:
    st.sidebar.info("Belum ada aktor. Silakan tambah di atas.")
else:
    for act in st.session_state.actors:
        st.sidebar.markdown(f"- {act}")

# 3. NAVIGASI MATRIKS UTAMA
tabs = st.tabs([
    "2. Matriks Aktor (Atribut)", 
    "3. Matriks Collaboration", 
    "4. Matriks Influence", 
    "5. Matriks Conflict", 
    "6. Matriks Power"
])

# DEFINISI SKALA STANDARD SESUAI FRAMEWORK CIC-P (-5 s.d +5)
cicp_full_options = list(range(-5, 6))       # [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
cicp_positive_options = list(range(0, 6))   # [0, 1, 2, 3, 4, 5] untuk Kolaborasi murni
cicp_negative_options = list(range(-5, 1))   # [-5, -4, -3, -2, -1, 0] untuk Konflik murni

# JIKA BELUM ADA AKTOR, TAMPILKAN PESAN DI SETIAP TAB
if len(st.session_state.actors) == 0:
    for i in range(5):
        with tabs[i]:
            st.info("Silakan masukkan minimal satu nama aktor di menu samping (sidebar) terlebih dahulu untuk mengisi matriks.")
else:
    # --- TAB 2: MATRIKS AKTOR (ATRIBUT) ---
    with tabs[0]:
        st.subheader("Matriks Profil & Atribut Aktor")
        if "matrix_atribut" not in st.session_state:
            st.session_state.matrix_atribut = pd.DataFrame(
                {"Tipe Lembaga": ["Formal"] * len(st.session_state.actors), "Peran Utama": ["Regulator"] * len(st.session_state.actors)},
                index=st.session_state.actors
            )
        if len(st.session_state.matrix_atribut) != len(st.session_state.actors):
            new_attr = pd.DataFrame(
                {"Tipe Lembaga": ["Formal"] * len(st.session_state.actors), "Peran Utama": ["Regulator"] * len(st.session_state.actors)},
                index=st.session_state.actors
            )
            for r in st.session_state.matrix_atribut.index:
                if r in new_attr.index:
                    new_attr.loc[r] = st.session_state.matrix_atribut.loc[r]
            st.session_state.matrix_atribut = new_attr

        edited_attr = st.data_editor(st.session_state.matrix_atribut, use_container_width=True, key="editor_attr")
        st.session_state.matrix_atribut = edited_attr

    # --- TAB 3: COLLABORATION (Skala 0 s.d +5) ---
    with tabs[1]:
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        st.caption("Arah pengisian: Seberapa besar Baris menginisiasi/mendukung kolaborasi ke Kolom (Skala 0 s.d 5)")
        df_collab = get_matrix("matrix_collaboration", default_val=0)
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in df_collab.columns}
        edited_collab = st.data_editor(df_collab, column_config=config_collab, use_container_width=True, key="editor_collab")
        st.session_state.matrix_collaboration = edited_collab

    # --- TAB 4: INFLUENCE (Skala Rentang Penuh -5 s.d +5) ---
    with tabs[2]:
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        st.caption("Arah pengisian: Dampak pengaruh Baris ke Kolom. Nilai (-) melemahkan, (+) memperkuat (Skala -5 s.d 5)")
        df_inf = get_matrix("matrix_influence", default_val=0)
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_inf.columns}
        edited_inf = st.data_editor(df_inf, column_config=config_inf, use_container_width=True, key="editor_inf")
        st.session_state.matrix_influence = edited_inf

    # --- TAB 5: CONFLICT (Skala -5 s.d 0) ---
    with tabs[3]:
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        st.caption("Arah pengisian: Resistensi atau potensi gesekan kepentingan Baris terhadap Kolom (Skala -5 s.d 0)")
        df_conf = get_matrix("matrix_conflict", default_val=0)
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in df_conf.columns}
        edited_conf = st.data_editor(df_conf, column_config=config_conf, use_container_width=True, key="editor_conf")
        st.session_state.matrix_conflict = edited_conf

    # --- TAB 6: POWER (Skala Rentang Penuh -5 s.d +5) ---
    with tabs[4]:
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        st.caption("Arah pengisian: Otoritas/Kendali Baris atas Kolom. Nilai (-) bentuk subordinasi, (+) kontrol langsung (Skala -5 s.d 5)")
        df_pow = get_matrix("matrix_power", default_val=0)
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_pow.columns}
        edited_pow = st.data_editor(df_pow, column_config=config_pow, use_container_width=True, key="editor_pow")
        st.session_state.matrix_power = edited_pow
