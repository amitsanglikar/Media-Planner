import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; width: 100%;
    }
    .stTable { background: rgba(30, 41, 59, 0.1); border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXHAUSTIVE GEOGRAPHY DATABASE ---
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

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    sel_zones = st.multiselect("1. Select Zones", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    if sel_zones:
        for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    else:
        for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. Select States", sorted(avail_states))

    avail_districts = []
    FLAT_MAP = {}
    for z in INDIA_GEO_DATABASE: FLAT_MAP.update(INDIA_GEO_DATABASE[z])
    for s in sel_states: avail_districts.extend(FLAT_MAP.get(s, []))
    sel_districts = st.multiselect("3. Select Districts", sorted(list(set(avail_districts))), disabled=not sel_states)

    st.markdown("---")
    sel_age = st.multiselect("4. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("5. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    st.markdown("### Strategy & Continuity")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    # --- CALCULATION ENGINE ---
    INDIA_BASE = 958000 
    state_factor = (len(sel_states) / 36) if sel_states else 1.0
    dist_factor = (len(sel_districts) / 766) if sel_districts else 1.0 
    
    pen_map = {"Urban": 0.75, "Rural": 0.52, "Overall": 0.64}
    qual_u = int(INDIA_BASE * state_factor * dist_factor * pen_map[m_type] * (len(sel_age)*0.25) * (len(sel_nccs)*0.2))
    
    # Core Strategy Logic
    avg_f_total = round(eff_freq_n * (1 + (exp_reach / 180)), 1)
    planned_reach_abs = int(qual_u * (exp_reach / 100))
    total_imps_val = int(planned_reach_abs * avg_f_total)
    
    # THE RESTORED FREQ CAP
    # Global cap to ensure Reach builds over duration without over-saturation
    campaign_freq_cap = int(avg_f_total * 2.2)

    # --- TOP KPI ROW (FREQ CAP RESTORED) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="label-text">Qualified Target</div><div class="value-text">{qual_u:,}</div><div class="sub-text">Universe (\'000)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="label-text">Planned Reach</div><div class="value-text">{planned_reach_abs:,}</div><div class="sub-text">{exp_reach}% Reach Goal</div></div>', unsafe_allow_html=True)
    with c3:
        # Restore Freq Cap here for maximum visibility
        st.markdown(f'<div class="metric-card"><div class="label-text">Freq. Cap</div><div class="value-text" style="color:#60A5FA;">{campaign_freq_cap}</div><div class="sub-text">Campaign Global Limit</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="label-text">Gross Impressions</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div><div class="sub-text">Total Volume (\'000)</div></div>', unsafe_allow_html=True)

    # --- DATA MATRIX ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label-text'>Strategic Control Matrix</p>", unsafe_allow_html=True)
    
    matrix_data = {
        "Strategic Parameter": ["Effective Freq (N+)", "Campaign Duration", "Overall Avg Frequency", "Campaign Freq Cap", "Gross Impressions ('000)"],
        "Value": [f"{eff_freq_n}+", f"{weeks_on_air} Weeks", f"{avg_f_total}", f"{campaign_freq_cap}", f"{total_imps_val:,}"],
        "Planning Rationale": ["Impact Threshold", "Continuity Period", "Weighted Mean", "Saturation Protection", "Inventory Pipeline"]
    }
    st.table(pd.DataFrame(matrix_data))
    st.markdown("</div>", unsafe_allow_html=True)

    

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>Terminal Standby. Geography Locked. Click EXECUTE.</div>", unsafe_allow_html=True)
