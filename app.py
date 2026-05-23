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
                        for col in old_df.columns:
                            if col in new_df.columns:
                                new_df.loc[r, col] = old_df.loc[r, col]
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
# SIDEBAR: NAVIGASI MENU UTAMA
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
        "Analisis: Transaction Cost & Info",
        "Analisis: Principal-Agent (NIE)",
        "Analisis: Social Capital & Informal"
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

# Pengecekan Aktor Kosong
if len(st.session_state.actors) == 0:
    st.info("Silakan masukkan minimal satu nama aktor di menu samping (sidebar) terlebih dahulu untuk membuka instrumen.")
else:
    # Inisialisasi list penampung penyakit global untuk Therapeutic Engine
    all_diseases = []

    # --- JALANKAN PROSES DIAGNOSIS BACKGROUND SECARA LATEN UNTUK RESERVOIR SOLUSI ---
    m_pow = st.session_state.matrix_power
    m_inf = st.session_state.matrix_influence
    m_collab = st.session_state.matrix_collaboration
    m_conf = st.session_state.matrix_conflict
    m_attr = st.session_state.matrix_atribut
    actors = st.session_state.actors

    for i in range(len(actors)):
        for j in range(len(actors)):
            if i == j: continue
            actA = actors[i]
            actB = actors[j]
            
            # Extract data relasi terarah
            p_formal = m_pow.loc[actA, actB]
            inf_val = m_inf.loc[actA, actB]
            collab_val = m_collab.loc[actA, actB]
            c_A_to_B = m_conf.loc[actA, actB]
            
            p_reverse = m_pow.loc[actB, actA]
            inf_reverse = m_inf.loc[actB, actA]
            collab_reverse = m_collab.loc[actB, actA]
            c_B_to_A = m_conf.loc[actB, actA]
            
            typeA = m_attr.loc[actA, "Tipe Lembaga"]
            typeB = m_attr.loc[actB, "Tipe Lembaga"]

            # Lacak Penyakit Property Rights
            if i < j:
                if (c_A_to_B <= -4 or c_B_to_A <= -4) and (p_formal >= 4 and p_reverse >= 4):
                    all_diseases.append("⚠️ Institutional Deadlock")
            
            # Lacak Penyakit Transaction Cost
            if inf_val >= 4 and collab_val <= 1:
                all_diseases.append("🚨 Information Hoarding")
            if i < j and (inf_val >= 3 or inf_reverse >= 3) and (collab_val == 0 and collab_reverse == 0):
                all_diseases.append("⚠️ High Transaction Cost Barrier")

            # Lacak Penyakit Principal Agent
            if p_formal >= 4 and inf_reverse >= 4:
                all_diseases.append("🚨 Potential Agency Capture")
            elif p_formal >= 4 and collab_reverse == 0:
                all_diseases.append("⚠️ Indikasi Moral Hazard (Shirking)")

            # Lacak Penyakit Social Capital (FIXED VARIABEL TYPO DI SINI)
            if i < j and typeA == "Informal" and typeB == "Informal" and collab_val <= 1 and collab_reverse <= 1:
                all_diseases.append("🚨 Low Bridging Capital")
            if typeA == "Formal" and typeB == "Informal" and collab_reverse == 0:
                all_diseases.append("🚨 Low Linking Capital")


    # ==========================================
    # KONTEN INTERFASE ROUTING MENU UTAMA
    # ==========================================
    
    # --- MENU: ATRIBUT ---
    if menu_pilihan == "Data: Matriks Atribut Aktor":
        st.subheader("Matriks Profil & Atribut Aktor")
        config_attr = {
            "Tipe Lembaga": st.column_config.SelectboxColumn(options=["Formal", "Informal"], width="medium", required=True),
            "Peran Utama": st.column_config.TextColumn(width="medium")
        }
        edited_attr = st.data_editor(st.session_state.matrix_atribut, column_config=config_attr, use_container_width=True, key="editor_attr_state", on_change=save_changes, args=("matrix_atribut", "editor_attr_state"))
        st.session_state.matrix_atribut = edited_attr

    # --- MENU: COLLABORATION ---
    elif menu_pilihan == "Data: Matriks Collaboration":
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in m_collab.columns}
        edited_collab = st.data_editor(m_collab, column_config=config_collab, use_container_width=True, key="editor_collab_state", on_change=save_changes, args=("matrix_collaboration", "editor_collab_state"))
        st.session_state.matrix_collaboration = edited_collab

    # --- MENU: INFLUENCE ---
    elif menu_pilihan == "Data: Matriks Influence":
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in m_inf.columns}
        edited_inf = st.data_editor(m_inf, column_config=config_inf, use_container_width=True, key="editor_inf_state", on_change=save_changes, args=("matrix_influence", "editor_inf_state"))
        st.session_state.matrix_influence = edited_inf

    # --- MENU: CONFLICT ---
    elif menu_pilihan == "Data: Matriks Conflict":
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in m_conf.columns}
        edited_conf = st.data_editor(m_conf, column_config=config_conf, use_container_width=True, key="editor_conf_state", on_change=save_changes, args=("matrix_conflict", "editor_conf_state"))
        st.session_state.matrix_conflict = edited_conf

    # --- MENU: POWER ---
    elif menu_pilihan == "Data: Matriks Power":
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in m_pow.columns}
        edited_pow = st.data_editor(m_pow, column_config=config_pow, use_container_width=True, key="editor_pow_state", on_change=save_changes, args=("matrix_power", "editor_pow_state"))
        st.session_state.matrix_power = edited_pow

    # --- MENU: ANALISIS PUBLIC CHOICE ---
    elif menu_pilihan == "Analisis: Power & Public Choice":
        st.subheader("Analisis Peta Kekuasaan & Pilihan Publik (Public Choice)")
        st.markdown("Mengacu pada kerangka pemikiran **James Buchanan & Gordon Tullock**, grafik memetakan posisi aktor berdasarkan akumulasi Otoritas Formal (Power) vs Kapasitas Lobi (Influence).")
        summary_data = []
        for actor in actors:
            sum_inf_out = m_inf.loc[actor].sum()
            sum_pow_out = m_pow.loc[actor].sum()
            if sum_inf_out > 0 and sum_pow_out > 0: kuadran = "Kuadran I: The Ruling Coalition"
            elif sum_inf_out >= 0 and sum_pow_out <= 0: kuadran = "Kuadran II: The Rent-Seekers / Lobbyists"
            elif sum_inf_out <= 0 and sum_pow_out > 0: kuadran = "Kuadran III: The Constitutional Agents"
            else: kuadran = "Kuadran IV: The Disfranchised Public"
            summary_data.append({"Aktor": actor, "Total Influence (X)": int(sum_inf_out), "Total Power (Y)": int(sum_pow_out), "Tipologi Kelembagaan": kuadran})
        df_summary = pd.DataFrame(summary_data)
        st.write("**Tabel Indeks Agregat Ekonomi Politik:**")
        st.dataframe(df_summary, use_container_width=True)
        st.write("---")
        max_bound = max(abs(df_summary["Total Influence (X)"].max()), abs(df_summary["Total Influence (X)"].min()), abs(df_summary["Total Power (Y)"].max()), abs(df_summary["Total Power (Y)"].min()), 5) + 2
        fig = px.scatter(df_summary, x="Total Influence (X)", y="Total Power (Y)", text="Aktor", color="Tipologi Kelembagaan", range_x=[-max_bound, max_bound], range_y=[-max_bound, max_bound])
        fig.add_shape(type="line", x0=-max_bound, y0=0, x1=max_bound, y1=0, line=dict(color="gray", width=1, dash="dash"))
        fig.add_shape(type="line", x0=0, y0=-max_bound, x1=0, y1=max_bound, line=dict(color="gray", width=1, dash="dash"))
        fig.update_traces(marker=dict(size=14), textposition='top center')
        fig.update_layout(height=550, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0))
        st.plotly_chart(fig, use_container_width=True)

    # --- MENU: ANALISIS PROPERTY RIGHTS ---
    elif menu_pilihan == "Analisis: Property Rights (NIE)":
        st.subheader("Analisis Hak Kepemilikan & Tatanan Kelembagaan (Property Rights)")
        friction_logs = []
        for i in range(len(actors)):
            for j in range(i + 1, len(actors)):
                actA, actB = actors[i], actors[j]
                if (m_conf.loc[actA, actB] <= -4 or m_conf.loc[actB, actA] <= -4) and (m_pow.loc[actA, actB] >= 4 and m_pow.loc[actB, actA] >= 4):
                    friction_logs.append({"Interaksi Aktor": f"{actA} ↔ {actB}", "Friction Type": "⚠️ Institutional Deadlock", "Deskripsi Diagnosis": "Terjadi tumpang tindih Hak Kepemilikan formal yang parah. Regulasi berisiko macet total."})
                elif (m_conf.loc[actA, actB] <= -3 or m_conf.loc[actB, actA] <= -3) and ((m_pow.loc[actA, actB] >= 4 and m_pow.loc[actB, actA] == 0) or (m_pow.loc[actB, actA] >= 4 and m_pow.loc[actA, actB] == 0)):
                    penguasa = actA if m_pow.loc[actA, actB] >= 4 else actB
                    tereksklusi = actB if m_pow.loc[actA, actB] >= 4 else actA
                    friction_logs.append({"Interaksi Aktor": f"{penguasa} → {tereksklusi}", "Friction Type": "🚨 Institutional Exclusion", "Deskripsi Diagnosis": f"Otoritas formal {penguasa} menekan kepentingan {tereksklusi} tanpa hak tawar hukum setara."})
        if len(friction_logs) == 0: st.success("✅ **Sistem Aman:** Tidak ditemukan indikasi kerusakan jalinan 'Property Rights'.")
        else:
            st.warning("🚨 **Terdeteksi Titik Gesekan Kelembagaan Sektoral:**")
            st.dataframe(pd.DataFrame(friction_logs), use_container_width=True)

    # --- MENU: ANALISIS TRANSACTION COST ---
    elif menu_pilihan == "Analisis: Transaction Cost & Info":
        st.subheader("Analisis Biaya Transaksi & Asimetri Informasi")
        tc_logs = []
        for actA in actors:
            for actB in actors:
                if actA == actB: continue
                if m_inf.loc[actA, actB] >= 4 and m_collab.loc[actA, actB] <= 1:
                    tc_logs.append({"Arah Hubungan": f"{actA} → {actB}", "Indikator Penyakit": "🚨 Information Hoarding", "Deskripsi Analisis": f"{actA} memanfaatkan asimetri informasi untuk mengunci posisi tawar."})
                if actA < actB and (m_inf.loc[actA, actB] >= 3 or m_inf.loc[actB, actA] >= 3) and (m_collab.loc[actA, actB] == 0 and m_collab.loc[actB, actA] == 0):
                    tc_logs.append({"Arah Hubungan": f"{actA} ↔ {actB}", "Indikator Penyakit": "⚠️ High Transaction Cost Barrier", "Deskripsi Analisis": "Tingginya sekat birokrasi atau 'distrust' membuat biaya transaksi koordinasi terlalu mahal."})
        if len(tc_logs) == 0: st.success("✅ **Sistem Efisien:** Tidak terdeteksi indikasi pembendungan informasi.")
        else:
            st.warning("🚨 **Terdeteksi Titik Kebocoran Efisiensi Transaksi:**")
            st.dataframe(pd.DataFrame(tc_logs), use_container_width=True)

    # --- MENU: ANALISIS PRINCIPAL-AGENT ---
    elif menu_pilihan == "Analisis: Principal-Agent (NIE)":
        st.subheader("Analisis Hubungan Keagenan (Principal-Agent Relationship)")
        pa_logs = []
        for actA in actors:
            for actB in actors:
                if actA == actB: continue
                if m_pow.loc[actA, actB] >= 4 and m_inf.loc[actB, actA] >= 4:
                    pa_logs.append({"Hubungan Struktural": f"{actA} (Principal) → {actB} (Agent)", "Kerentanan Hubungan": "🚨 Potential Agency Capture", "Deskripsi Analisis": "Risiko tinggi fungsi pengawasan formal runtuh tersandera kepentingan Agen."})
                elif m_pow.loc[actA, actB] >= 4 and m_collab.loc[actB, actA] == 0:
                    pa_logs.append({"Hubungan Struktural": f"{actA} (Principal) → {actB} (Agent)", "Kerentanan Hubungan": "⚠️ Indikasi Moral Hazard (Shirking)", "Deskripsi Analisis": "Agen terindikasi melakukan pengabaian mandat secara oportunis demi meredam radar evaluasi."})
        if len(pa_logs) == 0: st.success("✅ **Hubungan Akuntabel:** Tidak terdeteksi adanya indikasi moral hazard.")
        else:
            st.warning("🚨 **Terdeteksi Titik Kerentanan Akuntabilitas Keagenan:**")
            st.dataframe(pd.DataFrame(pa_logs), use_container_width=True)

    # --- MENU: ANALISIS SOCIAL CAPITAL ---
    elif menu_pilihan == "Analisis: Social Capital & Informal":
        st.subheader("Analisis Modal Sosial & Institusi Informal")
        sc_logs = []
        for actA in actors:
            for actB in actors:
                if actA == actB: continue
                collab_val = m_collab.loc[actA, actB]
                collab_reverse = m_collab.loc[actB, actA]
                typeA = m_attr.loc[actA, "Tipe Lembaga"]
                typeB = m_attr.loc[actB, "Tipe Lembaga"]
                
                if actA < actB and typeA == "Informal" and typeB == "Informal" and collab_val <= 1 and collab_reverse <= 1:
                    sc_logs.append({"Jejaring Relasional": f"{actA} ↔ {actB}", "Kerusakan Jaringan": "🚨 Low Bridging Capital", "Deskripsi Diagnosis": "Terjadi fragmentasi sosial akut (silo komunitas) di tingkat tapak."})
                if typeA == "Formal" and typeB == "Informal" and collab_reverse == 0:
                    sc_logs.append({"Jejaring Relasional": f"{actB} (Informal) → {actA} (Formal)", "Kerusakan Jaringan": "🚨 Low Linking Capital", "Deskripsi Diagnosis": "Saluran kemitraan vertikal menuju regulator formal bernilai murni 0. Risiko distrust masif."})
        if len(sc_logs) == 0: st.success("✅ **Kesehatan Sosial Terjamin:** Tingkat modal sosial (Social Trust) berada pada kapasitas optimal.")
        else:
            st.warning("🚨 **Terdeteksi Titik Kelemahan Modal Sosial Komunitas:**")
            st.dataframe(pd.DataFrame(sc_logs), use_container_width=True)


    # ==========================================
    # CORE ENGINE UTAMA: THERAPEUTIC SOLUTION GENERATOR
    # ==========================================
    st.write("---")
    st.header("3. Executive Policy Brief & Rekomendasi Solusi Kelembagaan")
    st.markdown("Menggunakan sintesis kumulatif lintas domain (**Ostromian Polycentricity & Williamson L1-L3 Framework**), sistem merumuskan cetak biru resep solusi otomatis:")

    if len(all_diseases) == 0:
        st.success("✅ **Sistem Konstitusi Aman:** Tidak ditemukan kontradiksi relasi strategis horizontal maupun vertikal. Struktur tata kelola berada pada efisiensi *Pareto Optimal*.")
    else:
        unique_diseases = set(all_diseases)
        st.error(f"🚨 **Hasil Diagnosis Sintesis Lintas Domain:** Terdeteksi indikasi kerusakan tata kelola sistemik. Berikut rekomendasi paket reformasi kelembagaan:")
        
        if "⚠️ Institutional Deadlock" in unique_diseases or "🚨 Institutional Exclusion" in unique_diseases:
            with st.expander("🏛️ KLASTER A: Jurisdictional Harmonization & Property Rights Redesign", expanded=True):
                st.write("**Rekomendasi Utama (Clear-cut Boundaries):**")
                st.write("- Terbitkan Peraturan Daerah (Perda) atau Peraturan Bersama Kepala Daerah baru untuk memotong tumpang tindih jurisdiksi yang memicu *deadlock*.")
                st.write("- Legalitas hak kelola faksi lokal/informal wajib diakui secara resmi melalui kepastian hukum tertulis agar terhindar dari peminggiran sepihak (*Institutional Exclusion*).")

        if "🚨 Information Hoarding" in unique_diseases or "⚠️ High Transaction Cost Barrier" in unique_diseases:
            with st.expander("📊 KLASTER B: Information Symmetry & Transaction Cost Reduction", expanded=True):
                st.write("**Rekomendasi Utama (Open-Data Manifest):**")
                st.write("- Batasi keunggulan asimetri swasta dengan mewajibkan transparansi data hulu-hilir (volume sampah riil, neraca keuangan sirkular) sebagai syarat mutlak perpanjangan konsesi.")
                st.write("- Sediakan platform data digital satu pintu untuk memangkas tingginya biaya transaksi koordinasi antar-instansi birokrasi.")

        if "🚨 Potential Agency Capture" in unique_diseases or "⚠️ Indikasi Moral Hazard (Shirking)" in unique_diseases:
            with st.expander("📜 KLASTER C: Performance-Based Accountability (Anti-Capture Mechanism)", expanded=True):
                st.write("**Rekomendasi Utama (Performance Contracting):**")
                st.write("- Transformasikan seluruh ikatan kerja sama operasional dengan pihak ketiga/Agen dari pola serapan anggaran konvensional beralih menuju *Performance-Based Contracting* (insentif dibayarkan berbasis output riil bersih di lapangan).")
                st.write("- Lembagakan dewan pengawas tripartit independen (pemerintah, akademisi, perwakilan warga) untuk mematahkan fenomena pembajakan regulasi (*Agency Capture*).")

        if "🚨 Low Bridging Capital" in unique_diseases or "🚨 Low Linking Capital" in unique_diseases:
            with st.expander("🌱 KLASTER D: Ostromian Co-Management & Social Trust Integration", expanded=True):
                st.write("**Rekomendasi Utama (Polycentric Governance):**")
                st.write("- Cegah malpraktik pemaksaan hukum *top-down* yang kaku. Ketika jalinan modal sosial vertikal retak (*Low Linking*), beralihlah ke pendekatan partisipatif.")
                st.write("- Pelembagakan mekanisme Pengelolaan Bersama (*Co-Management*) dengan memberikan kuota wilayah kerja resmi bagi pranata lokal (seperti paguyuban pengepul/pemulung) sebagai rantai pasok formal daerah.")
