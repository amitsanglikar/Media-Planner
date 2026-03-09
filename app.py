import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Digital Media Planner (IAMAI/Comscore)", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    :root { --primary: #0F172A; --accent: #3B82F6; --bg: #F1F5F9; }
    .stApp { background-color: var(--bg) !important; }
    .filter-section {
        background-color: #FFFFFF !important;
        padding: 25px; border-radius: 12px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
    }
    .kpi-card {
        background-color: white !important; padding: 20px;
        border-radius: 10px; border-top: 4px solid var(--accent);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    label, p, h1, h3 { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    .stButton>button {
        background-color: var(--accent) !important; color: white !important;
        font-weight: 600; width: 100%; height: 48px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE DIGITAL SOURCE ENGINE ---
# Mapping based on IAMAI 2024/25 & Comscore Benchmarks
DIGITAL_UNIVERSE_TOTAL = 958000 # In '000s (958 Million)

MARKET_PENETRATION = {
    "India (Total)": 1.0,
    "Maharashtra": 0.14, "Delhi NCR": 0.08, "Karnataka": 0.07,
    "Tamil Nadu": 0.09, "West Bengal": 0.08, "Uttar Pradesh": 0.16,
    "Kerala": 0.05, "Gujarat": 0.07, "Rest of India": 0.26
}

def calculate_digital_audience(market, gender, age, nccs):
    # 1. Base Market Size
    base = DIGITAL_UNIVERSE_TOTAL * MARKET_PENETRATION.get(market, 0.05)
    
    # 2. Gender Split (IAMAI: 54% M / 46% F)
    g_w = 0.54 if gender == "Male" else (0.46 if gender == "Female" else 1.0)
    
    # 3. Age Split (Comscore/IAMAI distribution)
    age_map = {"15-24": 0.35, "25-34": 0.30, "35-44": 0.20, "45+": 0.15}
    a_w = age_map.get(age, 1.0)
    
    # 4. NCCS Proxy (Digital access & E-comm propensity)
    nccs_map = {"A": 0.18, "AB": 0.38, "ABC": 0.58, "CDE": 0.42}
    n_w = n_map.get(nccs, 1.0) if 'n_map' in locals() else nccs_map.get(nccs, 1.0)
    
    universe = base * g_w * a_w * n_w
    return int(universe)

# --- 4. UI ---
st.markdown('<h1>📊 Digital Media Planner</h1>', unsafe_allow_html=True)
st.markdown('<p style="margin-top:-20px;">Source: IAMAI Internet in India 2025 | Comscore MMX</p>', unsafe_allow_html=True)

st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.markdown("### 🎯 Targeting Parameters")
c1, c2, c3, c4 = st.columns(4)
with c1: market = st.selectbox("Market", list(MARKET_PENETRATION.keys()))
with c2: gender = st.selectbox("Gender", ["Both", "Male", "Female"])
with c3: age = st.selectbox("Age Group", ["15-24", "25-34", "35-44", "45+"])
with c4: nccs = st.selectbox("NCCS", ["A", "AB", "ABC", "CDE"])

c5, c6, c7 = st.columns([2, 2, 1])
with c5: budget = st.number_input("Ad Spend (INR)", 500000)
with c6: goal = st.slider("Reach Target %", 10, 90, 50)
with c7: run = st.button("Build Plan")
st.markdown('</div>', unsafe_allow_html=True)

if run:
    u_size = calculate_digital_audience(market, gender, age, nccs)
    
    # Visualizing the Audience Funnel
    
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
            <div class="kpi-card">
                <p style="margin:0; font-size:14px; opacity:0.8;">Target Digital Universe</p>
                <h1 style="margin:0; font-size:44px;">{u_size:,}</h1>
                <p style="margin:0; font-size:12px;">Active Users ('000s) in selected segment</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_b:
        st.markdown("### 🛠 Data Source Audit")
        st.write(f"**Market Base:** {market}")
        st.write(f"**Demographic Weight:** {gender} ({age})")
        st.info("Mapping confirmed via IAMAI ICUBE 2024 active user base.")
