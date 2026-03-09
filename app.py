import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide", page_icon="🌐")

# --- 2. THE "MOCK-FAITHFUL" CSS OVERRIDE ---
# This forces the exact professional aesthetics from our design phase
st.markdown("""
    <style>
    /* Force Light Theme Colors and Clean Background */
    .stApp {
        background-color: #F1F5F9 !important;
    }

    /* Professional Sidebar & Header styling */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    
    /* Typography & Label Force */
    label, p, h1, h2, h3, h5, [data-testid="stWidgetLabel"] p {
        color: #1E3A8A !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }

    /* The White "Filter Bar" from the Mock */
    .filter-section {
        background-color: #FFFFFF !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 30px !important;
    }

    /* KPI Card Simulation with the Navy Accent Strip */
    .kpi-card {
        background-color: white !important;
        padding: 24px !important;
        border-radius: 12px !important;
        border-left: 8px solid #1E3A8A !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }

    /* Input Styling - Soft Blue Tint */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* Action Button - High Contrast Coral */
    .stButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: 0.3s ease all;
    }
    .stButton>button:hover {
        background-color: #E03E3E !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE: MARKET MASTER ---
MARKET_MASTER = {
    "India (Total)": {"base": 1400000, "internet_pen": 0.55},
    "Mumbai": {"base": 21000, "internet_pen": 0.85},
    "Delhi NCR": {"base": 32000, "internet_pen": 0.82},
    "Bangalore": {"base": 13000, "internet_pen": 0.88},
    "Chennai": {"base": 11000, "internet_pen": 0.84},
    "Kolkata": {"base": 15000, "internet_pen": 0.75},
    "Hyderabad": {"base": 10500, "internet_pen": 0.80},
    "Maharashtra (Rest)": {"base": 95000, "internet_pen": 0.65},
    "Uttar Pradesh": {"base": 240000, "internet_pen": 0.45},
}

def calculate_custom_universe(market, gender, age, nccs):
    data = MARKET_MASTER.get(market)
    total_pop = data['base']
    digital_pop = total_pop * data['internet_pen']
    
    # Weights based on Demographic distributions
    gender_w = 0.50 if gender != "Both" else 1.0
    age_map = {"15-30": 0.45, "15-21": 0.18, "22-30": 0.27, "31-40": 0.20, "41-50": 0.15, "2-14": 0.20}
    nccs_map = {"A": 0.15, "AB": 0.35, "ABC": 0.55, "B": 0.20, "CDE": 0.45}
    
    final_val = digital_pop * gender_w * age_map.get(age, 1.0) * nccs_map.get(nccs, 1.0)
    return int(final_val)

# --- 4. TOP BRANDING ---
st.markdown('<h1 style="font-size: 36px;">🌐 Virtual Media Planner</h1>', unsafe_allow_html=True)
st.markdown('<p style="margin-top:-20px; font-size:18px; color:#64748B !important; font-weight: 400 !important;">Intelligence Layer: Benchmark Model 2024-25</p>', unsafe_allow_html=True)

# --- 5. THE COMMAND CENTER (The Filter Bar) ---
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.markdown("#### 🎯 Define Target Audience")

c1, c2, c3, c4 = st.columns(4)
with c1: sel_market = st.selectbox("Market / Geography", list(MARKET_MASTER.keys()))
with c2: sel_gender = st.selectbox("Gender", ["Both", "Male", "Female"])
with c3: sel_age = st.selectbox("Age Bracket", ["15-30", "15-21", "22-30", "31-40", "41-50", "2-14"])
with c4: sel_nccs = st.selectbox("NCCS / SEC Class", ["AB", "A", "ABC", "B", "CDE"])

c5, c6, c7 = st.columns([1.5, 2, 1])
with c5: budget = st.number_input("Campaign Budget (INR)", value=1000000, step=50000)
with c6: reach_goal = st.slider("Reach Target (Min %)", 5, 95, 60)
with c7: 
    st.write("##") # Visual alignment
    calculate = st.button("Generate Plan")
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. RESULTS & OUTPUTS ---
if calculate:
    universe = calculate_custom_universe(sel_market, sel_gender, sel_age, sel_nccs)
    
    col_kpi, col_table = st.columns([1, 1.2])

    with col_kpi:
        # Card 1: Universe Size
        st.markdown(f"""
            <div class="kpi-card">
                <p style="margin:0; font-size:14px; color:#64748B !important; font-weight:
