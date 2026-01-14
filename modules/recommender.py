import pandas as pd
import os
import numpy as np

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CROP_DATA_PATH = os.path.join(DATA_DIR, "crop_recommendation.csv")
FERT_DATA_PATH = os.path.join(DATA_DIR, "fertilizer_recommendation.csv")
REAL_FERT_DATA_PATH = os.path.join(DATA_DIR, "dataset_untuk_rekomendasi_pupuk.csv")

class CropRecommender:
    def __init__(self):
        if os.path.exists(CROP_DATA_PATH):
            self.df = pd.read_csv(CROP_DATA_PATH)
            # Rename columns to standard internal names if necessary
            # Expected: Nitrogen (N), Fosforus (P), Kalium (K), Suhu, Kelembaban, pH, Curah Hujan, Label
        else:
            self.df = pd.DataFrame()

    def get_recommendation(self, n, p, k, temp, humidity, ph, rainfall):
        """
        Find top 3 recommendations based on nearest neighbor (Euclidean distance) of normalized features.
        """
        if self.df.empty:
            return []

        # Feature columns
        features = ['Nitrogen (N)', 'Fosforus (P)', 'Kalium (K)', 'Suhu', 'Kelembaban', 'pH', 'Curah Hujan']
        
        # Prepare input vector
        input_vector = np.array([n, p, k, temp, humidity, ph, rainfall])
        
        # Calculate distance for every row (Simplified KNN-1 approach per label, 
        # but here we just find closest rows and aggregate unique labels)
        
        # 1. Normalize dataset to avoid bias (simple min-max scaling relative to input range could work, 
        # but typically we should standardize. For simplicity in this demo, we compute raw distance
        # or we can assume the data ranges are somewhat comparable or weight them).
        # Let's use raw distance for now as standardizing requires persisting scaler stats.
        
        # Vectorized Euclidean Distance
        data_vectors = self.df[features].values
        distances = np.linalg.norm(data_vectors - input_vector, axis=1)
        
        self.df['distance'] = distances
        
        # Get top matches
        top_matches = self.df.sort_values('distance').head(20) # Look at top 20 closest points
        
        # Count frequency of labels in top matches
        recommendations = top_matches['Label'].value_counts().head(3).index.tolist()
        
        return recommendations

class FertilizerRecommender:
    def __init__(self):
        if os.path.exists(FERT_DATA_PATH):
            self.df = pd.read_csv(FERT_DATA_PATH)
        else:
            self.df = pd.DataFrame()
            
        if os.path.exists(REAL_FERT_DATA_PATH):
            self.real_df = pd.read_csv(REAL_FERT_DATA_PATH)
        else:
            self.real_df = pd.DataFrame()

    def get_crop_list(self):
        """Return list of supported crops."""
        if self.df.empty:
            return []
        return sorted(self.df['Tanaman'].unique().tolist())

    def calculate_needs(self, crop, n, p, k, ph):
        """
        Calculate nutrient deficit.
        """
        if self.df.empty:
            return None
            
        # Filter by crop
        crop_data = self.df[self.df['Tanaman'] == crop]
        if crop_data.empty:
            return None
            
        # Get target values (Average if multiple rows, though dataset seems unique per crop)
        target = crop_data.iloc[0]
        
        target_n = target['Nitrogen (N)']
        target_p = target['Fosforus (P)']
        target_k = target['Kalium (K)']
        target_ph = target['pH']
        
        # Calculate Deficits (Target - Current)
        # If Current > Target, Deficit is 0
        def_n = max(0, target_n - n)
        def_p = max(0, target_p - p)
        def_k = max(0, target_k - k)
        
        advice = []
        
        if def_n > 0:
            advice.append(f"**Kekurangan Nitrogen ({def_n:.1f} ppm):** Gunakan Urea atau ZA.")
        if def_p > 0:
            advice.append(f"**Kekurangan Fosfor ({def_p:.1f} ppm):** Gunakan SP-36 atau TSP.")
        if def_k > 0:
            advice.append(f"**Kekurangan Kalium ({def_k:.1f} ppm):** Gunakan KCl atau ZK.")
            
        if abs(ph - target_ph) > 0.5:
            if ph < target_ph:
                advice.append(f"**pH Terlalu Rendah ({ph} vs {target_ph}):** Tambahkan Kapur Dolomit.")
            else:
                advice.append(f"**pH Terlalu Tinggi ({ph} vs {target_ph}):** Tambahkan Belerang/Sulfur.")
                
        if not advice:
            advice.append("✅ Kondisi tanah sudah optimal untuk tanaman ini.")
            
        return {
            "target": {"N": target_n, "P": target_p, "K": target_k, "pH": target_ph},
            "deficit": {"N": def_n, "P": def_p, "K": def_k},
            "advice": advice
        }

    def get_data_driven_recommendation(self, n, p, k, ph):
        """
        Get recommendations based on historical successful yield data.
        Finds the closest soil matches in the dataset.
        """
        if self.real_df.empty:
            return None
            
        # Features to match: Soil_pH, Soil_N_index, Soil_P_index, Soil_K_index
        # Note: 'index' in dataset might be scaled differently than raw ppm.
        # Assuming input is raw numeric comparable to dataset or we need normalization.
        # Let's inspect dataset values in logic (or assume raw values for now as per plan).
        
        # Simple Euclidean distance on soil properties
        # Target Features
        features = ['Soil_pH', 'Soil_N_index', 'Soil_P_index', 'Soil_K_index']
        
        # Drop rows with missing values in features
        df_clean = self.real_df.dropna(subset=features)
        
        if df_clean.empty:
            return None
            
        data_matrix = df_clean[features].values
        input_vector = np.array([ph, n, p, k])
        
        # Calculate distances
        distances = np.linalg.norm(data_matrix - input_vector, axis=1)
        
        # Get top 5 closest matches
        top_indices = np.argsort(distances)[:5]
        top_matches = df_clean.iloc[top_indices]
        
        # Calculate average recommendation from these top matches
        avg_urea = top_matches['Pupuk_Urea_kgHa'].mean()
        avg_sp36 = top_matches['Pupuk_SP36_kgHa'].mean()
        avg_kcl = top_matches['Pupuk_KCl_kgHa'].mean()
        
        return {
            "Urea": avg_urea,
            "SP-36": avg_sp36,
            "KCl": avg_kcl,
            "match_count": len(top_matches)
        }
