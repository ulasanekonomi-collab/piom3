import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Pengaturan tata letak melebar agar ruang matriks maksimal
st.set_page_config(layout="wide")

# ==========================================
# SIDEBAR: PROFIL PENGEMBANG (VERSI KOMPAK)
# ==========================================
col1, col2 = st.sidebar.columns([1, 2])
with col1:
    st.image("yuhka.jpg", use_container_width=True)
with col2:
    st.caption("**PIOM Developer:**")
    st.caption("**Yuhka Sundaya**")
    st.caption("EP Unisba @2026")
st.sidebar.write("---")

# ==========================================
# SIDEBAR: 1. MANAJEMEN AKTOR
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

st.sidebar.header("1. Manajemen Aktor")
with st.sidebar.form("add_actor_form", clear_on_submit=True):
    new_actor = st.text_input("Nama Aktor Baru:")
    submit_actor = st.form_submit_button("Tambah Aktor")
    if submit_actor and new_actor:
        if new_actor not in st.session_state.actors:
            st.session_state.actors.append(new_actor)
            update_matrix_structure()
            st.rerun()

st.sidebar.write("**Aktor Aktif:**")
if len(st.session_state.actors) == 0:
    st.sidebar.info("Belum ada aktor.")
else:
    actor_list = ", ".join(st.session_state.actors)
    st.sidebar.caption(actor_list)

st.sidebar.write("---")

# ==========================================
# SIDEBAR: NAVIGASI MENU UTAMA (KOMPAK VERTIKAL)
# ==========================================
st.sidebar.header("2. Menu Navigasi")
menu_pilihan = st.sidebar.radio(
    "Pilih Langkah Analisis:",
    [
        "Data: Matriks Atribut Aktor",
        "Data: Matriks Collaboration",
        "Data: Matriks Influence",
        "Data: Matriks Conflict",
        "Data: Matriks Power",
        "Analisis: Power & Public Choice",
        "Analisis: Property Rights (NIE)",
        "Analisis: Transaction Cost & Info"
    ]
)

# ==========================================
# AREA UTAMA (KANAN) - RESPOND TERHADAP MENU
# ==========================================
st.title("Power-Institutional Map Analysis (PIOM)")

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
    st.info("Silakan masukkan minimal satu nama aktor di menu samping (sidebar) terlebih dahulu untuk membuka instrumen.")
