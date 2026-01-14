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
        
        menu = st.radio("Kategori", ["Beranda", "🌱 Pupuk (Fertilizer)", "☠️ Pestisida (Pesticide)", "🤖 Rekomendasi Cerdas"])
        
        st.info("Referensi Global Terpercaya untuk Praktik Pertanian Berkelanjutan.")
        st.caption("© 2026 AgriSensa - Encyclopedia")

    # Routing
    if menu == "Beranda":
        show_home()
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

if __name__ == "__main__":
    main()
