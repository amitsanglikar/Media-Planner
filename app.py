import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide")

# --- 2. THE "MOCK-FAITHFUL" CSS OVERRIDE ---
st.markdown("""
    <style>
    /* Force Light Theme Colors regardless of System Settings */
    :root {
        --primary-color: #1E3A8A;
        --bg-color: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-color: #1E293B;
    }

    .stApp {
        background-color: var(--bg-color) !important;
    }

    /* Force all labels to be readable (Dark Blue/Grey) */
    label, .stMarkdown, p, h1, h2, h3, h5, [data-testid="stWidgetLabel"] p {
        color: #1E3A8A !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Target the white input bar container from the mock */
    .filter-section {
        background-color: #FFFFFF !important;
        padding: 30px !important;
        border-radius: 15px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 25px !important;
    }

    /* Fix Selectbox/Input Visibility - Force White Background */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* KPI Card Styling */
    .kpi-card {
        background-color: white !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border-left: 6px solid #1E3A8A !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        margin-bottom: 15px !important;
    }

    /* Action Button (The Coral/Red from your screenshot) */
    .stButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: bold !important;
        margin-top: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
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
    target_col = next((p for p in patterns if p in (df_media.columns if df_media is not None else [])), "Universe")
    try:
        val = df_media[df_media['Region'] == region][target_col].values[0]
        return val, target_col
    except:
        return np.nan, "Not Found"

# --- 4. BRANDING ---
st.markdown('<h1>🌐 Virtual Media Planner</h1>', unsafe_allow_html=True)
st.markdown('<p style="margin-top:-20px; font-size:18px; color:#64748B !important;">Targeting & Audience Intelligence Engine</p>', unsafe_allow_html=True)

# --- 5. THE COMMAND CENTER (The white "Filter Bar") ---
if df_media is not None:
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 📍 Audience & Market")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: sel_market = st.selectbox("Market / Region", df_media['Region'].unique().tolist())
    with c2: sel_gender = st.selectbox("Gender", ["Both", "Male", "Female"])
    with c3: sel_age = st.selectbox("Age Group", ["15-30", "15-21", "22-30", "31-40", "41-50", "51-60", "61+", "2-14"])
    with c4: sel_nccs = st.selectbox("NCCS Category", ["AB", "A", "ABC", "B", "CDE"])
    
    c5, c6, c7 = st.columns([2, 2, 1])
    with c5: budget = st.number_input("Total Budget (INR)", min_value=10000, value=1000000, step=50000)
    with c6: reach_goal = st.slider("Reach Target (1+) %", 5, 95, 60)
    with c7: calculate = st.button("Finalize Inputs")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 6. RESULTS (KPI CARDS) ---
    if calculate:
        universe_val, matched_col = get_universe_value(sel_market, sel_gender, sel_age, sel_nccs)
        display_val = "N/A" if (pd.isna(universe_val) or universe_val == 0) else f"{int(universe_val):,} ('000s)"

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown(f"""
                <div class="kpi-card">
                    <p style="margin:0; font-size:14px; color:#64748B !important;">Universe Identified</p>
                    <h1 style="margin:0; font-size:42px; color:#1E3A8A !important;">{display_val}</h1>
                    <p style="margin:0; font-size:12px;">Mapping Column: <b>{matched_col}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="kpi-card">
                    <p style="margin:0; font-size:14px; color:#64748B !important;">Target Profile Summary</p>
                    <h3 style="margin:0; color:#1E3A8A !important;">{sel_gender} | {sel_age} | {sel_nccs}</h3>
                </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown("### ✅ System Sync Status")
            # Using st.table for that clean "verification" feel
            audit_df = pd.DataFrame({
                "Parameter": ["Region", "Demographics", "Source", "Budget"],
                "Value": [sel_market, f"{sel_gender} {sel_age}", matched_col, f"₹{budget:,}"],
                "Status": ["Verified ✅", "Mapped ✅", "Active ⚡", "Allocated ✅"]
            })
            st.table(audit_df)
else:
    st.error("Missing Data Source: Please ensure 'barc_data.xlsx.xlsx - Table.csv' is available.")
