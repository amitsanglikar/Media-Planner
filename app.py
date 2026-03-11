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

# --- 2. NEON-TERMINAL STYLING ---
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
    
    .tooltip { position: relative; display: inline-block; cursor: help; margin-left: 5px; color: #00f2ff; font-size: 0.8rem; }
    .tooltip .tooltiptext {
        visibility: hidden; width: 280px; background-color: #111; color: #fff;
        border-radius: 6px; padding: 12px; position: absolute; z-index: 100;
        bottom: 125%; left: 50%; margin-left: -140px; opacity: 0; transition: opacity 0.3s;
        border: 1px solid #00f2ff; font-family: 'Inter', sans-serif; font-size: 0.8rem; text-transform: none; letter-spacing: 0;
    }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; box-shadow: 0 0 15px #00f2ff55; }

    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; }
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

# --- 3. DATABASE (GEO) ---
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

# --- 4. ENGINE (MARKET CAPACITY & PHYSICS) ---
def calculate_breakthrough_physics(reach_goal_n, n_plus, weeks, market_choice):
    if market_choice == "Urban":
        capacity, base_ecpm = 60, 175
    elif market_choice == "Rural":
        capacity, base_ecpm = 35, 105
    else:  # Both
        capacity, base_ecpm = 47.5, 140

    l_raw = 0
    for l in np.arange(0.1, 150.0, 0.1):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    l_impact = l_raw * 1.3 
    
    if l_impact < 6: f_tier, f_color = "Forgettable", "#64748B"
    elif 6 <= l_impact < 10: f_tier, f_color = "Challenger", "#94a3b8"
    elif 10 <= l_impact <= 12: f_tier, f_color = "Sweet Spot", "#00f2ff"
    else: f_tier, f_color = "Dominant", "#bc13fe"
    
    reach_1p = (1 - math.exp(-l_impact)) * 100
    sov = (l_impact / (capacity * weeks)) * 100
    d_ecpm = base_ecpm * (1 + (sov / 100))
    
    return round(l_impact, 1), f_tier, f_color, round(reach_1p, 1), round(sov, 1), round(d_ecpm, 2)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; font-family:JetBrains Mono;'>PLANNING_INPUTS</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Selection", ["Urban", "Rural", "Both"], horizontal=True, index=2)
    sel_age = st.multiselect("Target Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender Selection", ["Both", "Male", "Female"], horizontal=True)
    
    NCCS_MAP = {
        "A": {"weight": 0.15, "desc": "Premium (Ad-Addressable: 95%)"},
        "B": {"weight": 0.20, "desc": "Upper Mid (Ad-Addressable: 85%)"},
        "C": {"weight": 0.35, "desc": "Middle (Ad-Addressable: 70%)"},
        "D": {"weight": 0.20, "desc": "Mass (Ad-Addressable: 55%)"},
        "E": {"weight": 0.10, "desc": "Lower (Ad-Addressable: 40%)"}
    }
    sel_nccs = st.multiselect("NCCS Group", list(NCCS_MAP.keys()), default=["A", "B"])
    
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

# --- 6. DASHBOARD ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white; margin-bottom:0;">VIRTUAL DIGITAL <span style="color:#00f2ff;">MEDIA PLANNING TOOL</span></p>', unsafe_allow_html=True)

def get_label(text, info):
    return f'<div class="label">{text}<div class="tooltip">ⓘ<span class="tooltiptext">{info}</span></div></div>'

