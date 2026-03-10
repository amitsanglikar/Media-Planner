import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (FINALIZED) ---
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
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .sub-text-orange { color: #FB923C; font-size: 0.75rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .stTable { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    .stButton>button {
        background: linear-gradient(90deg, #EA580C 0%, #FB923C 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important;
    }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GEOGRAPHY DATABASE (FROZEN) ---
INDIA_GEO_DATABASE = {
    "North": {"Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Shahdara", "North West Delhi", "South East Delhi"], "Haryana": ["Gurugram", "Faridabad", "Ambala", "Panipat", "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula"], "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Hoshiarpur", "Pathankot"], "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Prayagraj", "Noida", "Aligarh", "Bareilly", "Gorakhpur"], "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara", "Alwar", "Sikar"], "Uttarakhand": ["Dehradun", "Haridwar", "Haldwani", "Roorkee"], "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"], "Himachal Pradesh": ["Shimla", "Solan", "Dharamshala"]},
    "West": {"Maharashtra": ["Mumbai City", "Mumbai Suburban", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati", "Navi Mumbai", "Kolhapur"], "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Junagadh", "Anand"], "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Rewa", "Ratlam"], "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"], "Goa": ["North Goa", "South Goa"]},
    "South": {"Karnataka": ["Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi", "Ballari", "Udupi"], "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thoothukudi"], "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"], "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kakinada"], "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Malappuram", "Kollam", "Palakkad"]},
    "East/NE": {"West Bengal": ["Kolkata", "Howrah", "Asansol", "Siliguri", "Durgapur", "Bardhaman", "Malda", "Baharampur"], "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Bihar Sharif"], "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri"], "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"], "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur", "Tinsukia"], "Arunachal Pradesh": ["Itanagar", "Tawang", "Naharlagun", "Pasighat"], "Manipur": ["Imphal East", "Imphal West", "Thoubal", "Churachandpur"], "Meghalaya": ["Shillong", "Tura", "Jowai"], "Mizoram": ["Aizawl", "Lunglei", "Champhai"], "Nagaland": ["Dimapur", "Kohima", "Mokokchung", "Tuensang"], "Tripura": ["Agartala", "Dharmanagar", "Udaipur"], "Sikkim": ["Gangtok", "Namchi", "Geyzing"]}
}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    state_filled = len(st.session_state.get('state_selector', [])) > 0
    sel_zones = st.multiselect("1. Select Zones", list(INDIA_GEO_DATABASE.keys()), disabled=state_filled, key="zone_selector")
    
    avail_states = []
    for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. Select States", sorted(avail_states), disabled=len(sel_zones)>0, key="state_selector")

    avail_districts = []
    FLAT_MAP = {}
    for z in INDIA_GEO_DATABASE: FLAT_MAP.update(INDIA_GEO_DATABASE[z])
    for s in sel_states: avail_districts.extend(FLAT_MAP.get(s, []))
    sel_districts = st.multiselect("3. Select Districts", sorted(list(set(avail_districts))), disabled=len(sel_zones)>0 or not sel_states, key="dist_selector")

    st.markdown("---")
    sel_age = st.multiselect("4. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("5. Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("6. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 ANALYZING 2026 MEDIA ECOSYSTEM...'):
        # --- CALC ENGINE (Logic as frozen previously) ---
        INDIA_BASE = 962500 
        geo_weight = len(sel_zones)*0.22 if len(sel_zones)>0 else (len(sel_states)*0.045 if sel_states else 1.0)
        qual_u = int(INDIA_BASE * geo_weight * (len(sel_age)*0.25) * (len(sel_nccs)*0.2))
        planned_reach_abs = int(qual_u * (exp_reach / 100))
        total_imps_val = int(planned_reach_abs * round(eff_freq_n * (1 + (exp_reach / 150)), 1))
        campaign_freq_cap = int(max(eff_freq_n + 2, (weeks_on_air * 2.5)))

        # --- KPI ROW ---
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Universe</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Reach</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Freq Cap</div><div class="value-text">{campaign_freq_cap}</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Gross Imps</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- RESTORED TABLES (GENRE & PLATFORM) ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("<p class='label-text'>Media Platform Distribution</p>", unsafe_allow_html=True)
            platform_data = {
                "Platform": ["YouTube & OTT", "Meta (FB/IG)", "Short Video (Reels/TS)", "Search & Display"],
                "Imp. Share %": ["45%", "30%", "15%", "10%"],
                "Budgeted Imps ('000)": [f"{int(total_imps_val*0.45):,}", f"{int(total_imps_val*0.30):,}", f"{int(total_imps_val*0.15):,}", f"{int(total_imps_val*0.10):,}"]
            }
            st.table(pd.DataFrame(platform_data))

        with col_right:
            st.markdown("<p class='label-text'>Media Genre Preference</p>", unsafe_allow_html=True)
            genre_data = {
                "Genre": ["Entertainment", "News & Info", "Sports", "Lifestyle/Influencer"],
                "Universe Coverage": ["High", "Medium", "Seasonal", "Niche"],
                "Priority Index": ["9.2/10", "7.5/10", "8.1/10", "6.8/10"]
            }
            st.table(pd.DataFrame(genre_data))

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>TERMINAL STANDBY // EXECUTE TO VIEW MEDIA SPLITS</div>", unsafe_allow_html=True)
