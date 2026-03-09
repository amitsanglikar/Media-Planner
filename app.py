import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA ENGINE: LOADING & CLEANING ---
@st.cache_data
def load_barc_data():
    try:
        # Loading the specific Table CSV from your BARC upload
        df = pd.read_csv('barc_data.xlsx.xlsx - Table.csv')
        
        # Row 0 is the actual header in this specific BARC export
        header = df.iloc[0].values
        df = df[1:].copy()
        df.columns = header
        
        # Standardizing the first column to 'Region'
        df = df.rename(columns={df.columns[0]: 'Region'})
        
        # Clean numeric data (handle 'n.a' and whitespace)
        df = df.replace('n.a', np.nan)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna(subset=['Region'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df_media = load_barc_data()

# --- 2. THE FUZZY MAPPING ENGINE ---
def get_universe_value(region, gender, age, nccs):
    """
    Tries multiple BARC naming conventions to find a match for the inputs.
    """
    # Map UI 'Both' to BARC 'MF'
    g_prefix = "MF" if gender == "Both" else ("M" if gender == "Male" else "F")
    
    # Define potential column name patterns found in the Excel
    patterns = [
        f"{g_prefix} {age} {nccs}",  # e.g., "MF 15-30 AB"
        f"{age} {nccs}",             # e.g., "15-30 AB"
        f"{g_prefix} {nccs}",        # e.g., "MF AB"
        nccs,                        # e.g., "AB"
        age,                         # e.g., "15-30"
        f"{g_prefix} {age}"          # e.g., "MF 15-30"
    ]
    
    target_col = None
    # Iterate through patterns to find the first one that exists in the CSV headers
    for pattern in patterns:
        if pattern in df_media.columns:
            target_col = pattern
            break
    
    if not target_col:
        target_col = "Universe" # Final fallback to Total Universe
            
    try:
        val = df_media[df_media['Region'] == region][target_col].values[0]
        return val, target_col
    except:
        return np.nan, "Not Found"

# --- 3. UI: THE TASKBAR ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Part 1: Input Taskbar & BARC Data Mapping</p>", unsafe_allow_html=True)
st.divider()

if df_media is not None:
    with st.sidebar:
        st.header("📍 Audience & Market")
        
        # 1. Market Selection
        market_list = df_media['Region'].unique().tolist()
        sel_market = st.selectbox("Market / Region", market_list)
        
        # 2. Gender Selection
        sel_gender = st.selectbox("Gender", ["Both", "Male", "Female"])
        
        # 3. Age Selection (Aligned with BARC headers)
        age_options = ["15-30", "15-21", "22-30", "31-40", "41-50", "51-60", "61+", "2-14"]
        sel_age = st.selectbox("Age Group", age_options)
        
        # 4. N
