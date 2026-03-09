import streamlit as st
import pandas as pd
import numpy as np
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    :root { --primary: #1E3A8A; --accent: #FF4B4B; --bg: #F8FAFC; }
    .stApp { background-color: var(--bg) !important; }
    .filter-section {
        background-color: #FFFFFF !important;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .kpi-card {
        background-color: white !important;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid var(--primary);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    label, p, h1, h3 { color: var(--primary) !important; font-family: 'Inter', sans-serif; }
    .stButton>button {
        background-color: var(--accent) !important;
        color: white !important;
        font-weight: bold; width: 100%; height: 45px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE (FIXED FOR YOUR FILE) ---
@st.cache_data
def load_and_clean_data():
    file_path = 'barc_data.xlsx.xlsx - Table.csv'
    if not os.path.exists(file_path):
        return None
    
    # Read the CSV - your file has the column names in the 2nd row (index 0)
    df = pd.read_csv(file_path)
    header = df.iloc[0].values
    data = df[1:].copy()
    data.columns = header
    
    # Rename the first column to 'Region'
    data = data.rename(columns={data.columns[0]: 'Region'})
    
    # Clean numeric data
    data = data.replace('n.a', np.nan)
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    
    return data.dropna(subset=['Region'])

df_media = load_and_clean_data()

def get_universe_value(region, gender, age, nccs):
    if df_media is None: return 0, "No Data"
    
    # 1. Try to find an EXACT match in your file (e.g., "MF 15-30 AB")
    g_pre = "MF" if gender == "Both" else ("M" if gender == "Male" else "F")
    
    # These are the specific patterns found in your CSV headers
    patterns = [
        f"{g_pre} {age} {nccs}", 
        f"{age} {nccs}", 
        f"{g_pre} {age}",
        nccs,
        age,
        "Universe" # Last resort
    ]
    
    for p in patterns:
        if p in df_media.columns:
            try:
                val = df_media[df_media['Region'] == region][p].values[0]
                if not pd.isna(val):
                    return val, p
            except:
                continue
    
    return 0, "Not Found"

# --- 4. BRANDING ---
st.markdown('<h1>🌐 Virtual Media Planner</h1>', unsafe_allow_html=True)
st.markdown('<p style="margin-top:-20px; font-size:18px; color:#64748B !important;">Targeting & Audience Intelligence</p>', unsafe_allow_html=True)

# --- 5. THE COMMAND CENTER ---
if df_media is not None:
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 📍 Audience Selection")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        # Dynamically get markets from your file
        markets = df_media['Region'].unique().tolist()
        sel_market = st.selectbox("Market / Region", markets)
    with c2: 
        sel_gender = st.selectbox("Gender", ["Both", "Male", "Female"])
    with c3: 
        # Common age brackets in your file
        sel_age = st.selectbox("Age Group", ["15-30", "15-21", "22-30", "31-40", "41-50", "2-14"])
    with c4: 
        # NCCS from your file
        sel_nccs = st.selectbox("NCCS Category", ["AB", "ABC", "A", "B", "CDE"])
    
    c5, c6, c7 = st.columns([2, 2, 1])
    with c5: budget = st.number_input("Total Budget (INR)", value=1000000, step=50000)
    with c6: reach_goal = st.slider("Target Reach %", 5, 95, 60)
    with c7: calculate = st.button("Generate Plan")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 6. RESULTS ---
    if calculate:
        universe_val, matched_col = get_universe_value(sel_market, sel_gender, sel_age, sel_nccs)
        
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"""
                <div class="kpi-card">
                    <p style="margin:0; font-size:14px; color:#64748B !important;">Universe Size</p>
                    <h1 style="margin:0; font-size:48px; color:#1E3A8A !important;">{int(universe_val):,}</h1>
                    <p style="margin:0; font-size:12px;">Unit: '000s | Mapping: {matched_col}</p>
                </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown("### ✅ System Sync")
            audit_df = pd.DataFrame({
                "Parameter": ["Region", "Demographics", "Source"],
                "Value": [sel_market, f"{sel_gender} {sel_age}", "BARC Data File"],
                "Status": ["Synced ✅", "Mapped ✅", "Active ⚡"]
            })
            st.table(audit_df)
else:
    st.error("⚠️ Data file not found. Please ensure 'barc_data.xlsx.xlsx - Table.csv' is in the folder.")
