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
        "Analisis: Social Capital & Informal",
        "🎯 Cetak Biru: Solusi Kelembagaan"
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
    m_pow = st.session_state.matrix_power
    m_inf = st.session_state.matrix_influence
    m_collab = st.session_state.matrix_collaboration
    m_conf = st.session_state.matrix_conflict
    m_attr = st.session_state.matrix_atribut
    actors = st.session_state.actors

    # ==========================================
    # KONTEN INTERFASE ROUTING DATA & ANALISIS INDIVIDUAL
    # ==========================================
    
    if menu_pilihan == "Data: Matriks Atribut Aktor":
        st.subheader("Matriks Profil & Atribut Aktor")
        config_attr = {
            "Tipe Lembaga": st.column_config.SelectboxColumn(options=["Formal", "Informal"], width="medium", required=True),
            "Peran Utama": st.column_config.TextColumn(width="medium")
        }
        edited_attr = st.data_editor(st.session_state.matrix_atribut, column_config=config_attr, use_container_width=True, key="editor_attr_state", on_change=save_changes, args=("matrix_atribut", "editor_attr_state"))
        st.session_state.matrix_atribut = edited_attr

    elif menu_pilihan == "Data: Matriks Collaboration":
        st.subheader("Matriks Kolaborasi Antar-Aktor (Collaboration)")
        config_collab = {col: st.column_config.SelectboxColumn(options=cicp_positive_options, width="medium") for col in m_collab.columns}
        edited_collab = st.data_editor(m_collab, column_config=config_collab, use_container_width=True, key="editor_collab_state", on_change=save_changes, args=("matrix_collaboration", "editor_collab_state"))
        st.session_state.matrix_collaboration = edited_collab

    elif menu_pilihan == "Data: Matriks Influence":
        st.subheader("Matriks Pengaruh Antar-Aktor (Influence)")
        config_inf = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in m_inf.columns}
        edited_inf = st.data_editor(m_inf, column_config=config_inf, use_container_width=True, key="editor_inf_state", on_change=save_changes, args=("matrix_influence", "editor_inf_state"))
        st.session_state.matrix_influence = edited_inf

    elif menu_pilihan == "Data: Matriks Conflict":
        st.subheader("Matriks Konflik Kepentingan Antar-Aktor (Conflict)")
        config_conf = {col: st.column_config.SelectboxColumn(options=cicp_negative_options, width="medium") for col in m_conf.columns}
        edited_conf = st.data_editor(m_conf, column_config=config_conf, use_container_width=True, key="editor_conf_state", on_change=save_changes, args=("matrix_conflict", "editor_conf_state"))
        st.session_state.matrix_conflict = edited_conf

    elif menu_pilihan == "Data: Matriks Power":
        st.subheader("Matriks Kekuasaan/Otoritas Antar-Aktor (Power)")
        config_pow = {col: st.column_config.SelectboxColumn(options=cicp_full_options, width="medium") for col in m_pow.columns}
        edited_pow = st.data_editor(m_pow, column_config=config_pow, use_container_width=True, key="editor_pow_state", on_change=save_changes, args=("matrix_power", "editor_pow_state"))
        st.session_state.matrix_power = edited_pow

    elif menu_pilihan == "Analisis: Power & Public Choice":
        st.subheader("Analisis Peta Kekuasaan & Pilihan Publik (Public Choice)")
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

    # Menu Analisis Individual Tetap Berfungsi Statis Sebagai Log Awal Pengguna
    elif menu_pilihan == "Analisis: Property Rights (NIE)":
        st.subheader("Analisis Hak Kepemilikan & Tatanan Kelembagaan (Property Rights)")
        logs = []
        for i in range(len(actors)):
            for j in range(len(actors)):
                if i == j: continue
                if m_conf.loc[actors[i], actors[j]] <= -4 and m_pow.loc[actors[i], actors[j]] >= 4 and m_pow.loc[actors[j], actors[i]] >= 4:
                    logs.append({"Interaksi": f"{actors[i]} ↔ {actors[j]}", "Tipe": "⚠️ Institutional Deadlock", "Deskripsi": "Tumpang tindih klaim hak kelola formal yang memicu kemacetan regulasi."})
                elif m_conf.loc[actors[i], actors[j]] <= -3 and m_pow.loc[actors[i], actors[j]] >= 4 and m_pow.loc[actors[j], actors[i]] == 0:
                    logs.append({"Interaksi": f"{actors[i]} → {actors[j]}", "Tipe": "🚨 Institutional Exclusion", "Deskripsi": "Otoritas menekan kepentingan aktor lain tanpa hak tawar seimbang."})
        if not logs: st.success("✅ Tidak ditemukan anomali Property Rights.")
        else: st.warning("Anomali Terdeteksi:"); st.dataframe(pd.DataFrame(logs), use_container_width=True)

    elif menu_pilihan == "Analisis: Transaction Cost & Info":
        st.subheader("Analisis Biaya Transaksi & Asimetri Informasi")
        logs = []
        for i in range(len(actors)):
            for j in range(len(actors)):
                if i == j: continue
                if m_inf.loc[actors[i], actors[j]] >= 4 and m_collab.loc[actors[i], actors[j]] <= 1:
                    logs.append({"Arah": f"{actors[i]} → {actors[j]}", "Tipe": "🚨 Information Hoarding", "Deskripsi": "Pemanfaatan asimetri informasi untuk mengunci posisi tawar."})
        if not logs: st.success("✅ Tidak ditemukan anomali Biaya Transaksi.")
        else: st.warning("Anomali Terdeteksi:"); st.dataframe(pd.DataFrame(logs), use_container_width=True)

    elif menu_pilihan == "Analisis: Principal-Agent (NIE)":
        st.subheader("Analisis Hubungan Keagenan (Principal-Agent)")
        logs = []
        for i in range(len(actors)):
            for j in range(len(actors)):
                if i == j: continue
                if m_pow.loc[actors[i], actors[j]] >= 4 and m_inf.loc[actors[j], actors[i]] >= 4:
                    logs.append({"Struktur": f"{actors[i]} (P) → {actors[j]} (A)", "Tipe": "🚨 Potential Agency Capture", "Deskripsi": "Fungsi pengawasan runtuh tersandera kepentingan Agen."})
        if not logs: st.success("✅ Tidak ditemukan anomali Hubungan Keagenan.")
        else: st.warning("Anomali Terdeteksi:"); st.dataframe(pd.DataFrame(logs), use_container_width=True)

    elif menu_pilihan == "Analisis: Social Capital & Informal":
        st.subheader("Analisis Modal Sosial & Institusi Informal")
        logs = []
        for i in range(len(actors)):
            for j in range(len(actors)):
                if i == j: continue
                if m_attr.loc[actors[i], "Tipe Lembaga"] == "Formal" and m_attr.loc[actors[j], "Tipe Lembaga"] == "Informal" and m_collab.loc[actors[j], actors[i]] == 0:
                    logs.append({"Jejaring": f"{actors[j]} (Inf) → {actors[i]} (Form)", "Tipe": "🚨 Low Linking Capital", "Deskripsi": "Saluran kemitraan vertikal bernilai nol. Keretakan jalinan kepercayaan sosial."})
        if not logs: st.success("✅ Tidak ditemukan anomali Modal Sosial.")
        else: st.warning("Anomali Terdeteksi:"); st.dataframe(pd.DataFrame(logs), use_container_width=True)


    # ==========================================
    # 🎯 MENU UTAMA: SIMULASI LABORATOTIUM CETAK BIRU 
    # ==========================================
    elif menu_pilihan == "🎯 Cetak Biru: Solusi Kelembagaan":
        st.subheader("Cetak Biru Tata Kelola & Simulasi Kebijakan Dinamis")
        st.markdown("Selamat datang di **Policy Simulation Lab**. Di menu ini, Anda dapat menguji efektivitas paket reformasi kelembagaan terhadap tingkat kesehatan ekosistem secara interaktif.")

        # --- STEP 1: INTERFAS PANEL KENDALI INTERVENSI ---
        st.write("#### 🎛️ Panel Kendali Intervensi Kebijakan:")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a: sim_a = st.checkbox("Paket A: Harmonization")
        with col_b: sim_b = st.checkbox("Paket B: Open Data")
        with col_c: sim_c = st.checkbox("Paket C: Accountability")
        with col_d: sim_d = st.checkbox("Paket D: Co-Management")

        # --- STEP 2: ENGINE PEMINDAI ANOMALI DASAR LINTAS DOMAIN ---
        # Rumus Kapasitas Penyimpangan Maksimum Jaringan Berarah
        # Kita uji 6 varians anomali utama dalam sistem pakar ini
        D_maksimal = max(6 * len(actors) * (len(actors) - 1), 1)
        
        raw_anomalies = []
        
        for i in range(len(actors)):
            for j in range(len(actors)):
                if i == j: continue
                actA, actB = actors[i], actors[j]
                
                # Pengambilan nilai parameter dasar
                p_formal = m_pow.loc[actA, actB]
                p_reverse = m_pow.loc[actB, actA]
                inf_val = m_inf.loc[actA, actB]
                inf_reverse = m_inf.loc[actB, actA]
                collab_val = m_collab.loc[actA, actB]
                collab_reverse = m_collab.loc[actB, actA]
                c_val = m_conf.loc[actA, actB]
                c_reverse = m_conf.loc[actB, actA]
                typeA = m_attr.loc[actA, "Tipe Lembaga"]
                typeB = m_attr.loc[actB, "Tipe Lembaga"]

                # 1. Domain Property Rights
                if i < j and c_val <= -4 and c_reverse <= -4 and p_formal >= 4 and p_reverse >= 4:
                    raw_anomalies.append({"AktorA": actA, "AktorB": actB, "Tipe": "⚠️ Institutional Deadlock", "Klaster": "Paket A"})
                if c_val <= -3 and p_formal >= 4 and p_reverse == 0:
                    raw_anomalies.append({"AktorA": actA, "AktorB": actB, "Tipe": "🚨 Institutional Exclusion", "Klaster": "Paket A"})
                
                # 2. Domain Transaction Cost
                if inf_val >= 4 and collab_val <= 1:
                    raw_anomalies.append({"AktorA": actA, "AktorB": actB, "Tipe": "🚨 Information Hoarding", "Klaster": "Paket B"})
                if i < j and (inf_val >= 3 or inf_reverse >= 3) and collab_val == 0 and collab_reverse == 0:
                    raw_anomalies.append({"AktorA": actA, "AktorB": actB, "Tipe": "⚠️ High Transaction Cost Barrier", "Klaster": "Paket B"})

                # 3. Domain Principal Agent
                if p_formal >= 4 and inf_reverse >= 4:
                    raw_anomalies.append({"AktorA": actA, "AktorB": actB, "Tipe": "🚨 Potential Agency Capture", "Klaster": "Paket C"})
                
                # 4. Domain Social Capital
                if typeA == "Formal" and typeB == "Informal" and collab_reverse == 0:
                    raw_anomalies.append({"AktorA": actB, "AktorB": actA, "Tipe": "🚨 Low Linking Capital", "Klaster": "Paket D"})

        # --- STEP 3: ENGINE EVALUASI DAMPAK SIMULASI & HITUNG HEALTH SCORE ---
        D_aktual_awal = len(raw_anomalies)
        health_score_awal = int((1 - (D_aktual_awal / D_maksimal)) * 100)
        
        # Evaluasi kondisi pasca intervensi
        active_anomalies_pasca = []
        ledger_data = []

        for item in raw_anomalies:
            is_resolved = False
            if item["Klaster"] == "Paket A" and sim_a: is_resolved = True
            elif item["Klaster"] == "Paket B" and sim_b: is_resolved = True
            elif item["Klaster"] == "Paket C" and sim_c: is_resolved = True
            elif item["Klaster"] == "Paket D" and sim_d: is_resolved = True
            
            status_pasca = "✅ RESOLVED" if is_resolved else "🚨 ANOMALI"
            intervensi_aktif = item["Klaster"] if is_resolved else "Belum Diintervensi"
            
            if not is_resolved:
                active_anomalies_pasca.append(item)
                
            ledger_data.append({
                "Hubungan Hub": f"{item['AktorA']} ↔ {item['AktorB']}" if "Deadlock" in item["Tipe"] or "Barrier" in item["Tipe"] else f"{item['AktorA']} → {item['AktorB']}",
                "Anomali Kelembagaan": item["Tipe"],
                "Status Aktual": "🚨 ANOMALI",
                "Status Pasca Simulasi": status_pasca,
                "Intervensi Kebijakan": intervensi_aktif
            })

        D_aktual_pasca = len(active_anomalies_pasca)
        health_score_pasca = int((1 - (D_aktual_pasca / D_maksimal)) * 100)
        delta_growth = health_score_pasca - health_score_awal

        # --- STEP 4: VISUALISASI METRIK KESEHATAN SISTEM ---
        st.write("---")
        st.write("#### 📊 Indikator Kesehatan Sistem Kelembagaan (System Health Score):")
        met1, met2 = st.columns(2)
        with met1:
            st.metric(label="Kesehatan Sistem Aktual (Kondisi Riil)", value=f"{health_score_awal}%", delta="Kondisi Awal", delta_color="inverse")
        with met2:
            st.metric(label="Kesehatan Sistem Pasca Simulasi (Proyeksi)", value=f"{health_score_pasca}%", delta=f"+{delta_growth}% Kenaikan" if delta_growth > 0 else "0% Stabil")

        # --- STEP 5: VISUALISASI TABEL LEDGER DAMPAK KOMPARATIF ---
        st.write("---")
        st.write("#### 📜 Policy Impact Ledger (Daftar Jejak Dampak Kebijakan):")
        
        if not ledger_data:
            st.success("✅ **Sistem Konstitusi Aman:** Tidak ditemukan kontradiksi relasi strategis horizontal maupun vertikal. Struktur tata kelola berada pada efisiensi *Pareto Optimal* (Health Score: 100%).")
        else:
            df_ledger = pd.DataFrame(ledger_data)
            st.dataframe(df_ledger, use_container_width=True)

        # --- STEP 6: DRAF REKOMENDASI TEKS GENERIK (DIPICU SECARA KONDISIONAL) ---
        st.write("---")
        st.write("#### 🏛️ Lembar Rekomendasi Cetak Biru Kebijakan:")
        
        unique_types = set([item["Tipe"] for item in raw_anomalies])
        
        if not unique_types:
            st.info("Seluruh ekosistem bersih dari anomali struktural.")
        else:
            if "⚠️ Institutional Deadlock" in unique_types or "🚨 Institutional Exclusion" in unique_types:
                with st.expander("🏛️ KLASTER A: Jurisdictional Harmonization & Property Rights Redesign", expanded=True):
                    st.write("**Rekomendasi Dokumen Hukum (Clear-cut Boundaries):**")
                    st.write("- Terbitkan Surat Keputusan (SK) Bersama Kepala Daerah atau Peraturan Daerah (Perda) baru untuk memotong tumpang tindih otoritas regulasi di lapangan.")
                    st.write("- Berikan kepastian hukum formal tertulis bagi hak kelola pranata informal/lokal guna menghindari peminggiran sepihak.")

            if "🚨 Information Hoarding" in unique_types or "⚠️ High Transaction Cost Barrier" in unique_types:
                with st.expander("📊 KLASTER B: Information Symmetry & Transaction Cost Reduction", expanded=True):
                    st.write("**Rekomendasi Dokumen Aturan (Open-Data Manifest):**")
                    st.write("- Wajibkan audit transparansi data volume hulu-hilir sebagai klausul mutlak pemberian izin operasional konsesi swasta.")
                    st.write("- Bangun platform pangkalan data digital tunggal terintegrasi untuk memangkas tingginya biaya transaksi birokrasi.")

            if "🚨 Potential Agency Capture" in unique_types:
                with st.expander("📜 KLASTER C: Performance-Based Accountability (Anti-Capture Mechanism)", expanded=True):
                    st.write("**Rekomendasi Dokumen Kontrak (Performance Contracting):**")
                    st.write("- Ubah model ikatan kerja sama operasional dengan pihak ketiga dari sistem serapan anggaran konvensional menjadi *Performance-Based Contracting* berbasis output riil bersih.")
                    st.write("- Bentuk komisi pengawas independen tripartit guna memutus rantai pembajakan regulasi.")

            if "🚨 Low Linking Capital" in unique_types:
                with st.expander("🌱 KLASTER D: Ostromian Co-Management & Social Trust Integration", expanded=True):
                    st.write("**Rekomendasi Dokumen Pengelolaan (Polycentric Governance):**")
                    st.write("- Cegah pemaksaan penegakan aturan hukum *top-down* yang kaku ketika tingkat kepercayaan vertikal berada di titik nadir.")
                    st.write("- Pelembagakan mekanisme Pengelolaan Bersama (*Co-Management*) dengan memberikan jaminan kuota zonasi wilayah kerja resmi bagi komunitas lokal.")
