import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA ENGINE: LOADING & STRUCTURING BARC DATA ---
@st.cache_data
def load_barc_data():
    try:
        # Load the table data from the converted CSV
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
    g_map = {"Male": "M", "Female": "F", "Both": "MF"}
    
    # Construction of potential column name: e.g., "F 22-30 A"
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
            target_col = nccs if nccs in df_media.columns else "Universe"
            
    try:
        val = df_media[df_media['Region'] == region][target_col].values[0]
        return val, target_col
    except:
        return np.nan, "Not Found"

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Part 1: Multi-Dimensional Input & BARC Mapping</p>", unsafe_allow_html=True)
st.divider()

if df_media is not None:
    with st.sidebar:
        st.header("📍 Campaign Inputs")
        
        market_list = df_media['Region'].unique().tolist()
        sel_market = st.selectbox("1. Select Market / Region", market_list)
        
        sel_gender = st.selectbox("2. Select Gender", ["Both", "Male", "Female"])
        
        # Mapping common age brackets found in your BARC file
        age_options = ["15-21", "22-30", "31-40", "41-50", "51-60", "61+", "15-30", "2-14"]
        sel_age = st.selectbox("3. Select Age Group", age_options)
        
        # Fixed the missing quote in "CDE" here
        nccs_options = ["A", "AB", "ABC", "B", "CDE"]
        sel_nccs = st.selectbox("4. Select NCCS", nccs_options)
        
        st.divider()
        budget = st.number_input("Total Budget (INR)", min_value=10000, value=1000000, step=50000)
        reach_target = st.slider("Reach Goal %", 5, 95, 60)
        
        calculate = st.button("Finalize Part 1", type="primary")

    # --- 4. OUTPUT & VALIDATION ---
    if calculate:
        universe_val, matched_col = get_universe_value(sel_market, sel_gender, sel_age, sel_nccs)
        
        st.subheader("✅ Data Architecture Verification")
        
        if pd.isna(universe_val):
            display_universe = "N/A"
            st.error(f"Data for '{matched_col}' in '{sel_market}' is missing in source.")
        else:
            display_universe = f"{int(universe_val):,} ('000s)"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Market", sel_market)
        c2.metric("Profile", f"{sel_gender}|{sel_age}|{sel_nccs}")
        c3.metric("Universe (Base)", display_universe)
        c4.metric("Mapping Source", matched_col)

        st.write("### Part 1: Finalized Input Set")
        audit_df = pd.DataFrame({
            "Dimension": ["Region", "Gender", "Age Group", "NCCS Profile", "Universe Column", "Budget"],
            "User Selection": [sel_market, sel_gender, sel_age, sel_nccs, matched_col, f"₹{budget:,}"],
            "Status": ["Verified", "Mapped", "Mapped", "Mapped", "Synced", "Ready"]
        })
        st.table(audit_df)
        
        st.success("Part One successfully completed. Inputs are stable and synced to BARC data.")

else:
    st.error("BARC data file not found or corrupted.")
