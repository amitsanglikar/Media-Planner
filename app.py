import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Pro Digital Planner 2026", layout="wide", page_icon="📊")

# Industry Benchmarks (IAMAI 2025/2026)
TOTAL_DIGITAL_UNIVERSE = 958000  # '000s

GEOGRAPHY = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane", "Solapur"],
    "Delhi NCR": ["Central Delhi", "North Delhi", "South Delhi", "Gurgaon", "Noida", "Ghaziabad"],
    "Karnataka": ["Bangalore Urban", "Bangalore Rural", "Mysore", "Hubli-Dharwad", "Belgaum"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"]
}

# --- 2. CSS STYLING (Improved for Readability & Logos) ---
st.markdown("""
    <style>
    /* Force Light Professional Background */
    .stApp { background-color: #F8FAFC !important; }
    
    /* Branding & Header */
    .main-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
    .logo-text { color: #1E3A8A; font-size: 32px; font-weight: 800; font-family: 'Inter', sans-serif; }
    
    /* Filter Bar Container */
    .filter-section {
        background: #ffffff; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }
    
    /* KPI Card */
    .kpi-box {
        background: #ffffff; padding: 24px; border-radius: 12px;
        border-left: 8px solid #3B82F6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    /* Global Text Force */
    label, p, h1, h2, h3 { color: #1E3A8A !important; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI LAYOUT: LOGO & HEADER ---
st.markdown("""
    <div class="main-header">
        <span style="font-size: 40px;">🌐</span>
        <span class="logo-text">DIGITAL PLANNER <small style="font-size:14px; color:#64748B;">v3.2</small></span>
    </div>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("#### 🌍 Geographic & Demographic Targeting")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sel_states = st.multiselect("Select States", list(GEOGRAPHY.keys()), default=["Maharashtra"])
        geo_type = st.radio("Market Type", ["Overall", "Urban Only", "Rural Only"], horizontal=True)
    
    with col2:
        available_districts = []
        for s in sel_states: available_districts.extend(GEOGRAPHY[s])
        sel_districts = st.multiselect("Select Districts (Optional)", sorted(list(set(available_districts))))
        sel_gender = st.multiselect("Gender Selection", ["Male", "Female"], default=["Male", "Female"])
        
    with col3:
        sel_age = st.multiselect("Target Age Groups", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
        sel_nccs = st.multiselect("Target NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    calculate = st.button("BUILD AUDIENCE PLAN", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. CALCULATION ENGINE ---
def run_planner():
    state_weights = {"Maharashtra": 0.14, "Delhi NCR": 0.09, "Karnataka": 0.08, "Tamil Nadu": 0.09, "Uttar Pradesh": 0.16, "West Bengal": 0.08, "Gujarat": 0.07}
    
    # Base Market Universe
    total_weight = sum([state_weights.get(s, 0.05) for s in sel_states])
    base_u = TOTAL_DIGITAL_UNIVERSE * total_weight
    
    # Geography Split
    if geo_type == "Urban Only": base_u *= 0.43
    elif geo_type == "Rural Only": base_u *= 0.57
    
    # Age & NCCS Weights (Fixed Mapping)
    age_map = {"15-24": 0.35, "25-34": 0.30, "35-44": 0.20, "45+": 0.15}
    nccs_map = {"A": 0.15, "B": 0.20, "C": 0.25, "D": 0.20, "E": 0.20}
    
    age_w = sum([age_map.get(a, 0) for a in sel_age])
    nccs_w = sum([nccs_map.get(n, 0) for n in sel_nccs])
    
    gender_w = 0
    if "Male" in sel_gender: gender_w += 0.54
    if "Female" in sel_gender: gender_w += 0.46
    
    final_universe = int(base_u * age_w * nccs_w * gender_w)
    return final_universe, base_u

# --- 5. RESULTS DISPLAY ---
if calculate:
    universe, regional_base = run_planner()
    
    res_col1, res_col2 = st.columns([1, 1.2])
    
    with res_col1:
        # KPI BOX
        st.markdown(f"""
        <div class="kpi-box">
            <p style="color:#64748B; margin:0; font-size:14px; font-weight:400;">Target Digital Universe</p>
            <h1 style="color:#1E3A8A; margin:0; font-size:48px;">{universe:,}</h1>
            <p style="font-size:12px; color:#64748B; margin:0;">Active Monthly Users ('000s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AUDIENCE FUNNEL (Plotly)
        st.markdown("#### 🔍 Funnel Analytics")
        fig = go.Figure(go.Funnel(
            y = ["Total Digital", "Selected Region", "Demographics"],
            x = [TOTAL_DIGITAL_UNIVERSE, regional_base, universe],
            textinfo = "value+percent initial",
            marker = {"color": ["#0F172
