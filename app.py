import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast
import re
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. SECURE API CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except Exception as e:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 3. ELITE-UI CSS (IMPACT MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #3B82F6;
    }
    .metric-card-orange {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(251, 146, 60, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #FB923C;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .warning-text { color: #F59E0B; font-size: 0.85rem; font-weight: 700; border: 1px solid #F59E0B; padding: 12px; border-radius: 8px; background: rgba(245, 158, 11, 0.1); }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GEOGRAPHY DATABASE (FROZEN) ---
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural", "Overall"], horizontal=True)
    st.markdown("---")
    
    sel_zones = st.multiselect("1. Select Regions", list(INDIA_GEO_DATABASE.keys()), key="zone_selector")
    avail_states = []
    for z in (sel_zones if sel_zones else INDIA_GEO_DATABASE.keys()): 
        avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. Select States", sorted(avail_states), key="state_selector")

    st.markdown("---")
    sel_age = st.multiselect("3. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("4. NCCS", ["A", "B", "C", "D", "E"], default=["A"])
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%) at N+", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 15, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    
    run_calc = st.button("EXECUTE IMPACT ANALYSIS")

# --- 6. BREAKTHROUGH PHYSICS ENGINE ---
def calculate_breakthrough_physics(target_reach_n, n_plus, weeks, market_type):
    # Clutter adjustment for Digital breakthrough in India
    clutter_factor = 1.35 if market_type == "Urban" else 1.15
    
    # Breakthrough Target: 11 exposures per 4-week base cycle (Ad Recall Threshold)
    impact_baseline = (11 / 4) * weeks
    
    required_lambda = 0
    # Solve for Lambda: Must satisfy Reach Goal AND Memory Threshold
    for l in np.arange(0.1, 80.0, 0.1):
        reach_at_n = 1 - stats.poisson.cdf(n_plus - 1, l)
        if reach_at_n >= (target_reach_n / 100):
            required_lambda = max(l, impact_baseline) * clutter_factor
            break
            
    reach_1_plus = (1 - math.exp(-required_lambda)) * 100
    weekly_cap = math.ceil(required_lambda / weeks)
    
    return required_lambda, reach_1_plus, weekly_cap

# --- 7. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white;'>Impact Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 CALCULATING AD BREAKTHROUGH COEFFICIENTS...'):
        l_val, r1_val, impact_cap = calculate_breakthrough_physics(exp_reach, eff_freq_n, weeks_on_air, m_type)
        
        # Universe Modeling
        base_u = 1500000 
        geo_weight = (len(sel_zones)*0.25 if sel_zones else len(sel_states)*0.08 if sel_states else 1.0)
        qual_u = int(base_u * geo_weight * (len(sel_age)*0.35) * (len(sel_nccs)*0.2))
        
        planned_reach_abs = int(qual_u * (exp_reach/100))
        # Gross impressions include the clutter buffer
        total_imps_val = int(planned_reach_abs * l_val)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Universe</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Reach @ {eff_freq_n}+</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Impact Cap</div><div class="value-text">{impact_cap}/Week</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Total Imps</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

        if r1_val > 98:
            st.markdown(f"<div class='warning-text'>⚠️ SATURATION ALERT: High-frequency impact requires {r1_val:.1f}% 1+ Reach. You are hitting the audience ceiling.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='color:#94A3B8; font-size:0.8rem; margin-top:15px;'>ℹ️ Ad Recall Probability: High | Total Avg Freq: {l_val:.2f} | 1+ Pool: {r1_val:.1f}%</p>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        
        

        # AI Contextual Data
        prompt = f"Media Planner India 2026. Market: {m_type}. Audience: {sel_gender}, {sel_age}, NCCS {sel_nccs}. Breakthrough Goal: {l_val:.1f} freq. Return Python dict 'genres' and 'platforms' (Top 10, Name, Reach%, Affinity, TimeSpent). Return ONLY dict."
        try:
            response = model.generate_content(prompt)
            data_dict = ast.literal_eval(re.search(r'\{.*\}', response.text, re.DOTALL).group())
            cl, cr = st.columns(2)
            with cl:
                st.markdown("<p class='label-text'>Impact Genres</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data_dict["genres"]), use_container_width=True, hide_index=True)
            with cr:
                st.markdown("<p class='label-text'>Breakthrough Platforms</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data_dict["platforms"]), use_container_width=True, hide_index=True)
        except:
            st.error("AI Bridge Connectivity Issue.")

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B; font-family:\"JetBrains Mono\";'>SYSTEM READY // MODE: AD BREAKTHROUGH & RECALL</div>", unsafe_allow_html=True)
