import streamlit as st
from modules import data_loader, ui_components

st.set_page_config(
    page_title="Ensiklopedia Pupuk & Pestisida | AgriSensa",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; }
    h1 { color: #2E7d32; }
    .stSelectbox label { color: #2E7d32; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/book-shelf.png", width=80)
        st.title("AgriSensa Knowledge")
        
        menu = st.radio("Kategori", ["Beranda", "📊 Dashboard Pintar", "🌱 Pupuk (Fertilizer)", "☠️ Pestisida (Pesticide)", "🤖 Rekomendasi Cerdas"])
        
        st.info("Referensi Global Terpercaya untuk Praktik Pertanian Berkelanjutan.")
        st.caption("© 2026 AgriSensa - Encyclopedia")

    # Routing
    if menu == "Beranda":
        show_home()
    elif "Dashboard" in menu:
        show_smart_dashboard()
    elif "Pupuk" in menu:
        show_encyclopedia("fertilizers", "Ensiklopedi Pupuk")
    elif "Pestisida" in menu:
        show_encyclopedia("pesticides", "Ensiklopedi Pestisida")
    elif "Rekomendasi" in menu:
        show_recommendation()

def show_recommendation():
    st.title("🤖 Sistem Rekomendasi Cerdas")
    st.markdown("Gunakan AI untuk menentukan tanaman terbaik dan kebutuhan pupuk berdasarkan data tanah Anda.")
    
    from modules.recommender import CropRecommender, FertilizerRecommender
    
    tab1, tab2 = st.tabs(["🌾 Rekomendasi Tanaman", "🧪 Kalkulator Pupuk"])
    
    # --- CROP RECOMMENDER ---
    with tab1:
        st.subheader("Cari Tanaman yang Cocok")
        st.warning("Masukkan data kondisi lingkungan lahan Anda:")
        
        col1, col2 = st.columns(2)
        with col1:
            n = st.number_input("Nitrogen (N) - ppm", 0, 140, 90)
            p = st.number_input("Fosfor (P) - ppm", 0, 145, 42)
            k = st.number_input("Kalium (K) - ppm", 0, 205, 43)
            ph = st.number_input("pH Tanah", 0.0, 14.0, 6.5)
        with col2:
            temp = st.number_input("Suhu (°C)", 10.0, 45.0, 20.8)
            humidity = st.number_input("Kelembaban Udara (%)", 10.0, 100.0, 82.0)
            rainfall = st.number_input("Curah Hujan (mm)", 0.0, 300.0, 202.9)
            
        if st.button("🔍 Analisis Kecocokan Lahan"):
            rec = CropRecommender()
            results = rec.get_recommendation(n, p, k, temp, humidity, ph, rainfall)
            
            if results:
                st.success(f"✅ Tanaman yang Paling Cocok: **{results[0].upper()}**")
                if len(results) > 1:
                    st.info(f"Alternatif lain: {', '.join([r.upper() for r in results[1:]])}")
            else:
                st.error("Data tidak cukup untuk memberikan rekomendasi.")

    # --- FERTILIZER CALC ---
    with tab2:
        st.subheader("Hitung Kekurangan Nutrisi")
        rec_fert = FertilizerRecommender()
        crops = rec_fert.get_crop_list()
        
        selected_crop = st.selectbox("Pilih Tanaman yang akan ditanam:", crops)
        
        st.markdown("**Kondisi Tanah Saat Ini:**")
        c1, c2, c3, c4 = st.columns(4)
        curr_n = c1.number_input("N (Saat Ini)", 0, 200, 0, key="fn")
        curr_p = c2.number_input("P (Saat Ini)", 0, 200, 0, key="fp")
        curr_k = c3.number_input("K (Saat Ini)", 0, 200, 0, key="fk")
        curr_ph = c4.number_input("pH (Saat Ini)", 0.0, 14.0, 6.0, key="fph")
        
        if st.button("🧪 Hitung Dosis Pupuk"):
            analysis = rec_fert.calculate_needs(selected_crop, curr_n, curr_p, curr_k, curr_ph)
            
            if analysis:
                st.write("---")
                st.markdown(f"### Hasil Analisis untuk {selected_crop.upper()}")
                
                # Visual Comparison
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.caption("Target Kebutuhan (Ideal)")
                    st.json(analysis['target'])
                with col_res2:
                    st.caption("Defisit (Kekurangan)")
                    st.json(analysis['deficit'])
                
                st.subheader("💡 Rekomendasi Tindakan:")
                for adv in analysis['advice']:
                    st.markdown(f"- {adv}")
            else:
                st.error("Gagal menghitung. Cek data tanaman.")

def show_home():
    st.title("📚 Pusat Pengetahuan AgriSensa")
    st.markdown("### Referensi Lengkap Pupuk & Pestisida")
    
    c1, c2 = st.columns(2)
    with c1:
        st.success("### 🌱 Pupuk")
        st.markdown("Panduan lengkap mengenai nutrisi tanaman, baik kimia maupun organik.")
        st.markdown("- **Topik**: Makro (NPK), Mikro, Organik, Hayati.")
    with c2:
        st.warning("### ☠️ Pestisida")
        st.markdown("Database pengendalian hama dan penyakit dengan panduan keamanan.")
        st.markdown("- **Topik**: Insektisida, Fungisida, Herbisida.")

def show_encyclopedia(category, title):
    st.title(f"📖 {title}")
    
    # Search
    query = st.text_input("🔍 Cari (Nama/Deskripsi)...", placeholder=f"Cari dalam {title}...")
    
    if category == "pesticides":
        t1, t2 = st.tabs(["⭐ Populer (Kurasi)", "💊 Database Kementan (Lengkap)"])
        
        with t1:
            render_card_list(category, query)
            
        with t2:
            st.markdown("### Database Hama & Penyakit (1800+ Entri)")
            p_type = st.radio("Jenis Pestisida:", ["umum", "teknis", "ekspor"], horizontal=True, format_func=lambda x: x.title())
            
            df_pest = data_loader.load_pesticide_csv(p_type)
            
            if not df_pest.empty:
                # Search within dataframe
                if query:
                    mask = df_pest.apply(lambda x: x.astype(str).str.contains(query, case=False).any(), axis=1)
                    df_pest = df_pest[mask]
                
                st.dataframe(df_pest, use_container_width=True, hide_index=True)
                st.caption(f"Menampilkan {len(df_pest)} data dari database resmi.")
            else:
                st.warning("Database sedang memuat atau kosong.")
    else:
        # Standard view for Fertilizers
        render_card_list(category, query)

def render_card_list(category, query):
    if query:
        items = data_loader.search_items(category, query)
    else:
        items = data_loader.load_data(category)
    
    st.markdown(f"**Menampilkan {len(items)} entri:**")
    st.markdown("---")
    
    for item in items:
        if category == "fertilizers":
            ui_components.render_fertilizer_card(item)
        else:
            ui_components.render_pesticide_card(item)

def show_smart_dashboard():
    st.title("📊 Dashboard Pintar AgriSensa")
    st.markdown("Analisis data historis untuk keputusan pertanian yang lebih baik.")
    
    from modules.smart_dashboard import SmartDashboard
    from modules.recommender import FertilizerRecommender
    
    dashboard = SmartDashboard()
    
    tab1, tab2, tab3 = st.tabs(["🗺️ Peta Produktivitas", "💰 Kalkulator Profitabilitas", "🧪 Rekomendasi Terlokalisasi"])
    
    # --- PRODUCTIVITY ---
    with tab1:
        st.subheader("Analisis Produktivitas Wilayah")
        
        prov_map, commodities = dashboard.get_location_options()
        
        if not commodities:
            st.error("Data tidak tersedia.")
        else:
            selected_comm = st.selectbox("Pilih Komoditas:", commodities)
            
            if selected_comm:
                stats = dashboard.get_productivity_stats(selected_comm)
                
                if not stats.empty:
                    st.markdown(f"**Top 20 Daerah dengan Produktivitas Tertinggi untuk {selected_comm}**")
                    st.bar_chart(stats, x="District", y="Production_KgHa", color="#2E7d32")
                    
                    best = stats.iloc[0]
                    st.success(f"🏆 Daerah Terbaik: **{best['District']}, {best['Province']}** ({best['Production_KgHa']:.0f} Kg/Ha)")
                else:
                    st.info("Tidak ada data untuk komoditas ini.")

    # --- PROFITABILITY ---
    with tab2:
        st.subheader("Simulasi Bisnis Tani")
        
        prov_map, commodities = dashboard.get_location_options()
        
        col1, col2 = st.columns(2)
        with col1:
            prov = st.selectbox("Provinsi:", list(prov_map.keys()))
            dist = st.selectbox("Kabupaten:", prov_map.get(prov, []))
        with col2:
            comm = st.selectbox("Komoditas:", commodities, key="p_comm")
            area = st.number_input("Luas Lahan (Ha):", 0.1, 100.0, 1.0, 0.1)
            
        if st.button("🧮 Hitung Estimasi ROI"):
            roi_data = dashboard.calculate_roi(prov, dist, comm, area)
            
            if roi_data:
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.metric("Total Biaya (Estimasi)", f"Rp {roi_data['total_cost']:,.0f}")
                    st.metric("Potensi Pendapatan", f"Rp {roi_data['total_revenue']:,.0f}")
                with res_col2:
                    profit_color = "normal" if roi_data['profit'] > 0 else "off"
                    st.metric("Keuntungan Bersih", f"Rp {roi_data['profit']:,.0f}", delta=f"{roi_data['roi']:.1f}% ROI", delta_color=profit_color)
                    st.caption(f"*Yield*: {roi_data['yield_ha']:.0f} Kg/Ha | *Harga*: Rp {roi_data['price_per_kg']:,}/Kg")
            else:
                st.warning("Data historis tidak ditemukan untuk kombinasi lokasi dan komoditas ini.")

    # --- SMART REC ---
    with tab3:
        st.subheader("Rekomendasi Pupuk Berbasis Data")
        st.info("Sistem akan mencari lokasi dengan karakteristik tanah mirip yang memiliki hasil panen tinggi.")
        
        c1, c2, c3, c4 = st.columns(4)
        n = c1.number_input("N (Index)", 0, 200, 100)
        p = c2.number_input("P (Index)", 0, 200, 100)
        k = c3.number_input("K (Index)", 0, 200, 100)
        ph = c4.number_input("pH Tanah", 0.0, 14.0, 6.5)
        
        if st.button("🔍 Cari Rekomendasi Historis"):
            rec_fert = FertilizerRecommender()
            res = rec_fert.get_data_driven_recommendation(n, p, k, ph)
            
            if res:
                st.success(f"Ditemukan {res['match_count']} data lahan sukses yang mirip!")
                st.markdown("### Rekomendasi Dosis:")
                
                col_d1, col_d2, col_d3 = st.columns(3)
                col_d1.metric("Urea", f"{res['Urea']:.1f} Kg/Ha")
                col_d2.metric("SP-36", f"{res['SP-36']:.1f} Kg/Ha")
                col_d3.metric("KCl", f"{res['KCl']:.1f} Kg/Ha")
            else:
                st.warning("Data referensi tidak cukup.")

if __name__ == "__main__":
    main()
