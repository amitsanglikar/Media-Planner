import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

# --- 2. THE BULLETPROOF CSS ---
# This forces the specific colors from the mock and adds the card depth
st.markdown("""
    <style>
    /* Force a clean background for the whole app */
    .stApp {
        background-color: #F0F2F6 !important;
    }

    /* Modern Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1E3A8A;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    /* Container for the 'Input Taskbar' to look like the mock */
    .filter-container {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border: 1px solid #e6e9ef;
    }

    /* Styling the Main Header */
    .main-title {
        color: #1E3A8A;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 32px;
        margin-bottom: 0px;
    }
    
    /* KPI Card Simulation */
    div.element-container:has(div.card-style) {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #1E3A8A;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Change button color to the coral/red in your screenshot or the primary blue */
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE (Logic remains identical) ---
@st.cache_data
def load_barc_data():
    try:
        df = pd.read_csv('barc_data.xlsx.xlsx - Table.csv')
        header = df.iloc[0].values
        df = df[1:].copy()
        df.columns = header
        df = df.rename(columns={df.columns[0]: 'Region'})
        df = df.replace('n.a', np.nan)
        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['Region'])
    except:
        return None

df_media = load_barc_data()

def get_universe_value(region, gender, age, nccs):
    g_prefix = "MF" if gender == "Both" else ("M" if gender == "Male" else "F")
    patterns = [f"{g_prefix} {age} {nccs}", f"{age} {nccs}", f"{g_prefix} {nccs}", nccs, age, f"{g_prefix} {age}"]
    target_col = next((p for p in patterns if p in df_media.columns), "Universe")
    try:
        val = df_media[df_media['Region'] == region][target_col].values[0]
        return val, target_col
    except:
        return np.nan, "Not Found"

# --- 4. UI: BRANDING ---
st.markdown('<p class="main-title">🌐 Virtual Media Planner</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #64748B; margin-bottom: 25px;">Targeting & Audience Intelligence Engine</p>', unsafe_allow_html=True)

# --- 5. UI: THE COMMAND CENTER (White Box) ---
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("##### 📍 Audience & Market")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: sel_market = st.selectbox("Market / Region", df_media['Region'].unique().tolist() if df_media is not None else ["No Data"])
    with c2: sel_gender = st.selectbox("Gender", ["Both", "Male", "Female"])
    with c3: sel_age = st.selectbox("Age Group", ["15-30", "15-21", "22-30", "31-40", "41-50", "51-60", "61+", "2-14"])
    with c4: sel_nccs = st.selectbox("NCCS Category", ["AB", "A", "ABC", "B", "CDE"])
    
    c5, c6, c7 = st.columns([2, 2, 1])
    with c5: budget = st.number_input("Total Budget (INR)", min_value=10000, value=1000000, step=50000)
    with c6: reach_goal = st.slider("Reach Target (1+) %", 5, 95, 60)
    with c7: 
        st.write("##") # alignment
        calculate = st.button("Finalize Inputs")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. OUTPUT: RESULTS GRID ---
if calculate and df_media is not None:
    universe_val, matched_col = get_universe_value(sel_market, sel_gender, sel_age, sel_nccs)
    display_val = "N/A" if (pd.isna(universe_val) or universe_val == 0) else f"{int(universe_val):,} ('000s)"

    res_col1, res_col2 = st.columns([1, 1])
    
    with res_col1:
        st.markdown("### 📊 Validation Insights")
        # Custom Card 1
        st.metric(label="Universe Identified", value=display_val, delta=f"Column: {matched_col}")
        # Custom Card 2
        st.info(f"**Target Persona:** {sel_gender} | {sel_age} | {sel_nccs}")

    with res_col2:
        st.markdown("### ✅ System Sync")
        audit_df = pd.DataFrame({
            "Parameter": ["Region", "Demographics", "Source", "Budget"],
            "Value": [sel_market, f"{sel_gender} {sel_age}", matched_col, f"₹{budget:,}"],
            "Status": ["Verified ✅", "Mapped ✅", "Active ⚡", "Allocated ✅"]
        })
        st.table(audit_df)
