import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast
import re
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Impact Media Terminal 2026", layout="wide", page_icon="🏛️")

# --- 2. SECURE API CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except Exception as e:
    st.error("Setup Error: Please ensure GEMINI_API_KEY is in your secrets.")
    st.stop()

# --- 3. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #3B82F6;
    }
    .metric-card-impact {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(168, 85, 247, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #A855F7;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .sov-badge { font-size: 0.8rem; padding: 4px 12px; border-radius: 20px; font-weight: 700; margin-top: 10px; display: inline-block; }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. COMPREHENSIVE MARKET DATABASE ---
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

# --- 5. BREAKTHROUGH PHYSICS & SOV ENGINE ---
def calculate_breakthrough_logic(reach_goal, n_plus, weeks, market_type):
    # Clutter Physics: Urban requires 35% more frequency to break through
    clutter_multiplier = 1.35 if market_type == "Urban" else 1.15
    
    # Impact Frequency Goal: Base memory threshold of 11.5 per 4 weeks
    memory_threshold = (11.5 / 4) * weeks * clutter_multiplier
    
    # Solve for Required Lambda (Avg Frequency)
    req_lambda = 0
    for l in np.arange(0.1, 100.0, 0.1):
        reach_at_n = 1 - stats.poisson.cdf(n_plus - 1, l)
        if reach_at_n >= (reach_goal / 100):
            # We take the higher of mathematical requirement or memory threshold
            req_lambda = max(l, memory_threshold)
            break
            
    # SOV Logic: 2026 Inventory Capacity (Impressions per user per week)
    market_capacity_weekly = 55 if market_type == "Urban" else 35
    total_inventory_pool = market_capacity_weekly * weeks
    sov_perc = (req_lambda / total_inventory_pool) * 100
    
    # Market Impact Tiering
    if sov_perc < 5: tier, color, impact = "MAINTENANCE", "#64748B", "Low Recall / Background"
    elif sov_perc < 15: tier, color, impact = "CHALLENGER", "#3B82F6", "Solid Breakthrough"
    elif sov_perc < 25: tier, color, impact = "DOMINANT", "#A855F7", "High Top-of-Mind Awareness"
    else: tier, color, impact = "MONOPOLY", "#EF4444", "Category Ownership"
    
    return round(req_lambda, 1), round(sov_perc, 1), tier, color, impact

# --- 6. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    sel_zones = st.multiselect("1. Select Regions", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    if sel_zones:
        for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    else:
        for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
        
    sel_states = st.multiselect("2. Select States", sorted(avail_states))
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%) at N+", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 15, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    
    run_calc = st.button("EXECUTE IMPACT ANALYSIS")

# --- 7. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white;'>Impact Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 QUANTIZING MARKET BREAKTHROUGH...'):
        l_val, sov_val, tier_name, t_color, t_impact = calculate_breakthrough_logic(exp_reach, eff_freq_n, weeks_on_air, m_type)
        
        # Universe Math (Dynamic Weighting based on Geographies)
        base_u = 1250000 
        geo_weight = (len(sel_zones)*0.25 if sel_zones else len(sel_states)*0.06 if sel_states else 1.0)
        qual_u = int(base_u * geo_weight)
        
        planned_reach_abs = int(qual_u * (exp_reach/100))
        total_imps = int(planned_reach_abs * l_val)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Actual Impact Freq</div><div class="value-text">{l_val}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Total Reach Imps</div><div class="value-text">{total_imps:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-impact"><div class="label-text">Share of Voice (SOV)</div><div class="value-text">{sov_val}%</div><div class="sov-badge" style="background:{t_color}; color:white;">{tier_name}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Market Impact</div><div class="value-text" style="font-size:1.3rem; color:{t_color};">{t_impact}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # AI Intelligence Bridge
        prompt = f"Media Planner India 2026. Market: {m_type}. States: {sel_states}. Goal: {exp_reach}% reach at {eff_freq_n}+. Impact Freq: {l_val}. SOV Tier: {tier_name}. Return Python dictionary with 'genres' and 'platforms' (Top 10 each, with Reach%, Affinity, TimeSpent). ONLY dictionary."
        try:
            response = model.generate_content(prompt)
            data_dict = ast.literal_eval(re.search(r'\{.*\}', response.text, re.DOTALL).group())
            cl, cr = st.columns(2)
            with cl:
                st.markdown("<p class='label-text'>High-Impact Genres</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data_dict["genres"]), use_container_width=True, hide_index=True)
            with cr:
                st.markdown("<p class='label-text'>Breakthrough Platforms</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data_dict["platforms"]), use_container_width=True, hide_index=True)
        except:
            st.error("AI Bridge Connectivity Issue.")
else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>SYSTEM READY // MODE: AD BREAKTHROUGH & SOV SIMULATION</div>", unsafe_allow_html=True)
