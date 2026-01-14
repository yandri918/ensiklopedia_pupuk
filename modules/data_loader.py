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
