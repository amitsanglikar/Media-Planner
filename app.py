import streamlit as st
import pandas as pd
from google import genai
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Impact Media Terminal 2026", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. TERMINAL STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 420px !important; }
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 180px;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; font-weight: 500; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (LOCKED - NO CHANGES ALLOWED) ---
INDIA_GEO_DATABASE = {
    "North": {
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Shahdara", "North West Delhi", "South East Delhi"],
        "Haryana": ["Gurugram", "Faridabad", "Ambala", "Panipat", "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Hoshiarpur", "Pathankot"],
        "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Prayagraj", "Noida", "Aligarh", "Bareilly", "Gorakhpur"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara", "Alwar", "Sikar"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Haldwani", "Roorkee"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Himachal Pradesh": ["Shimla", "Solan", "Dharamshala"]
    },
    "West": {
        "Maharashtra": ["Mumbai City", "Mumbai Suburban", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati", "Navi Mumbai", "Kolhapur"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Junagadh", "Anand"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Rewa", "Ratlam"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
        "Goa": ["North Goa", "South Goa"]
    },
    "South": {
        "Karnataka": ["Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi", "Ballari", "Udupi"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thoothukudi"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kakinada"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Malappuram", "Kollam", "Palakkad"]
    },
    "East/NE": {
        "West Bengal": ["Kolkata", "Howrah", "Asansol", "Siliguri", "Durgapur", "Bardhaman", "Malda", "Baharampur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Bihar Sharif"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
        "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur", "Tinsukia"],
        "Arunachal Pradesh": ["Itanagar", "Tawang", "Naharlagun", "Pasighat"],
        "Manipur": ["Imphal East", "Imphal West", "Thoubal", "Churachandpur"],
        "Meghalaya": ["Shillong", "Tura", "Jowai"],
        "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
        "Nagaland": ["Dimapur", "Kohima", "Mokokchung", "Tuensang"],
        "Tripura": ["Agartala", "Dharmanagar", "Udaipur"],
        "Sikkim": ["Gangtok", "Namchi", "Geyzing"]
    }
}

# --- 4. ENGINE: BREAKTHROUGH PHYSICS ---
def calculate_breakthrough_physics(reach_goal_n, n_plus, weeks, m_type):
    l_raw = 0
    # Inverse Poisson Solver for Lambda
    for l in np.arange(0.1, 150.0, 0.1):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    # Core Multiplier
    l_impact = l_raw * 1.3 
    
    # Breakthrough Grading (3-5-10-12)
    if l_impact < 6: f_tier, f_color = "Forgettable", "#64748B"
    elif 6 <= l_impact < 10: f_tier, f_color = "Challenger", "#94a3b8"
    elif 10 <= l_impact <= 12: f_tier, f_color = "Sweet Spot", "#00f2ff"
    else: f_tier, f_color = "Dominant", "#bc13fe"
    
    reach_1p = (1 - math.exp(-l_impact)) * 100
    capacity = 60 if m_type == "Urban" else 35
    sov = (l_impact / (capacity * weeks)) * 100
    
    # Dynamic eCPM
    base_ecpm = 175 if m_type == "Urban" else 105
    d_ecpm = base_ecpm * (1 + (sov / 100))
    
    return round(l_impact, 1), f_tier, f_color, round(reach_1p, 1), round(sov, 1), round(d_ecpm, 2)

# --- 5. SIDEBAR (RESTORED EXACT INPUTS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; font-family:JetBrains Mono;'>PLANNING_INPUTS</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    sel_age = st.multiselect("Target Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender Selection", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS Group", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    sel_zones = st.multiselect("Select Zones", list(INDIA_GEO_DATABASE.keys()))
    
    selected_districts = []
    if sel_zones:
        # Collect all states in selected zones
        states_in_zones = {}
        for z in sel_zones:
            states_in_zones.update(INDIA_GEO_DATABASE[z])
            
        sel_states = st.multiselect("Select States", sorted(states_in_zones.keys()))
        
        if sel_states:
            # Collect all districts in selected states
            dist_list = []
            for s in sel_states:
                for z in sel_zones:
                    if s in INDIA_GEO_DATABASE[z]:
                        dist_list.extend(INDIA_GEO_DATABASE[z][s])
            selected_districts = st.multiselect("Select Districts", sorted(dist_list))

    st.markdown("---")
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 6. MAIN TERMINAL ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white; margin-bottom:0;">BREAKTHROUGH <span style="color:#00f2ff;">MEDIA TERMINAL</span></p>', unsafe_allow_html=True)

if execute:
    freq, f_tier, f_color, r1_perc, sov_val, d_ecpm = calculate_breakthrough_physics(r_goal, n_eff, weeks, m_type)
    
    # TAM Scaling Engine
    universe_base = 950000000 
    nccs_scale = len(sel_nccs) / 5.0
    age_scale = len(sel_age) / 4.0
    # Each district represents roughly 1/700th of the penetrable digital market
    dist_scale = len(selected_districts) if selected_districts else 1
    
    universe = int(universe_base * nccs_scale * age_scale * (dist_scale / 700))
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * d_ecpm

    st.markdown('<div class="section-header" style="color:#00f2ff; border-left:3px solid #00f2ff; padding-left:10px; margin-top:30px; margin-bottom:20px; font-weight:800; letter-spacing:1px;">CORE IMPACT METRICS</div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">Target TAM</div><div class="value">{universe:,}</div><div class="sub-value">Digital Universe</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">Reach @ 1+</div><div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} People</div></div>', unsafe_allow_html=True)
    
    with c3: st.markdown(f'''
        <div class="metric-card-impact" style="border-left: 5px solid {f_color};">
            <div class="label">Actual Frequency</div>
            <div class="value" style="color:{f_color};">{freq}</div>
            <div class="status-badge" style="background:{f_color}">{f_tier}</div>
            <div class="sub-value">Incl. 1.3x Wastage Buffer</div>
        </div>''', unsafe_allow_html=True)
        
    with c4: st.markdown(f'<div class="metric-card"><div class="label">Total Budget</div><div class="value">₹{int(est_budget):,}</div><div class="sub-value">at ₹{d_ecpm} eCPM</div></div>', unsafe_allow_html=True)
