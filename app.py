import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast
import re
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Impact Media Terminal 2026", layout="wide", page_icon="🏛️")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. ELITE-UI STYLING (SYMMETRY & PROFESSIONALISM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 380px !important; }
    
    /* Uniform Card Sizing for Dashboard Professionalism */
    .metric-card, .metric-card-impact {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3B82F6;
        min-height: 165px; 
        display: flex; flex-direction: column; justify-content: space-between;
        backdrop-filter: blur(10px);
    }
    .metric-card-impact { border-left: 4px solid #A855F7; }
    
    .label { color: #94A3B8; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: #F8FAFC; font-size: 1.9rem; font-weight: 800; margin-top: 5px; line-height: 1.1; }
    .sub-value { font-size: 0.82rem; color: #64748B; margin-top: 8px; font-weight: 600; }
    
    .sov-badge { 
        padding: 4px 10px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; 
        color: white; letter-spacing: 0.5px; margin-top: 5px; display: inline-block;
    }
    
    .section-header {
        background: linear-gradient(90deg, #1E293B 0%, transparent 100%);
        padding: 12px 20px; border-radius: 4px; border-left: 3px solid #3B82F6;
        color: #F8FAFC; font-weight: 700; margin: 35px 0 15px 0; font-size: 0.85rem; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE 2026 PAN-INDIA DATABASE (FIXED & LOCKED) ---
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
    memory_decay = (11.0 / 4) * weeks * clutter
    l_final = 0
    for l in np.arange(0.1, 150.0, 0.1):
        if (1 - stats.poisson.cdf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_final = max(l, memory_decay)
            break
    reach_1p = (1 - math.exp(-l_final)) * 100
    sov = (l_final / ((55 if m_type == "Urban" else 30) * weeks)) * 100
    if sov < 10: tier, color, desc = "MAINTENANCE", "#64748B", "Low Recall"
    elif sov < 20: tier, color, desc = "CHALLENGER", "#3B82F6", "High Breakthrough"
    else: tier, color, desc = "DOMINANT", "#A855F7", "Market Authority"
    return round(l_final, 1), round(reach_1p, 1), round(sov, 1), tier, color, desc

# --- 5. SIDEBAR (COMPREHENSIVE INPUTS) ---
with st.sidebar:
    st.markdown("### 🏛️ COMMAND CENTER")
    m_type = st.radio("Market Classification", ["Urban", "Rural"], horizontal=True)
    
    st.markdown("---")
    sel_age = st.multiselect("Target Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender Selection", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS Groupings", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    sel_zones = st.multiselect("Geography: Zones", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    if sel_zones:
        for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    else:
        for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    
    sel_states = st.multiselect("Geography: States", sorted(avail_states))
    
    avail_districts = []
    if sel_states:
        for z in INDIA_GEO_DATABASE:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]: avail_districts.extend(INDIA_GEO_DATABASE[z][s])
    sel_districts = st.multiselect("Geography: Districts (Optional)", sorted(avail_districts))
    
    st.markdown("---")
    r_goal = st.slider("Reach Target % (Effective)", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Campaign Duration (Weeks)", 1, 12, 4)
    
    execute = st.button("EXECUTE TERMINAL PHYSICS", use_container_width=True)

# --- 6. MAIN DASHBOARD ---
st.markdown('<p style="font-size:2.4rem; font-weight:800; color:white; margin-bottom:0; letter-spacing:-1px;">Impact Media Terminal <span style="color:#3B82F6;">2026</span></p>', unsafe_allow_html=True)
st.markdown('<p style="color:#3B82F6; font-family:\'JetBrains Mono\'; font-size:0.8rem; margin-bottom:30px; letter-spacing:1px;">AI-POWERED REACH & SOV ANALYSIS</p>', unsafe_allow_html=True)

if execute:
    freq, r1_perc, sov_val, tier, t_color, t_desc = calculate_physics(r_goal, n_eff, weeks, m_type)
    
    # Universe Modeling
    geo_scale = len(sel_districts) if sel_districts else (len(sel_states) * 12 if sel_states else 100)
    universe = int(1450000 * (geo_scale/100) * (len(sel_age)*0.3))
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * (180 if m_type == "Urban" else 110)

    # ROW 1: PRIMARY PHYSICS
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">Target Universe</div><div class="value">{universe:,}</div><div class="sub-value">Total Addressable Market</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">Max Reach (1+)</div><div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} Uniques</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="label">Actual Freq/Imps</div><div class="value">{freq}x</div><div class="sub-value">{total_imps:,} Total Deliv.</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card-impact"><div class="label">Share of Voice</div><div class="value" style="color:{t_color};">{sov_val}%</div><div class="sov-badge" style="background:{t_color}">{tier}</div></div>', unsafe_allow_html=True)

    # ROW 2: BUDGET & FINANCIALS
    st.markdown('<div class="section-header">ESTIMATED MEDIA BUDGETING & FINANCIAL EFFICIENCY</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.markdown(f'<div class="metric-card"><div class="label">Est. Budget</div><div class="value">₹{int(est_budget):,}</div><div class="sub-value">Projected Investment</div></div>', unsafe_allow_html=True)
    with b2: st.markdown(f'<div class="metric-card"><div class="label">Cost Per Reach</div><div class="value">₹{round(est_budget/r1_abs, 2)}</div><div class="sub-value">Per Unique User</div></div>', unsafe_allow_html=True)
    with b3: st.markdown(f'<div class="metric-card"><div class="label">CPRP</div><div class="value">₹{int(est_budget/r1_perc):,}</div><div class="sub-value">Per Rating Point</div></div>', unsafe_allow_html=True)
    with b4: st.markdown(f'<div class="metric-card"><div class="label">Impact Factor</div><div class="value">{"High" if sov_val > 18 else "Standard"}</div><div class="sub-value">Clutter Resistance</div></div>', unsafe_allow_html=True)

    # ROW 3: AI STRATEGIC PENETRATION
    st.markdown('<div class="section-header">AI STRATEGIC PENETRATION & AFFINITY (2026 PROJECTION)</div>', unsafe_allow_html=True)
    try:
        ai_prompt = f"Media Strategist 2026. Audience: {sel_age}, {sel_gender}, NCCS {sel_nccs}. Market: {m_type} {sel_states}. SOV: {sov_val}%. List Top 10 Genres and Top 10 Platforms in a Python dictionary 'genres' and 'platforms'."
        response = model.generate_content(ai_prompt)
        data = ast.literal_eval(re.search(r'\{.*\}', response.text, re.DOTALL).group())
        cl, cr = st.columns(2)
        with cl: 
            st.markdown("<p style='color:#94A3B8; font-size:0.7rem; font-weight:700; margin-bottom:10px;'>TOP MEDIA GENRES</p>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(data["genres"]), use_container_width=True, hide_index=True)
        with cr: 
            st.markdown("<p style='color:#94A3B8; font-size:0.7rem; font-weight:700; margin-bottom:10px;'>TOP MEDIA PLATFORMS</p>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(data["platforms"]), use_container_width=True, hide_index=True)
    except:
        st.warning("Strategic AI Engine Synchronizing...")

else:
    st.info("System Ready. Define campaign parameters to execute impact simulation.")
