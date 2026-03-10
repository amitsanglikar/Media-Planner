import streamlit as st
import pandas as pd
import google.generativeai as genai
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Impact Media Terminal 2026", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. TERMINAL & TOOLTIP STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 380px !important; }
    
    .metric-card, .metric-card-impact {
        background: rgba(10, 10, 10, 0.8); border: 1px solid #00f2ff33;
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 200px; position: relative; display: flex; flex-direction: column; justify-content: space-between;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    
    .info-container { position: absolute; top: 12px; right: 12px; cursor: help; }
    .info-icon { color: #00f2ff; border: 1px solid #00f2ff; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; }
    .info-container:hover .tooltip-text { visibility: visible; opacity: 1; }
    .tooltip-text {
        visibility: hidden; width: 240px; background-color: #1e293b; color: #fff; text-align: left;
        border-radius: 8px; padding: 12px; position: absolute; z-index: 99; bottom: 125%; left: 50%;
        margin-left: -120px; opacity: 0; transition: opacity 0.3s; font-size: 0.8rem; line-height: 1.4;
        border: 1px solid #00f2ff; box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }

    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.75rem; color: #888; font-weight: 500; }
    .outcome-text { font-size: 0.75rem; color: #eee; margin-top: 8px; font-style: italic; line-height: 1.3; font-weight: 600; }
    
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 10px 20px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 30px 0 15px 0; font-size: 0.9rem; letter-spacing: 2px;
    }
    .sov-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (FULL 2026 INDIA GEO) ---
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

# --- 4. ENGINE: RECALIBRATED BREAKTHROUGH LOGIC ---
def calculate_terminal_physics(reach_goal_n, n_plus, weeks, m_type):
    # Step 1: Find Raw Lambda for the N+ goal using Poisson tail
    l_raw = 0
    for l in np.arange(0.1, 250.0, 0.1):
        if (1 - stats.poisson.cdf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    # Step 2: Recency/Duration Adjustment
    # Every extra week requires more frequency to combat memory decay.
    # We apply a 'Maintenance Multiplier' of ~12% per additional week.
    maintenance_load = 1 + (weeks - 1) * 0.12
    l_impact = round(l_raw * 1.3 * maintenance_load, 1) # 1.3 is base Indian clutter factor
    
    # Step 3: Frequency Grading (Your Logic)
    if l_impact < 6.0:
        f_tier, f_color, f_outcome = "FORGETTABLE", "#64748B", "High wastage; brand signal is lost in digital noise."
    elif 6.0 <= l_impact < 10.0:
        f_tier, f_color, f_outcome = "CHALLENGER", "#00f2ff", "Establishing presence; requires high creative salience."
    elif 10.0 <= l_impact <= 12.0:
        f_tier, f_color, f_outcome = "SWEET SPOT", "#22C55E", "Optimal Recall. High probability of Aided Awareness."
    else:
        f_tier, f_color, f_outcome = "DOMINANT", "#bc13fe", "Category ownership; risk of creative fatigue (Ad Wear-out)."

    # Step 4: Market SOV Logic
    capacity = 60 if m_type == "Urban" else 35
    sov = round((l_impact / (capacity * weeks)) * 100, 1)
    
    if sov < 10: s_tier, s_color = "THIN", "#64748B"
    elif sov < 25: s_tier, s_color = "STRONG", "#00f2ff"
    else: s_tier, s_color = "AGGRESSIVE", "#EF4444"

    reach_1p = round((1 - math.exp(-l_impact)) * 100, 1)
    base_ecpm = 175 if m_type == "Urban" else 105
    dynamic_ecpm = round(base_ecpm * (1 + (sov / 100)), 2)
    
    return l_impact, reach_1p, sov, f_tier, f_color, f_outcome, s_tier, s_color, dynamic_ecpm

# --- 5. UI COMPONENTS ---
def metric_card_with_badge(label, value, sub_value, badge_text, badge_color, outcome_text, definition, is_impact=True):
    card_class = "metric-card-impact" if is_impact else "metric-card"
    st.markdown(f"""
        <div class="{card_class}" style="border-left: 5px solid {badge_color};">
            <div class="info-container"><div class="info-icon">i</div><span class="tooltip-text">{definition}</span></div>
            <div><div class="label">{label}</div><div class="value">{value}</div><div class="sov-badge" style="background:{badge_color}">{badge_text}</div></div>
            <div><div class="outcome-text">{outcome_text}</div><div class="sub-value" style="margin-top:4px;">{sub_value}</div></div>
        </div>
    """, unsafe_allow_html=True)

def standard_card(label, value, sub_value, definition):
    st.markdown(f"""
        <div class="metric-card">
            <div class="info-container"><div class="info-icon">i</div><span class="tooltip-text">{definition}</span></div>
            <div><div class="label">{label}</div><div class="value">{value}</div></div>
            <div class="sub-value">{sub_value}</div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR COMMANDS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; font-family:JetBrains Mono;'>PLANNING_COMMAND</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    
    st.markdown("---")
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("Gender", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS Group", ["A", "B", "C", "D", "E"], default=["A", "B"])

    st.markdown("---")
    zone_options = ["8 Metros"] + list(INDIA_GEO_DATABASE.keys())
    sel_zones = st.multiselect("Select Zones", zone_options, default=["8 Metros"])
    
    if "8 Metros" in sel_zones:
        sel_districts = st.multiselect("Top 8 Metros", sorted(METROS), default=["Mumbai", "Delhi", "Bengaluru"])
    else:
        avail_states = []
        for z in (sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()):
            avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
        sel_states_input = st.multiselect("Select States", sorted(list(set(avail_states))))
        
        avail_districts = []
        for z in INDIA_GEO_DATABASE:
            for s in sel_states_input:
                if s in INDIA_GEO_DATABASE[z]: avail_districts.extend(INDIA_GEO_DATABASE[z][s])
        sel_districts = st.multiselect("Select Districts", sorted(avail_districts))
    
    st.markdown("---")
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 3)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 7. MAIN DASHBOARD ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white; margin-bottom:0;">BREAKTHROUGH <span style="color:#00f2ff;">TERMINAL</span></p>', unsafe_allow_html=True)

if execute:
    freq, r1_perc, sov_val, f_tier, f_color, f_outcome, s_tier, s_color, d_ecpm = calculate_terminal_physics(r_goal, n_eff, weeks, m_type)
    
    # TAM Math
    geo_count = len(sel_districts) if sel_districts else 1
    universe = int(950000000 * (geo_count / 750) * (len(sel_age)/4) * (len(sel_nccs)/5) * 1.4) 
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * d_ecpm

    
    

    st.markdown('<div class="section-header">IMPACT METRICS</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: standard_card("Target TAM", f"{universe:,}", "Total Audience", "The total number of unique people in your chosen age and location. Think of this as the size of the whole stadium.")
    with c2: standard_card("Reach @ 1+", f"{r1_perc}%", f"{r1_abs:,} People", "The % of your audience who sees the ad at least once. It's like the number of people who look at your billboard.")
    with c3: metric_card_with_badge("Impact Frequency", freq, f"{total_imps:,} Total Imps", f_tier, f_color, f_outcome, "The average times one person sees your ad. In India, people need to see an ad many times to remember it over 4 weeks.")
    with c4: metric_card_with_badge("Market SOV", f"{sov_val}%", "Share of Voice", s_tier, s_color, "Presence vs Market Capacity", "How much of the digital conversation you own. Higher SOV means you are shouting louder than your rivals.")

    st.markdown('<div class="section-header">FINANCIALS</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1: standard_card("Total Budget", f"₹{int(est_budget):,}", "Est. Investment", "The total cost to hit these targets. More impact and longer duration increase this number.")
    with f2: standard_card("Dynamic eCPM", f"₹{d_ecpm}", "Cost per 1k Imps", "The cost to show your ad 1,000 times. This gets more expensive as you try to dominate the market.")
    with f3: standard_card("Cost / Unique", f"₹{round(est_budget/r1_abs, 2) if r1_abs > 0 else 0}", "Per Person reached", "The money spent to convert one person from a stranger into someone who remembers your brand.")
    with f4: standard_card("Efficiency", "OPTIMIZED", "Strategic Index", "A rating of how well your money is working. We aim for the 'Sweet Spot' of frequency.")

else:
    st.info("Terminal Ready. Adjust your Reach & Duration targets and click 'Execute'.")
