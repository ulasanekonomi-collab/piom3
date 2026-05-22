import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Power-Institutional Map Analysis (PIOM)")

# 1. INISIALISASI SESSION STATE
if "actors" not in st.session_state:
    st.session_state.actors = ["Kementerian A", "Dinas B", "Asosiasi C"]

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

# Opsi Dropdown untuk pengisian matriks relasi
score_options = [0, 1, 2, 3]
score_options_conflict = [-2, -1, 0, 1, 2]

# --- TAB 2: MATRIKS AKTOR (ATRIBUT) ---
with tabs[0]:
    st.subheader("Matriks Profil & Atribut Aktor")
    if "matrix_atribut" not in st.session_state:
        st.session_state.matrix_atribut = pd.DataFrame(
            {"Tipe Lembaga": ["Formal"] * len(st.session_state.actors), "Peran Utama": ["Regulator"] * len(st.session_state.actors)},
            index=st.session_state.actors
        )
    edited_attr = st.data_editor(st.session_state.matrix_atribut, use_container_width=True)
    st.session_state.matrix_atribut = edited_attr

# --- TAB 3: COLLABORATION ---
with tabs[1]:
    st.subheader("Matriks Kolaborasi Antar-Aktor")
    df_collab = get_matrix("matrix_collaboration", default_val=0)
    # Membuat dropdown otomatis di setiap sel tabel
    config = {col: st.column_config.SelectboxColumn(options=score_options, width="medium") for col in df_collab.columns}
    edited_collab = st.data_editor(df_collab, column_config=config, use_container_width=True)
    st.session_state.matrix_collaboration = edited_collab

# --- TAB 4: INFLUENCE ---
with tabs[2]:
    st.subheader("Matriks Pengaruh (Influence) Antar-Aktor")
    df_inf = get_matrix("matrix_influence", default_val=0)
    config = {col: st.column_config.SelectboxColumn(options=score_options, width="medium") for col in df_inf.columns}
    edited_inf = st.data_editor(df_inf, column_config=config, use_container_width=True)
    st.session_state.matrix_influence = edited_inf

# --- TAB 5: CONFLICT ---
with tabs[3]:
    st.subheader("Matriks Konflik Kepentingan Antar-Aktor")
    df_conf = get_matrix("matrix_conflict", default_val=0)
    config = {col: st.column_config.SelectboxColumn(options=score_options_conflict, width="medium") for col in df_conf.columns}
    edited_conf = st.data_editor(df_conf, column_config=config, use_container_width=True)
    st.session_state.matrix_conflict = edited_conf

# --- TAB 6: POWER ---
with tabs[4]:
    st.subheader("Matriks Kekuasaan (Power) Antar-Aktor")
    df_pow = get_matrix("matrix_power", default_val=0)
    config = {col: st.column_config.SelectboxColumn(options=score_options, width="medium") for col in df_pow.columns}
    edited_pow = st.data_editor(df_pow, column_config=config, use_container_width=True)
    st.session_state.matrix_power = edited_pow
