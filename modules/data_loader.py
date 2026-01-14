import json
import os
import pandas as pd

# Resolve data directory relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_data(category):
    """
    Load data from JSON files.
    :param category: 'fertilizers' or 'pesticides'
    :return: List of dictionaries
    """
    file_path = os.path.join(DATA_DIR, f"{category}.json")
    
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_as_dataframe(category):
    """Load data and convert to Pandas DataFrame for searching."""
    data = load_data(category)
    return pd.DataFrame(data)

def search_items(category, query):
    """Search for items by name or description."""
    data = load_data(category)
    query = query.lower()
    
    results = []
    for item in data:
        if query in item["name"].lower() or query in item.get("description", "").lower():
            results.append(item)
    return results

def load_pesticide_csv(pest_type="umum"):
    """
    Load pesticide data from CSV.
    :param pest_type: 'umum', 'teknis', or 'ekspor'
    :return: Pandas DataFrame
    """
    file_map = {
        "umum": "pestisida_umum.csv",
        "teknis": "pestisida_teknis.csv",
        "ekspor": "pestisida_ekspor.csv"
    }
    
    filename = file_map.get(pest_type, "pestisida_umum.csv")
    file_path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(file_path)
        
        # Clean column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        # Normalize columns
        # Original: ['no', 'merek dagang', 'bahan aktif', 'deskrispi', 'pembuat']
        # Target: ['Name', 'Active_Ingredient', 'Description', 'Manufacturer']
        
        column_map = {
            'merek dagang': 'Name',
            'bahan aktif': 'Active_Ingredient',
            'deskrispi': 'Description', # Handle typo in CSV
            'deskripsi': 'Description', # Or correct spelling
            'pembuat': 'Manufacturer',
            'no': 'No'
        }
        
        df = df.rename(columns=column_map)
        
        # Select relevant columns
        cols = ['Name', 'Active_Ingredient', 'Description', 'Manufacturer']
        available_cols = [c for c in cols if c in df.columns]
        
        return df[available_cols]
    except Exception as e:
        print(f"Error loading pesticide CSV: {e}")
        return pd.DataFrame()
