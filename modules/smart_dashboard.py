import streamlit as st
import pandas as pd
import os

class SmartDashboard:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.pred_file = os.path.join(self.data_dir, 'dataset_untuk_prediksi.csv')
        self.rec_file = os.path.join(self.data_dir, 'dataset_untuk_rekomendasi_pupuk.csv')
        self.df_pred = self.load_prediction_data()
        self.df_rec = self.load_recommendation_data()

    @st.cache_data
    def load_prediction_data(_self):
        try:
            df = pd.read_csv(_self.pred_file)
            # Ensure numeric columns are actually numeric
            numeric_cols = ['Production_KgHa', 'InputPrice_Urea_RpKg', 'InputPrice_SP36_RpKg', 
                           'InputPrice_KCl_RpKg', 'Init_Capital_RpHa', 'Maintenance_Cost_RpHa',
                           'Prev_Yield_KgHa', 'Rain_mm', 'Temp_C']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
        except Exception as e:
            st.error(f"Error loading prediction data: {e}")
            return pd.DataFrame()

    @st.cache_data
    def load_recommendation_data(_self):
        try:
            return pd.read_csv(_self.rec_file)
        except Exception as e:
            # Silent fallback if file missing
            return pd.DataFrame()

    def get_productivity_stats(self, commodity):
        """
        Get productivity statistics for a specific commodity grouped by district.
        Returns: DataFrame sorted by Production_KgHa descending.
        """
        if self.df_pred.empty:
            return pd.DataFrame()
        
        df_filtered = self.df_pred[self.df_pred['Commodity'] == commodity].copy()
        
        if df_filtered.empty:
            return pd.DataFrame()
            
        # Group by Province & District
        stats = df_filtered.groupby(['Province', 'District'])['Production_KgHa'].mean().reset_index()
        stats = stats.sort_values('Production_KgHa', ascending=False)
        return stats.head(20) # Return top 20 districts

    def calculate_roi(self, province, district, commodity, land_area_ha):
        """
        Calculate potential ROI based on historical data for the region.
        """
        if self.df_pred.empty:
            return None
            
        # Filter data
        mask = (
            (self.df_pred['Province'] == province) & 
            (self.df_pred['District'] == district) & 
            (self.df_pred['Commodity'] == commodity)
        )
        data = self.df_pred[mask]
        
        if data.empty:
            return None
            
        # Use average of historical data for the region
        avg_data = data.mean(numeric_only=True)
        
        yield_per_ha = avg_data.get('Production_KgHa', 0)
        
        # Costs
        init_capital = avg_data.get('Init_Capital_RpHa', 0)
        maintenance = avg_data.get('Maintenance_Cost_RpHa', 0)
        
        # Estimate Fertilizer Cost if not explicitly in total capital (Dataset has input prices)
        # Assuming Init_Capital includes seeds etc, but let's be safe and use Init + Maint as base cost per ha
        cost_per_ha = init_capital + maintenance
        
        # Revenue
        # Note: Dataset doesn't have 'SalesPrice' column explicitly in the check output 
        # but usually Production * Price = Revenue. 
        # If Price is missing, we might need to assume a price or check if 'Revenue' exists.
        # Checking columns again: ..., 'InputPrice_Urea...', 'Init_Capital...', 'Pupuk_Urea...'
        # Did not see Commodity Price in the checked columns. 
        # We will estimate Revenue based on a lookup or user input if price is missing.
        # PROVISIONAL: Use a dummy price dict or prompt user. 
        # For now, let's assume a standard price map for demo.
        price_map = {
            'Padi': 6000,
            'Jagung': 4500,
            'Kedelai': 8000,
            'Bawang Merah': 25000,
            'Cabai': 30000
        }
        price_per_kg = price_map.get(commodity, 5000) # Default fallback
        
        total_revenue = yield_per_ha * price_per_kg * land_area_ha
        total_cost = cost_per_ha * land_area_ha
        profit = total_revenue - total_cost
        roi = (profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "yield_ha": yield_per_ha,
            "total_production": yield_per_ha * land_area_ha,
            "price_per_kg": price_per_kg,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "profit": profit,
            "roi": roi
        }

    def get_location_options(self):
        """Get unique Provinces and Districts for dropdowns"""
        if self.df_pred.empty:
            return {}, []
        
        provinces = sorted(self.df_pred['Province'].dropna().unique().tolist())
        commodities = sorted(self.df_pred['Commodity'].dropna().unique().tolist())
        
        # Map province to districts
        prov_dist_map = {}
        for prov in provinces:
            dists = self.df_pred[self.df_pred['Province'] == prov]['District'].dropna().unique().tolist()
            prov_dist_map[prov] = sorted(dists)
            
        return prov_dist_map, commodities
