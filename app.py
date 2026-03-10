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

# --- 2. ELITE-UI STYLING (THE TERMINAL LOOK) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 380px !important; }
    
    /* Header Styling */
    .main-title { font-size: 2.5rem; font-weight: 800; color: white; letter-spacing: -1px; margin-bottom: 0px; }
    .sub-title { color: #3B82F6; font-family: 'JetBrains Mono'; font-size: 0.9rem; margin-bottom: 30px; text-transform: uppercase; }

    /* Card Styling */
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3B82F6; height: 100%;
        backdrop-filter: blur(10px);
    }
    .metric-card-impact {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(168, 85, 247, 0.2);
        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #A855F7; height: 100%;
        backdrop-filter: blur(10px);
    }
    .label { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: #F8FAFC; font-size: 2.2rem; font-weight: 800; margin-top: 5px; }
    .sub-value { font-size: 0.85rem; color: #64748B; margin-top: 8px; font-weight: 600; display: block; }
    
    /* Badge Styling */
    .sov-badge { 
        padding: 6px 14px; border-radius: 6px; font-size: 0.7rem; font-weight: 900; 
        margin-top: 12px; display: inline-block; color: white; letter-spacing: 1px;
    }
    
    /* Table Headers */
    .section-header {
        background: linear-gradient(90deg, #1E293B 0%, transparent 100%);
        padding: 10px 20px; border-radius: 4px; border-left: 3px solid #3B82F6;
        color: #F8FAFC; font-weight: 700; margin: 25px 0 15px 0; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (FROZEN) ---
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

# --- 4. ENGINE: PHYSICS & BUDGET ---
def calculate_physics(reach_goal_n, n_plus, weeks, m_type):
    clutter = 1.45 if m_type == "Urban" else 1.20
    memory_decay = (11.0 / 4) * weeks * clutter
    
    l_final = 0
    for l in np.arange(0.1, 150.0, 0.1):
        r_at_n = (1 - stats.poisson.cdf(n_plus - 1, l)) * 100
        if r_at_n >= reach_goal_n:
            l_final = max(l, memory_decay)
            break
            
    reach_1p = (1 - math.exp(-l_final)) * 100
    capacity = 55 if m_type == "Urban" else 30
    sov = (l_final / (capacity * weeks)) * 100
    
    if sov < 7: tier, color, desc = "MAINTENANCE", "#64748B", "Competitive Parity"
    elif sov < 18: tier, color, desc = "CHALLENGER", "#3B82F6", "Breakthrough Recall"
    elif sov < 28: tier, color, desc = "DOMINANT", "#A855F7", "Market Authority"
    else: tier, color, desc = "LEADER", "#EF4444", "Category Ownership"
    
    return round(l_final, 1), round(reach_1p, 1), round(sov, 1), tier, color, desc

# --- 5. COMMAND CENTER SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/3B82F6/radar.png", width=60)
    st.title("Campaign Command")
    m_type = st.radio("Market Classification", ["Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    sel_zones = st.multiselect("Geography: Zones", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    for z in (sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()):
        avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("Geography: States", sorted(avail_states))
    
    avail_districts = []
    if sel_states:
        for z in INDIA_GEO_DATABASE:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]: avail_districts.extend(INDIA_GEO_DATABASE[z][s])
    sel_districts = st.multiselect("Geography: Districts (Filter)", sorted(avail_districts))
    
    st.markdown("---")
    r_goal = st.slider("Reach Target % (Effective)", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Campaign Duration (Weeks)", 1, 12, 4)
    
    st.markdown("---")
    execute = st.button("RUN IMPACT PROJECTION", use_container_width=True)

# --- 6. DASHBOARD MAIN VIEW ---
st.markdown('<p class="main-title">Impact Media Terminal <span style="color:#3B82F6;">2026</span></p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Advanced Reach & Share-of-Voice Physics Engine</p>', unsafe_allow_html=True)

if execute:
    freq, r1_perc, sov_val, tier, t_color, t_desc = calculate_physics(r_goal, n_eff, weeks, m_type)
    
    # Advanced Geography Multiplier
    base_pop = 1450000 
    geo_scale = len(sel_districts) if sel_districts else (len(sel_states) * 12) if sel_states else 120
    universe = int(base_pop * (geo_scale / 100))
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    
    # Estimated Cost Factor (Simulated)
    cpm = 180 if m_type == "Urban" else 110
    est_budget = (total_imps / 1000) * cpm

    # ROW 1: CORE METRICS
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f'''<div class="metric-card"><div class="label">Total Universe (TAM)</div>
        <div class="value">{universe:,}</div><div class="sub-value">Active Digital Population</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card"><div class="label">Total Campaign Reach</div>
        <div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} Unique Aud. Reached</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card"><div class="label">Avg Freq & Impressions</div>
        <div class="value">{freq}x</div><div class="sub-value">{total_imps:,} Total Ad Delivery</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card-impact"><div class="label">Share of Voice (SOV)</div>
        <div class="value" style="color:{t_color};">{sov_val}%</div><div class="sov-badge" style="background:{t_color}">{tier}</div>
        <div class="sub-value" style="color:#F8FAFC;">{t_desc}</div></div>''', unsafe_allow_html=True)

    # IMAGE TRIGGER: Visualizing Reach/Frequency Build
    

    # ROW 2: AI STRATEGY ENGINE
    st.markdown('<div class="section-header">PLATFORM AFFINITY & GENRE PENETRATION (AI GEN-2 PROJECTION)</div>', unsafe_allow_html=True)
    
    try:
        # Specialized prompt for professional output
        ai_prompt = (
            f"As a 2026 India Media Strategist, provide a Top 10 Media Genres and Top 10 Media Platforms table "
            f"for a {m_type} market with {sov_val}% Share of Voice. Context: {sel_states} geography. "
            f"Columns for Genres: Genre, Reach%, Affinity, Index. "
            f"Columns for Platforms: Platform, Daily Time Spent, Reach%, Growth. "
            f"Return ONLY a Python dictionary object."
        )
        
        with st.spinner("Synchronizing with 2026 Intelligence Nodes..."):
            response = model.generate_content(ai_prompt)
            clean_data = re.search(r'\{.*\}', response.text, re.DOTALL).group()
            strategy_data = ast.literal_eval(clean_data)
            
            col_left, col_right = st.columns(2)
            with col_left:
                st.dataframe(pd.DataFrame(strategy_data["genres"]), 
                             use_container_width=True, hide_index=True)
            with col_right:
                st.dataframe(pd.DataFrame(strategy_data["platforms"]), 
                             use_container_width=True, hide_index=True)
                             
    except Exception as e:
        st.error("AI Bridge Connectivity Issue. Verify API Key limits.")

    # BUDGET & ALLOCATION SECTION
    st.markdown('<div class="section-header">ESTIMATED MEDIA BUDGETING & KPI VALUE</div>', unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f'<div class="metric-card"><div class="label">Est. Budget Req.</div><div class="value">₹{int(est_budget):,}</div></div>', unsafe_allow_html=True)
    with b2:
        st.markdown(f'<div class="metric-card"><div class="label">Cost Per Reach (CPR)</div><div class="value">₹{round(est_budget/r1_abs, 2)}</div></div>', unsafe_allow_html=True)
    with b3:
        st.markdown(f'<div class="metric-card"><div class="label">Ad Clutter Resistance</div><div class="value">{"HIGH" if sov_val > 20 else "MEDIUM"}</div></div>', unsafe_allow_html=True)

else:
    # STANDBY SCREEN
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.2); padding: 100px; border-radius: 20px; border: 1px dashed #3B82F6; text-align: center;">
        <p style="color: #64748B; font-family: 'JetBrains Mono';">SYSTEM STANDBY // WAITING FOR COMMAND PARAMETERS</p>
        <p style="color: #3B82F6; font-size: 0.8rem;">Select Geography and Breakthrough Goals in the Sidebar to Execute Simulation.</p>
    </div>
    """, unsafe_allow_html=True)
