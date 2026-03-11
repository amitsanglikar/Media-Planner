import streamlit as st
import pandas as pd
import numpy as np
import math
from scipy import stats

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Virtual Digital Media Planning Tool", layout="wide", page_icon="📡")

# --- 2. NEON-TERMINAL STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 420px !important; }
    .metric-card {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1);
        padding: 1.25rem; border-radius: 10px; border-left: 4px solid #00f2ff;
        min-height: 160px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .value { color: #ffffff; font-size: 1.9rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.75rem; color: #888; margin-top: 4px; font-weight: 500; }
    .source-text { font-size: 0.6rem; color: #555; margin-top: 6px; font-style: italic; border-top: 1px solid #222; padding-top: 4px; }
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 8px 15px; border-radius: 4px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 25px 0 12px 0; font-size: 0.85rem; letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DEFINITIVE GEO DATABASE ---
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

# --- 4. ENGINE (DURATION-SENSITIVE PHYSICS) ---
def calculate_media_physics(reach_goal_n, n_plus, weeks, market_choice):
    # Weekly market capacity (potential exposures)
    m_cap = 60 if market_choice == "Urban" else 30 if market_choice == "Rural" else 45
    base_ecpm = 175 if market_choice == "Urban" else 105 if market_choice == "Rural" else 140

    # Step 1: Solve for Total Lambda (Mean Impressions per person)
    l_total = 0.01
    for l in np.arange(0.01, 500.0, 0.05):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_total = l
            break
            
    # Step 2: 1+ Reach Build over time
    # This formula makes 1+ Reach build cumulatively over weeks
    # A 1-week burst requires higher R1 to hit the N+ goal.
    decay_constant = 1 + (math.log(weeks) * 0.28)
    r1_perc = (1 - math.exp(-l_total / decay_constant)) * 100
    
    # Mathematical guardrail: R1 must be >= Rn
    r1_perc = max(r1_perc, reach_goal_n * 1.1)
    if r1_perc > 98: r1_perc = 98.0

    # Step 3: Average Plan Frequency (1+)
    # Friction factor for 2026 digital clutter
    avg_freq = (l_total / (r1_perc / 100)) * 1.3
    
    # Step 4: Share of Voice (SOV)
    sov_perc = ((avg_freq / weeks) / m_cap) * 100
    
    # Step 5: Dynamic eCPM
    d_ecpm = base_ecpm * (1 + (sov_perc / 100))
    
    return round(avg_freq, 1), round(r1_perc, 1), round(sov_perc, 1), round(d_ecpm, 2)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>PLANNING_INPUTS</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Selection", ["Urban", "Rural", "Both"], index=2)
    
    def all_selector(label, options):
        sel = st.multiselect(label, ["ALL"] + options, default=["ALL"])
        return options if "ALL" in sel else sel

    sel_age = all_selector("Target Age", ["15-24", "25-34", "35-44", "45+"])
    sel_gender = st.radio("Gender", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = all_selector("NCCS Group", ["A", "B", "C", "D", "E"])
    
    st.markdown("---")
    sel_zones = all_selector("Select Zones", list(INDIA_GEO_DATABASE.keys()))
    
    available_states = []
    for z in sel_zones: available_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = all_selector("Select States", sorted(available_states))
    
    available_districts = []
    if sel_states:
        for z in sel_zones:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]: available_districts.extend(INDIA_GEO_DATABASE[z][s])
    sel_districts = all_selector("Select Districts", sorted(available_districts))

    st.markdown("---")
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 27)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 2)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 6. MAIN DASHBOARD ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white;">VIRTUAL DIGITAL <span style="color:#00f2ff;">PLANNER</span></p>', unsafe_allow_html=True)

if execute:
    freq, r1_perc, sov_val, d_ecpm = calculate_media_physics(r_goal, n_eff, weeks, m_type)
    
    # UNIVERSE CALCULATIONS
    TRAI_IAMAI_2026 = 950000000 
    m_factor = 0.48 if m_type == "Urban" else 0.52 if m_type == "Rural" else 1.0
    d_factor = (len(sel_age)/4) * (len(sel_nccs)/5) * (0.5 if sel_gender != "Both" else 1.0)
    
    total_dists = sum(len(d) for s in INDIA_GEO_DATABASE.values() for d in s.values())
    g_factor = len(sel_districts)/total_dists if sel_districts else len(sel_states)/28 if sel_states else 1.0
    
    source = "TRAI & IAMAI 2026"
    if sel_districts or sel_states:
        source = "Meta Audience Insights Overrides"
        g_factor *= 0.85

    universe = int(TRAI_IAMAI_2026 * m_factor * d_factor * g_factor * 0.72)
    reached_heads = int(universe * (r1_perc / 100))
    total_imps = int(reached_heads * freq)
    budget = (total_imps / 1000) * d_ecpm

    st.markdown('<div class="section-header">AUDIENCE & INTENSITY</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">1. Addressable Universe</div><div class="value">{universe:,}</div><div class="sub-value">{m_type} | {sel_gender} | Ages: {", ".join(sel_age)}</div><div class="source-text">Source: {source}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">2. 1+ Reach Required</div><div class="value">{r1_perc}%</div><div class="sub-value">Decay adjusted for {weeks} weeks build</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card"><div class="label">3. Frequency (1+)</div><div class="value">{freq}</div><div class="sub-value">Required for {r_goal}% @ {n_eff}+</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">DELIVERY & INVESTMENT</div>', unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4: st.markdown(f'<div class="metric-card"><div class="label">4. Impressions</div><div class="value">{total_imps:,}</div><div class="sub-value">Total delivery for duration</div></div>', unsafe_allow_html=True)
    with c5: st.markdown(f'<div class="metric-card"><div class="label">5. Total Budget</div><div class="value">₹{int(budget):,}</div><div class="sub-value">Estimated Gross Spend</div></div>', unsafe_allow_html=True)
    with c6: st.markdown(f'<div class="metric-card"><div class="label">6. Share of Voice (SOV)</div><div class="value">{sov_val}%</div><div class="sub-value">Weekly Ad Pressure vs. Capacity</div></div>', unsafe_allow_html=True)