else:
    # --- MENU: ATRIBUT ---
    if menu_pilihan == "Data: Matriks Atribut Aktor":
        st.subheader("Matriks Profil & Atribut Aktor")
        edited_attr = st.data_editor(
            st.session_state.matrix_atribut, use_container_width=True, key="editor_attr_state",
            on_change=save_changes, args=("matrix_atribut", "editor_attr_state")
        )
        st.session_state.matrix_atribut = edited_attr

    # --- MENU: COLLABORATION ---
    elif menu_pilihan == "Data: Matriks Collaboration":
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        df_collab = st.session_state.matrix_collaboration
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in df_collab.columns}
        edited_collab = st.data_editor(
            df_collab, column_config=config_collab, use_container_width=True, key="editor_collab_state",
            on_change=save_changes, args=("matrix_collaboration", "editor_collab_state")
        )
        st.session_state.matrix_collaboration = edited_collab

    # --- MENU: INFLUENCE ---
    elif menu_pilihan == "Data: Matriks Influence":
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        df_inf = st.session_state.matrix_influence
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_inf.columns}
        edited_inf = st.data_editor(
            df_inf, column_config=config_inf, use_container_width=True, key="editor_inf_state",
            on_change=save_changes, args=("matrix_influence", "editor_inf_state")
        )
        st.session_state.matrix_influence = edited_inf

    # --- MENU: CONFLICT ---
    elif menu_pilihan == "Data: Matriks Conflict":
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        df_conf = st.session_state.matrix_conflict
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in df_conf.columns}
        edited_conf = st.data_editor(
            df_conf, column_config=config_conf, use_container_width=True, key="editor_conf_state",
            on_change=save_changes, args=("matrix_conflict", "editor_conf_state")
        )
        st.session_state.matrix_conflict = edited_conf

    # --- MENU: POWER ---
    elif menu_pilihan == "Data: Matriks Power":
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        df_pow = st.session_state.matrix_power
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in df_pow.columns}
        edited_pow = st.data_editor(
            df_pow, column_config=config_pow, use_container_width=True, key="editor_pow_state",
            on_change=save_changes, args=("matrix_power", "editor_pow_state")
        )
        st.session_state.matrix_power = edited_pow

    # --- MENU: ANALISIS PUBLIC CHOICE ---
    elif menu_pilihan == "Analisis: Power & Public Choice":
        st.subheader("Analisis Peta Kekuasaan & Pilihan Publik (Public Choice)")
        st.markdown("Mengacu pada kerangka pemikiran **James Buchanan & Gordon Tullock**, grafik memetakan posisi aktor berdasarkan akumulasi Otoritas Formal (Power) vs Kapasitas Lobi (Influence).")
        
        m_inf = st.session_state.matrix_influence
        m_pow = st.session_state.matrix_power
        
        summary_data = []
        for actor in st.session_state.actors:
            sum_inf_out = m_inf.loc[actor].sum()
            sum_pow_out = m_pow.loc[actor].sum()
            
            if sum_inf_out > 0 and sum_pow_out > 0:
                kuadran = "Kuadran I: The Ruling Coalition"
            elif sum_inf_out >= 0 and sum_pow_out <= 0:
                kuadran = "Kuadran II: The Rent-Seekers / Lobbyists"
            elif sum_inf_out <= 0 and sum_pow_out > 0:
                kuadran = "Kuadran III: The Constitutional Agents"
            else:
                kuadran = "Kuadran IV: The Disfranchised Public"
                
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
        max_bound = max(abs(df_summary["Total Influence (X)"].max()), abs(df_summary["Total Influence (X)"].min()),
                        abs(df_summary["Total Power (Y)"].max()), abs(df_summary["Total Power (Y)"].min()), 5) + 2
        
        fig = px.scatter(
            df_summary, x="Total Influence (X)", y="Total Power (Y)", text="Aktor",
            color="Tipologi Kelembagaan", range_x=[-max_bound, max_bound], range_y=[-max_bound, max_bound],
            labels={"Total Influence (X)": "Total Kapasitas Pengaruh (Influence)", "Total Power (Y)": "Total Otoritas Konstitusional (Power)"}
        )
        fig.add_shape(type="line", x0=-max_bound, y0=0, x1=max_bound, y1=0, line=dict(color="gray", width=1, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=-max_bound, x1=0, y1=max_bound, line=dict(color="gray", width=1, dash="dash"))
        fig.update_traces(marker=dict(size=14), textposition='top center')
        fig.update_layout(height=550, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        st.plotly_chart(fig, use_container_width=True)

    # --- MENU: ANALISIS PROPERTY RIGHTS (NIE) ---
    elif menu_pilihan == "Analisis: Property Rights (NIE)":
        st.subheader("Analisis Hak Kepemilikan & Tatanan Kelembagaan (Property Rights)")
        st.markdown("Mengacu pada kerangka pemikiran **Oliver Williamson & Ronald Coase**, dashboard ini memindai titik friksi kelembagaan akibat sengketa hak kelola (*overlapping jurisdictions*) atau peminggiran hak kelompok marjinal.")
        
        m_conf = st.session_state.matrix_conflict
        m_pow = st.session_state.matrix_power
        actors = st.session_state.actors
        
        friction_logs = []
        
        for i in range(len(actors)):
            for j in range(i + 1, len(actors)):
                actA = actors[i]
                actB = actors[j]
                
                c_A_to_B = m_conf.loc[actA, actB]
                c_B_to_A = m_conf.loc[actB, actA]
                p_A_to_B = m_pow.loc[actA, actB]
                p_B_to_A = m_pow.loc[actB, actA]
                
                if (c_A_to_B <= -4 or c_B_to_A <= -4) and (p_A_to_B >= 4 and p_B_to_A >= 4):
                    friction_logs.append({
                        "Interaksi Aktor": f"{actA} $\\leftrightarrow$ {actB}",
                        "Friction Type": "⚠️ Institutional Deadlock",
                        "Deskripsi Diagnosis": f"Terjadi tumpang tindih Hak Kepemilikan formal yang parah (Keduanya memegang Power formal $\\ge 4$ namun memiliki tingkat konflik relasi ekstrem $\\le -4$). Regulasi berisiko macet total."
                    })
                
                elif (c_A_to_B <= -3 or c_B_to_A <= -3) and ((p_A_to_B >= 4 and p_B_to_A == 0) or (p_B_to_A >= 4 and p_A_to_B == 0)):
                    penguasa = actA if p_A_to_B >= 4 else actB
                    tereksklusi = actB if p_A_to_B >= 4 else actA
                    friction_logs.append({
                        "Interaksi Aktor": f"{penguasa} $\\rightarrow$ {tereksklusi}",
                        "Friction Type": "🚨 Institutional Exclusion",
                        "Deskripsi Diagnosis": f"Struktur aturan formal mengucilkan pranata lokal/informal. Otoritas formal {penguasa} menekan kepentingan {tereksklusi} tanpa memberikan ruang hak tawar hukum yang setara (Power = 0)."
                    })
        
        if len(friction_logs) == 0:
            st.success("✅ **Sistem Aman:** Tidak ditemukan indikasi kerusakan jalinan 'Property Rights' atau tumpang tindih jurisdiksi formal yang ekstrem dari data matriks saat ini.")
        else:
            st.warning(f"🚨 **Terdeteksi {len(friction_logs)} Titik Gesekan Kelembagaan Sektoral:**")
            df_friction = pd.DataFrame(friction_logs)
            st.dataframe(df_friction, use_container_width=True)
            st.write("---")
            st.info("💡 **Rekomendasi Kebijakan (Coasean Insight):** Sengketa kelembagaan di atas membutuhkan penegasan garis demarkasi hak kelola (*clear-cut property rights*) pada Level 2 Williamson (Aturan Formal) untuk menekan tingginya biaya transaksi di lapangan.")

    # --- MENU: ANALISIS TRANSACTION COST & ASIMETRI INFORMASI (LOGIKA BARU) ---
    elif menu_pilihan == "Analisis: Transaction Cost & Info":
        st.subheader("Analisis Biaya Transaksi & Asimetri Informasi")
        st.markdown("Mengacu pada kerangka pemikiran **Ronald Coase & Oliver Williamson**, modul ini mendeteksi kebocoran efisiensi sistem akibat pembendungan informasi (*information hoarding*) atau sumbatan sekat birokrasi.")
        
        m_inf = st.session_state.matrix_influence
        m_collab = st.session_state.matrix_collaboration
        actors = st.session_state.actors
        
        tc_logs = []
        
        for actA in actors:
            for actB in actors:
                if actA == actB:
                    continue
                
                inf_val = m_inf.loc[actA, actB]
                collab_val = m_collab.loc[actA, actB]
                inf_reverse = m_inf.loc[actB, actA]
                collab_reverse = m_collab.loc[actB, actA]
                
                # Deteksi Kasus 1: Information Hoarding
                if inf_val >= 4 and collab_val <= 1:
                    tc_logs.append({
                        "Arah Hubungan": f"{actA} → {actB}", # Menggunakan panah teks standar
                        "Indikator Penyakit": "🚨 Information Hoarding",
                        "Deskripsi Analisis": f"{actA} memancarkan daya lobi/pengaruh yang kuat ({inf_val}) terhadap {actB}, namun menahan level kolaborasi riil di tingkat minimal ({collab_val}). Terindikasi memanfaatkan asimetri informasi untuk mengunci posisi tawar."
                    })
                
                # Deteksi Kasus 2: High Transaction Cost Barrier
                if actA < actB:
                    if (inf_val >= 3 or inf_reverse >= 3) and (collab_val == 0 and collab_reverse == 0):
                        tc_logs.append({
                            "Arah Hubungan": f"{actA} ↔ {actB}", # Menggunakan panah teks standar
                            "Indikator Penyakit": "⚠️ High Transaction Cost Barrier",
                            "Deskripsi Analisis": f"Kedua aktor saling memiliki keterikatan pengaruh horizontal yang kuat, namun level kolaborasi dua arah terkunci di angka 0. Tingginya sekat birokrasi atau 'distrust' membuat biaya transaksi koordinasi lebih mahal daripada insentif kerjasamanya."
                        })
                        
        if len(tc_logs) == 0:
            st.success("✅ **Sistem Efisien:** Tidak terdeteksi indikasi pembendungan informasi strategis atau sumbatan biaya transaksi yang ekstrem antar-aktor.")
        else:
            st.warning(f"🚨 **Terdeteksi {len(tc_logs)} Titik Kebocoran Efisiensi Transaksi:**")
            df_tc = pd.DataFrame(tc_logs)
            st.dataframe(df_tc, use_container_width=True)
            st.write("---")
            st.info("💡 **Rekomendasi Kebijakan (Williamsonian Insight):** Atasi friksi di atas dengan menyusun instruksi kerja bersama, standarisasi data satu pintu, atau penguatan sistem pengawasan independen untuk memangkas *Information Asymmetry*.")
