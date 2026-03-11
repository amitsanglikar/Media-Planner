import streamlit as st
import pandas as pd
from google import genai
import math
import numpy as np
from scipy import stats
import re
import ast

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Virtual Digital Media Planning Tool", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 420px !important; }
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 180px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; font-weight: 500; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; text-transform: uppercase; }
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 12px 20px; border-radius: 4px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 30px 0 15px 0; font-size: 0.9rem; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (GEO - LOCKED) ---
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
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilapur", "Korba", "Durg"],
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

# --- 4. IMPROVED PHYSICS ENGINE ---
def calculate_breakthrough_physics(reach_goal_n, n_plus, weeks, market_choice):
    if market_choice == "Urban":
        capacity, base_ecpm = 60, 175
    elif market_choice == "Rural":
        capacity, base_ecpm = 35, 105
    else:
        capacity, base_ecpm = 47.5, 140

    l_raw = 0
    # Solve for the exact statistical lambda required
    for l in np.arange(0.1, 800.0, 0.1):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    # Apply your requested 2.0x Friction Multiplier
    # To get 45% at 4+, l_raw is ~4.1. 4.1 * 4 (since we scale by N+) = ~16.4
    l_impact = l_raw * 2.0 * (1 + (n_plus * 0.25)) 
    
    if l_impact < 15: f_tier, f_color = "Forgettable", "#64748B"
    elif 15 <= l_impact < 30: f_tier, f_color = "Challenger", "#94a3b8"
    elif 30 <= l_impact <= 50: f_tier, f_color = "Sweet Spot", "#00f2ff"
    else: f_tier, f_color = "Dominant", "#bc13fe"
    
    sov = (l_impact / (capacity * weeks)) * 100
    d_ecpm = base_ecpm * (1 + (sov / 100))
    
    return round(l_impact, 1), f_tier, f_color, round(sov, 1), round(d_ecpm, 2)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>PLANNING_INPUTS</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Selection", ["Urban", "Rural", "Both"], horizontal=True, index=2)
    sel_age = st.multiselect("Target Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender Selection", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS Group", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    sel_zones = st.multiselect("Select Zones", list(INDIA_GEO_DATABASE.keys()))
    available_states = []
    zones_to_search = sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()
    for z in zones_to_search:
        available_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("Select States", sorted(available_states))
    
    available_districts = []
    if sel_states:
        for z in zones_to_search:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]:
                    available_districts.extend(INDIA_GEO_DATABASE[z][s])
    sel_districts = st.multiselect("Select Districts", sorted(available_districts))

    st.markdown("---")
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 6. MAIN DASHBOARD ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white;">VIRTUAL DIGITAL <span style="color:#00f2ff;">MEDIA PLANNING TOOL</span></p>', unsafe_allow_html=True)

if execute:
    freq, f_tier, f_color, sov_val, d_ecpm = calculate_breakthrough_physics(r_goal, n_eff, weeks, m_type)
    
    # Universe Math
    TOTAL_PENETRATION = 950000000 
    market_base = TOTAL_PENETRATION * (0.72 if m_type=="Both" else 0.40)
    nccs_w = len(sel_nccs) * 0.2
    age_w = len(sel_age) * 0.25
    geo_w = (len(sel_districts) if sel_districts else 1) / 780
    
    universe = int(market_base * nccs_w * age_w * geo_w)
    # At high N+, 1+ reach is almost 95% of the universe
    reached_heads = int(universe * 0.95) 
    total_imps = int(reached_heads * freq)
    est_budget = (total_imps / 1000) * d_ecpm

    st.markdown('<div class="section-header">CORE IMPACT METRICS</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">Addressable Universe</div><div class="value">{universe:,}</div><div class="sub-value">Buyable Target</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">Actual Frequency</div><div class="value">{freq}</div><div class="sub-value">Average 1+ Impressions</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="label">Total Budget</div><div class="value">₹{int(est_budget):,}</div><div class="sub-value">Gross Investment</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">MARKET BREAKTHROUGH</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1: st.markdown(f'<div class="metric-card"><div class="label">eCPM</div><div class="value">₹{d_ecpm}</div><div class="sub-value">Inventory Rate</div></div>', unsafe_allow_html=True)
    with b2: st.markdown(f'<div class="metric-card-impact" style="border-left:5px solid {f_color}"><div class="label">Market Shout</div><div class="value" style="color:{f_color}">{sov_val}%</div><div class="status-badge" style="background:{f_color}">{f_tier}</div></div>', unsafe_allow_html=True)
