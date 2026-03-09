import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA ENGINE: LOADING & STRUCTURING BARC DATA ---
@st.cache_data
def load_barc_data():
    # Load the table data from the CSV conversion of your excel
    try:
        df = pd.read_csv('barc_data.xlsx.xlsx - Table.csv')
        
        # Set headers correctly (First row contains the labels)
        header = df.iloc[0].values
        df = df[1:].copy()
        df.columns = header
        
        # Rename first column to 'Region' for clarity
        df = df.rename(columns={df.columns[0]: 'Region'})
        
        # Clean data: convert 'n.a' strings to NaN and ensure numeric types
        df = df.replace('n.a', np.nan)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna(subset=['Region'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df_media = load_barc_data()

# --- 2. MAPPING ENGINE: MULTI-DIMENSIONAL SEARCH ---
def get_universe_value(region, gender, age, nccs):
    """
    Maps user selections to the specific BARC column naming conventions.
    """
    g_map = {"Male": "M", "Female": "F", "Both": "MF"}
    
    # Logic: Attempt to construct the column name based on file patterns
    # Pattern: [Gender] [Age] [NCCS] -> e.g., "F 22-30 A"
    target_col = f"{g_map[gender]} {age} {nccs}"
    
    # Fallback Logic: If the specific cut is not in the Excel, try broader segments
    if target_col not in df_media.columns:
        if nccs == "A" and age == "All" and gender == "Both":
            target_col = "A"
        elif age != "All" and gender == "Both" and nccs == "All":
            target_col = age
        elif gender != "Both" and age == "All" and nccs == "All":
            target_col = "Male" if gender == "Male" else "Female"
        else:
            # Defaults to NCCS selection if no gender/age cross-section exists
            target_col = nccs if nccs in df_media.columns else "Universe"
            
    try:
        val = df_media[df_media['Region'] == region][target_col].values[0]
        return val, target_col
    except:
        return np.nan, "Not Found"

# --- 3. UI: THE RESTRUCTURED INPUT TASKBAR ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-
