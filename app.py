import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast
import re
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Neon Impact Terminal 2026", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. NEON-TERMINAL STYLING WITH TOOLTIPS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 380px !important; }
    
    /* Neon Card Architecture */
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); 
        border: 1px solid #00f2ff33;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 170px; 
        display: flex; flex-direction: column; justify-content: space-between;
        transition: 0.3s;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; box-shadow: 0 0 15px rgba(188, 19, 254, 0.1); }
    
    /* Tooltip Logic */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        margin-left: 5px;
        color: #00f2ff;
        font-size: 0.8rem;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 220px;
        background-color: #111;
        color: #fff;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 100;
        bottom: 125%; 
        left: 50%;
        margin-left: -110px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #00f2ff;
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 400;
        line-height: 1.4;
        text-transform: none;
        letter-spacing: 0px;
    }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; box-shadow: 0 0 15px #00f2ff55; }

    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; text-shadow: 0 0 10px rgba(255,255,255,0.2); }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; font-weight: 500; }
    
    .sov-badge { 
        padding: 5px 12px; border-radius: 4px; font-size: 0.7rem; font-weight: 900; 
        color: black; letter-spacing: 1px; margin-top: 10px; display: inline-block;
        background: #bc13fe; box-shadow: 0 0 10px #bc13fe;
    }
    
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 12px 20px; border-radius: 4px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 40px 0 20px 0; font-size: 0.9rem; letter-spacing: 2px;
        font-family: 'JetBrains Mono';
    }
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

# --- 4. ENGINE ---
def calculate_physics(reach_goal_n, n_plus, weeks, m_type):
    clutter = 1.45 if m_type == "Urban" else 1.20
    l_final = 0
    for l in np.arange(0.1, 150.0, 0.1):
        if (1 - stats.poisson.cdf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_final = l
            break
    reach_1p = (1 - math.exp(-l_final)) * 100
    sov = (l_final / ((55 if m_type == "Urban" else 30) * weeks)) * 100
    if sov < 10: tier, color, desc = "MAINTENANCE", "#64748B", "Low Recall"
    elif sov < 20: tier, color, desc = "CHALLENGER", "#00f2ff", "High Breakthrough"
    else: tier, color, desc = "DOMINANT", "#bc13fe", "Market Authority"
    return round(l_final, 1), round(reach_1p, 1), round(sov, 1), tier, color, desc

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; font-family:JetBrains Mono;'>COMMAND_CORE</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Classification", ["Urban", "Rural"], horizontal=True)
    sel_age = st.multiselect("Target Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS Groupings", ["A", "B", "C", "D", "E"], default=["A", "B"])
    st.markdown("---")
    sel_zones = st.multiselect("Geography: Zones", list(INDIA_GEO_DATABASE.keys()))
    avail_states = []
    for z in (sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()): avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("Geography: States", sorted(avail_states))
    st.markdown("---")
    r_goal = st.slider("Reach Target %", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("RUN IMPACT PHYSICS", use_container_width=True)

# --- 6. DASHBOARD ---
st.markdown('<p style="font-size:3rem; font-weight:900; color:white; margin-bottom:0; letter-spacing:-2px;">IMPACT TERMINAL <span style="color:#00f2ff;">2026</span></p>', unsafe_allow_html=True)

# Tooltip Helper Function
def get_label(text, info):
    return f'<div class="label">{text}<div class="tooltip">ⓘ<span class="tooltiptext">{info}</span></div></div>'

if execute:
    freq, r1_perc, sov_val, tier, t_color, t_desc = calculate_physics(r_goal, n_eff, weeks, m_type)
    universe = int(1450000 * ((len(sel_states)*12 if sel_states else 100)/100) * (len(sel_age)*0.3))
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * (180 if m_type == "Urban" else 110)
    ecpm = (est_budget / total_imps) * 1000 if total_imps > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card">{get_label("Total Universe", "The estimated total number of unique individuals in your selected geography and demographic segments.")}<div class="value">{universe:,}</div><div class="sub-value">TAM Projection</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card">{get_label("Reach (1+)", "The percentage of the Total Universe exposed to the ad at least once.")}<div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} Uniques</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card">{get_label("Frequency", "The average number of times a reached individual is exposed to the campaign.")}<div class="value">{freq}x</div><div class="sub-value">{total_imps:,} Imps.</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card-impact">{get_label("Share of Voice", "Your brands percentage of total category ad impressions within the selected time and market.")}<div class="value" style="color:{t_color};">{sov_val}%</div><div class="sov-badge">{tier}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">FINANCIAL_EFFICIENCY_NODES</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.markdown(f'<div class="metric-card">{get_label("Est. Budget", "Total projected investment required to achieve these reach and frequency goals based on 2026 market rates.")}<div class="value">₹{int(est_budget):,}</div><div class="sub-value">Net Investment</div></div>', unsafe_allow_html=True)
    with b2: st.markdown(f'<div class="metric-card">{get_label("Cost / Reach", "The amount spent to reach a single unique individual in your target segment.")}<div class="value">₹{round(est_budget/r1_abs, 2)}</div><div class="sub-value">Per Unique User</div></div>', unsafe_allow_html=True)
    with b3: st.markdown(f'<div class="metric-card">{get_label("eCPM", "Effective Cost Per Mille: The cost for every 1,000 ad impressions delivered.")}<div class="value">₹{round(ecpm, 2)}</div><div class="sub-value">Efficiency Metric</div></div>', unsafe_allow_html=True)
    with b4: st.markdown(f'<div class="metric-card">{get_label("Saturation", "The point where additional spending results in minimal incremental reach gain.")}<div class="value">{"84%" if sov_val > 20 else "42%"}</div><div class="sub-value">Clutter Resistance</div></div>', unsafe_allow_html=True)
else:
    st.info("System Standby. Define Parameters to Initialize.")