if execute:
    freq, f_tier, f_color, r1_perc, sov_val, d_ecpm = calculate_breakthrough_physics(r_goal, n_eff, weeks, m_type)
    
    # --- ADDRESSABLE UNIVERSE LOGIC ---
    TOTAL_PENETRATION = 950000000 
    ADDRESSABLE_RATIO = 0.72 
    
    if m_type == "Urban":
        market_base = TOTAL_PENETRATION * 0.48 * 0.85
    elif m_type == "Rural":
        market_base = TOTAL_PENETRATION * 0.52 * 0.60
    else: # Both
        market_base = TOTAL_PENETRATION * ADDRESSABLE_RATIO

    nccs_total_weight = sum([NCCS_MAP[g]["weight"] for g in sel_nccs])
    age_weight = len(sel_age) / 4
    gender_weight = 0.5 if sel_gender != "Both" else 1.0
    
    total_districts_in_india = 780
    geo_multiplier = (len(sel_districts) if sel_districts else (len(available_districts) if sel_states else total_districts_in_india)) / total_districts_in_india
    
    universe = int(market_base * nccs_total_weight * age_weight * gender_weight * geo_multiplier)
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * d_ecpm

    st.markdown('<div class="section-header">CORE IMPACT METRICS</div>', unsafe_allow_html=True)
    c1_2, c3, c4 = st.columns([2, 1, 1])
    
    with c1_2: 
        st.markdown(f'''
            <div class="metric-card">
                {get_label("Addressable Universe", "Filtered Persona Reachable via Digital Advertising (Bot-filtered/Active).")}
                <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                    <div>
                        <div class="value">{universe:,}</div>
                        <div class="sub-value">Buyable Target Persona</div>
                    </div>
                    <div style="text-align: right; border-left: 1px solid #00f2ff33; padding-left: 20px;">
                        <div class="value" style="color:#00f2ff;">{r1_perc}%</div>
                        <div class="sub-value">{r1_abs:,} Targeted Reach</div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)

    with c3: st.markdown(f'''
        <div class="metric-card-impact" style="border-left: 5px solid {f_color};">
            {get_label("Actual Frequency / SOV Status", "The Breakthrough status shows if your brand will be remembered amidst market clutter.")}
            <div class="value" style="color:{f_color};">{freq}</div>
            <div class="status-badge" style="background:{f_color}">{f_tier}</div>
            <div class="sub-value">Market Intensity: {sov_val}% SOV</div>
        </div>''', unsafe_allow_html=True)
        
    with c4: st.markdown(f'''
        <div class="metric-card">
            {get_label("Total Budget", "Total buy required at current market rates to achieve this specific Breakthrough Status.")}
            <div class="value">₹{int(est_budget):,}</div>
            <div class="sub-value">at ₹{d_ecpm} eCPM</div>
        </div>''', unsafe_allow_html=True)

    

    st.markdown('<div class="section-header">EFFICIENCY & PENETRATION</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.markdown(f'<div class="metric-card">{get_label("Cost / Person", "Budget divided by unique people reached.")}<div class="value">₹{round(est_budget/r1_abs, 2) if r1_abs > 0 else 0}</div><div class="sub-value">Per Unique Head</div></div>', unsafe_allow_html=True)
    with b2: st.markdown(f'<div class="metric-card">{get_label("eCPM", "Effective cost per 1000 impressions based on SOV intensity.")}<div class="value">₹{d_ecpm}</div><div class="sub-value">Wholesale Rate</div></div>', unsafe_allow_html=True)
    with b3: st.markdown(f'<div class="metric-card">{get_label("Market Shout", "Your total share of the digital conversation capacity.")}<div class="value">{sov_val}%</div><div class="sub-value">SOV %</div></div>', unsafe_allow_html=True)
    with b4: st.markdown(f'<div class="metric-card">{get_label("Total Views", "Total ad displays across the chosen weeks.")}<div class="value">{total_imps:,}</div><div class="sub-value">Gross Impressions</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">AI STRATEGIC PLACEMENT (PREDICTED)</div>', unsafe_allow_html=True)
    try:
        prompt = f"Media Strategist 2026. Audience: {sel_age}, {sel_gender}, NCCS {sel_nccs}. Market: {m_type}. Return Python dict 'genres' and 'platforms' (Top 5 each)."
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        dict_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if dict_match:
            data = ast.literal_eval(dict_match.group())
            cl, cr = st.columns(2)
            with cl: st.dataframe(pd.DataFrame(data["genres"]), use_container_width=True, hide_index=True)
            with cr: st.dataframe(pd.DataFrame(data["platforms"]), use_container_width=True, hide_index=True)
    except:
        st.write("AI insights are currently recalibrating...")
else:
    st.info("System Standby. Adjust inputs and click 'EXECUTE IMPACT PLAN'.")
