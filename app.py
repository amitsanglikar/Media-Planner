import streamlit as st
import pandas as pd
from google import genai
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Breakthrough Media Terminal 2026", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Setup Error: Ensure GEMINI_API_KEY is configured in Streamlit Secrets.")
    st.stop()

# --- 2. TERMINAL STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 380px !important; }
    
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 180px;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; font-weight: 500; line-height: 1.2; }
    
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 10px 20px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 30px 0 15px 0; font-size: 0.9rem; letter-spacing: 2px;
    }
    
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; text-transform: uppercase; }
    
    .glossary-content { color: #f8fafc; line-height: 1.6; }
    .glossary-term { color: #00f2ff; font-weight: 700; font-family: 'JetBrains Mono'; display: block; margin-top: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (LOCKED) ---
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
METROS = ["Mumbai", "Delhi", "Bengaluru", "Kolkata", "Chennai", "Hyderabad", "Ahmedabad", "Pune"]

# --- 4. ENGINE: IMPACT PHYSICS ---
def calculate_breakthrough_physics(reach_goal_n, n_plus, weeks, m_type):
    l_raw = 0
    # Solver for Poisson Lambda
    for l in np.arange(0.1, 150.0, 0.1):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    # Apply 1.3x Wastage Multiplier
    l_impact = l_raw * 1.3
    
    # 3-5-10-12 Frequency Grade
    if l_impact < 6: f_tier, f_color = "Forgettable", "#64748B"
    elif 6 <= l_impact < 10: f_tier, f_color = "Challenger", "#94a3b8"
    elif 10 <= l_impact <= 12: f_tier, f_color = "Sweet Spot", "#00f2ff"
    else: f_tier, f_color = "Dominant", "#bc13fe"
    
    reach_1p = (1 - math.exp(-l_impact)) * 100
    capacity = 60 if m_type == "Urban" else 35
    sov = (l_impact / (capacity * weeks)) * 100
    
    base_ecpm = 175 if m_type == "Urban" else 105
    dynamic_ecpm = base_ecpm * (1 + (sov / 100))
    
    if sov < 5: s_tier, s_color = "MAINTENANCE", "#64748B"
    elif sov < 15: s_tier, s_color = "CHALLENGER", "#00f2ff"
    else: s_tier, s_color = "DOMINANT", "#bc13fe"
    
    return round(l_impact, 1), f_tier, f_color, round(reach_1p, 1), round(sov, 1), s_tier, s_color, round(dynamic_ecpm, 2)

# --- 5. TOP BAR & GLOSSARY MODAL ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white; margin-bottom:0;">BREAKTHROUGH <span style="color:#00f2ff;">MEDIA TERMINAL</span></p>', unsafe_allow_html=True)

@st.dialog("GLOSSARY & INTELLIGENCE LOGIC")
def open_glossary():
    st.markdown("""
    <div class="glossary-content">
        <span class="glossary-term">Actual Frequency (Impact-Weighted)</span>
        Derived from Poisson Lambda ($\lambda$) and adjusted by a <b>1.3x Wastage Multiplier</b>. This accounts for ads that are rendered but not viewed in high-clutter Indian digital feeds.
        
        <span class="glossary-term">3-5-10-12 Breakthrough Logic</span>
        <b>< 6.0:</b> Threshold of Forgetfulness. Ad recall is statistically negligible.<br>
        <b>10.0-12.0:</b> Optimal Recall "Sweet Spot". Maximum efficiency for Aided Brand Awareness.<br>
        <b>> 12.0:</b> Market Dominance. High Breakthrough velocity but risk of creative fatigue.
        
        <span class="glossary-term">Market SOV (Share of Voice)</span>
        Campaign weight relative to total category inventory capacity (Urban: 60/wk, Rural: 35/wk).
        
        <span class="glossary-term">Dynamic eCPM</span>
        SOV-adjusted pricing. Reflects the premium paid to secure higher inventory occupancy in a competitive auction.
    </div>
    """, unsafe_allow_html=True)

if st.button("🔍 OPEN GLOSSARY & LOGIC"):
    open_glossary()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>PLANNING_COMMAND</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    
    st.markdown("---")
    zone_options = ["8 Metros"] + list(INDIA_GEO_DATABASE.keys())
    sel_zones = st.multiselect("Select Zones", zone_options)
    
    if "8 Metros" in sel_zones:
        sel_states = st.multiselect("Top 8 Metros", sorted(METROS))
        sel_districts = sel_states
    else:
        avail_states = []
        for z in (sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()):
            avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
        sel_states = st.multiselect("Select States", sorted(list(set(avail_states))))
        
        avail_districts = []
        for z in INDIA_GEO_DATABASE:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]: avail_districts.extend(INDIA_GEO_DATABASE[z][s])
        sel_districts = st.multiselect("Select Districts", sorted(avail_districts))
    
    st.markdown("---")
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 7. MAIN DASHBOARD ---
if execute:
    freq, f_tier, f_color, r1_perc, sov_val, s_tier, s_color, d_ecpm = calculate_breakthrough_physics(r_goal, n_eff, weeks, m_type)
    
    # Universe Calculation
    universe_base = 950000000 
    geo_count = len(sel_districts) if sel_districts else 1
    universe = int(universe_base * (geo_count / 850) * 12) # Scaled for digital penetration
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * d_ecpm

    st.markdown('<div class="section-header">CORE IMPACT METRICS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">Digital Universe</div><div class="value">{universe:,}</div><div class="sub-value">Target TAM</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">Reach @ 1+</div><div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} People</div></div>', unsafe_allow_html=True)
    
    # Frequency Card with Status Badge
    with c3: st.markdown(f'''
        <div class="metric-card-impact" style="border-left: 5px solid {f_color}; border-color: {f_color}33;">
            <div class="label">Actual Frequency</div>
            <div class="value" style="color:{f_color};">{freq}</div>
            <div class="status-badge" style="background:{f_color}">{f_tier}</div>
            <div class="sub-value">Incl. 1.3x Wastage Buffer</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # SOV Card with Status Badge
    with c4: st.markdown(f'''
        <div class="metric-card-impact" style="border-left: 5px solid {s_color}; border-color: {s_color}33;">
            <div class="label">Market SOV</div>
            <div class="value" style="color:{s_color};">{sov_val}%</div>
            <div class="status-badge" style="background:{s_color}">{s_tier}</div>
            <div class="sub-value">Inventory Occupancy</div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('<div class="section-header">FINANCIALS</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1: st.markdown(f'<div class="metric-card"><div class="label">Total Budget</div><div class="value">₹{int(est_budget):,}</div></div>', unsafe_allow_html=True)
    with f2: st.markdown(f'<div class="metric-card"><div class="label">Impact eCPM</div><div class="value">₹{d_ecpm}</div></div>', unsafe_allow_html=True)
    with f3: st.markdown(f'<div class="metric-card"><div class="label">Cost / Unique</div><div class="value">₹{round(est_budget/r1_abs, 2) if r1_abs > 0 else 0}</div></div>', unsafe_allow_html=True)
    with f4: st.markdown(f'<div class="metric-card-impact"><div class="label">Efficiency</div><div class="value">{"HIGH" if sov_val < 15 else "STRETCHED"}</div></div>', unsafe_allow_html=True)

    # Added Visual Intelligence for Frequency Distribution
    
    

else:
    st.info("System Standby. Configure Planning Command and Execute to begin.")
