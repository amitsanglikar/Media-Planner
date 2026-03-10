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

# --- 2. ELITE-UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 380px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3B82F6; height: 100%;
    }
    .metric-card-impact {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(168, 85, 247, 0.2);
        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #A855F7; height: 100%;
    }
    .label { color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: #F8FAFC; font-size: 1.9rem; font-weight: 800; margin-top: 5px; }
    .sub-value { font-size: 0.85rem; color: #64748B; margin-top: 5px; font-weight: 600; }
    .sov-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE 2026 PAN-INDIA DATABASE ---
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

# --- 4. THE PHYSICS ENGINE ---
def calculate_physics(reach_goal_n, n_plus, weeks, m_type):
    clutter = 1.35 if m_type == "Urban" else 1.15
    memory_threshold = (11.5 / 4) * weeks * clutter
    
    # Solve for Average Freq (Lambda)
    l_final = 0
    for l in np.arange(0.1, 150.0, 0.1):
        r_at_n = (1 - stats.poisson.cdf(n_plus - 1, l)) * 100
        if r_at_n >= reach_goal_n:
            l_final = max(l, memory_threshold)
            break
            
    # Derive 1+ Reach and SOV
    reach_1p = (1 - math.exp(-l_final)) * 100
    capacity = 60 if m_type == "Urban" else 35
    sov = (l_final / (capacity * weeks)) * 100
    
    if sov < 5: tier, color, desc = "MAINTENANCE", "#64748B", "Low Share; Competitive Noise"
    elif sov < 15: tier, color, desc = "CHALLENGER", "#3B82F6", "Solid Breakthrough; Meaningful Recall"
    elif sov < 25: tier, color, desc = "DOMINANT", "#A855F7", "High Top-of-Mind Awareness"
    else: tier, color, desc = "MONOPOLY", "#EF4444", "Category Ownership; Max Impact"
    
    return round(l_final, 1), round(reach_1p, 1), round(sov, 1), tier, color, desc

# --- 5. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.title("Campaign Command")
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    sel_zones = st.multiselect("1. Select Zones", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    if sel_zones:
        for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    else:
        for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    
    sel_states = st.multiselect("2. Select States", sorted(avail_states))
    
    avail_districts = []
    if sel_states:
        for z in INDIA_GEO_DATABASE:
            for s in sel_states:
                if s in INDIA_GEO_DATABASE[z]: avail_districts.extend(INDIA_GEO_DATABASE[z][s])
    sel_districts = st.multiselect("3. Select Districts (Optional)", sorted(avail_districts))
    
    st.markdown("---")
    r_goal = st.slider("Reach Goal % @ N+", 5, 95, 45)
    n_eff = st.number_input("N+ Effective Freq", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    
    execute = st.button("EXECUTE IMPACT PHYSICS")

# --- 6. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white;'>Media Impact <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if execute:
    freq, r1_perc, sov, tier, t_color, t_desc = calculate_physics(r_goal, n_eff, weeks, m_type)
    
    # Universe Modeling (Dynamic based on Geography selection)
    base_pop = 1200000 
    geo_count = len(sel_districts) if sel_districts else (len(sel_states) * 10) if sel_states else 100
    universe = int(base_pop * (geo_count / 100))
    
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f'''<div class="metric-card"><div class="label">Total Universe</div>
        <div class="value">{universe:,}</div><div class="sub-value">Targeted Audience (TAM)</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card"><div class="label">Reach @ 1+ (Derived)</div>
        <div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} Unique Reached</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card"><div class="label">Actual Freq & Imps</div>
        <div class="value">{freq} Freq</div><div class="sub-value">{total_imps:,} Total Impressions</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card-impact"><div class="label">SOV & Market Impact</div>
        <div class="value" style="color:{t_color};">{sov}%</div><div class="sov-badge" style="background:{t_color}">{tier}</div>
        <div class="sub-value" style="color:#F8FAFC;">{t_desc}</div></div>''', unsafe_allow_html=True)

    st.markdown("---")
    
    
    

    # AI Insight Bridge
    try:
        prompt = f"Media Planner 2026 India. Market: {m_type}. State: {sel_states}. Freq: {freq}. SOV: {sov}%. Impact: {tier}. Return Python dict 'genres' and 'platforms' (Top 10)."
        response = model.generate_content(prompt)
        data = ast.literal_eval(re.search(r'\{.*\}', response.text, re.DOTALL).group())
        cl, cr = st.columns(2)
        with cl: st.dataframe(pd.DataFrame(data["genres"]), use_container_width=True, hide_index=True)
        with cr: st.dataframe(pd.DataFrame(data["platforms"]), use_container_width=True, hide_index=True)
    except:
        st.warning("AI Insights Engine offline.")
else:
    st.info("System Ready. Select your markets and Breakthrough goals to begin.")
