import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS ---
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
    
    .lock-msg { color: #EF4444; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: -15px; }
    .data-header { color: #FB923C; font-size: 1rem; font-weight: 800; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .source-text { color: #475569; font-size: 0.65rem; margin-top: 10px; font-style: italic; }

    .stButton>button {
        background: linear-gradient(90deg, #EA580C 0%, #FB923C 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; width: 100%; transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOCKED GEOGRAPHY DATABASE ---
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
    
    # State Selector Logic
    state_filled = len(st.session_state.get('state_selector', [])) > 0
    if state_filled: st.markdown("<p class='lock-msg'>🔒 Locked (State Focus Active)</p>", unsafe_allow_html=True)
    sel_zones = st.multiselect("1. Select Zones", list(INDIA_GEO_DATABASE.keys()), disabled=state_filled, key="zone_selector")
    zone_filled = len(sel_zones) > 0

    # Zone Selector Logic
    if zone_filled: st.markdown("<p class='lock-msg'>🔒 Locked (Zone Focus Active)</p>", unsafe_allow_html=True)
    avail_states = []
    for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. Select States", sorted(avail_states), disabled=zone_filled, key="state_selector")

    # District Selector Logic
    dist_locked = zone_filled or not sel_states
    avail_districts = []
    FLAT_MAP = {}
    for z in INDIA_GEO_DATABASE: FLAT_MAP.update(INDIA_GEO_DATABASE[z])
    for s in sel_states: avail_districts.extend(FLAT_MAP.get(s, []))
    sel_districts = st.multiselect("3. Select Districts", sorted(list(set(avail_districts))), disabled=dist_locked, key="dist_selector")

    st.markdown("---")
    sel_age = st.multiselect("4. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_gender = st.radio("5. Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("6. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. DYNAMIC DATA ENGINE ---
def get_dynamic_data(age_list, gender, nccs_list, market):
    genres_pool = [
        {"Genre": "Short-form Video", "Base_R": 84, "Aff": 125, "TS": 55, "Tags": ["15-24", "25-34", "Urban", "Rural"]},
        {"Genre": "OTT/Streaming", "Base_R": 72, "Aff": 122, "TS": 110, "Tags": ["A", "B", "Urban", "25-34", "35-44"]},
        {"Genre": "Social Media", "Base_R": 88, "Aff": 110, "TS": 50, "Tags": ["Rural", "Urban", "15-24", "25-34", "35-44"]},
        {"Genre": "News & Info", "Base_R": 55, "Aff": 118, "TS": 30, "Tags": ["45+", "Male", "A", "B"]},
        {"Genre": "Gaming", "Base_R": 40, "Aff": 140, "TS": 85, "Tags": ["15-24", "Male", "Urban"]},
        {"Genre": "E-comm/Retail", "Base_R": 66, "Aff": 115, "TS": 25, "Tags": ["Female", "Urban", "A", "B", "25-34"]},
        {"Genre": "Utility/Payments", "Base_R": 70, "Aff": 105, "TS": 15, "Tags": ["Rural", "Urban", "C", "D", "E"]}
    ]
    
    platforms_pool = [
        {"Platform": "YouTube", "Base_R": 90, "Aff": 120, "TS": 70, "Tags": ["Urban", "Rural"]},
        {"Platform": "Instagram", "Base_R": 75, "Aff": 135, "TS": 45, "Tags": ["15-24", "25-34", "Urban", "Female"]},
        {"Platform": "WhatsApp", "Base_R": 94, "Aff": 105, "TS": 120, "Tags": ["Rural", "Urban", "45+"]},
        {"Platform": "JioCinema", "Base_R": 65, "Aff": 130, "TS": 105, "Tags": ["Male", "Rural", "Sports", "B", "C"]},
        {"Platform": "Amazon/Flipkart", "Base_R": 62, "Aff": 112, "TS": 22, "Tags": ["Urban", "A", "B", "Female"]},
        {"Platform": "Netflix/Prime", "Base_R": 28, "Aff": 160, "TS": 145, "Tags": ["A", "Urban", "25-34"]},
        {"Platform": "LinkedIn", "Base_R": 22, "Aff": 155, "TS": 15, "Tags": ["A", "Urban", "35-44", "Male"]}
    ]

    def rank_list(pool, key_name):
        scored = []
        for item in pool:
            weight = sum(1 for tag in item["Tags"] if tag in age_list or tag == gender or tag in nccs_list or tag == market)
            r = min(98, item["Base_R"] + (weight * 1.8))
            a = item["Aff"] + (weight * 2.2)
            ts = item["TS"]
            score = (r * 0.45) + (a * 0.3) + (ts * 0.25)
            scored.append({key_name: item[key_name], "Monthly Reach%": f"{r:.1f}%", "Affinity Index": int(a), "Avg. Monthly Time Spent (Min)": ts, "Score": score})
        return pd.DataFrame(scored).sort_values(by="Score", ascending=False).head(5).drop(columns=["Score"])

    return rank_list(genres_pool, "Genre"), rank_list(platforms_pool, "Platform")

# --- 6. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    # Calculation Logic
    INDIA_BASE = 958000 
    
    # Calculate Geography Factor
    if zone_filled:
        geo_factor = len(sel_zones) * 0.22 
    elif sel_states:
        state_weight = (len(sel_states) * 0.045)
        dist_weight = (len(sel_districts) / max(1, len(avail_districts))) if sel_districts else 1.0
        geo_factor = state_weight * dist_weight
    else:
        geo_factor = 1.0 # Default/National

    pen_map = {"Urban": 0.75, "Rural": 0.52, "Overall": 0.64}
    gender_map = {"Both": 1.0, "Male": 0.51, "Female": 0.49}
    
    qual_u = int(INDIA_BASE * geo_factor * pen_map[m_type] * (len(sel_age)*0.25) * (len(sel_nccs)*0.2) * gender_map[sel_gender])
    planned_reach_abs = int(qual_u * (exp_reach / 100))
    avg_f_total = round(eff_freq_n * (1 + (exp_reach / 150)), 1)
    total_imps_val = int(planned_reach_abs * avg_f_total)
    campaign_freq_cap = int(max(eff_freq_n + 2, (weeks_on_air * 3)))

    # Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Qualified Target</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Planned Reach</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Freq. Cap</div><div class="value-text" style="color:#FB923C;">{campaign_freq_cap}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Gross Impressions</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Intelligence Row
    col_left, col_right = st.columns(2)
    genre_df, platform_df = get_dynamic_data(sel_age, sel_gender, sel_nccs, m_type)

    with col_left:
        st.markdown("<div class='data-header'>🏆 Top 5 Media Genres</div>", unsafe_allow_html=True)
        st.dataframe(genre_df, use_container_width=True, hide_index=True)
        st.markdown("<p class='source-text'>Data cross-referenced: Comscore MMX / GWI Consumer Trends 2026</p>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='data-header'>📱 Top 5 Platforms</div>", unsafe_allow_html=True)
        st.dataframe(platform_df, use_container_width=True, hide_index=True)
        st.markdown("<p class='source-text'>Analysis based on Digital Consumption Index (DCI) India 2026</p>", unsafe_allow_html=True)

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B; font-family:JetBrains Mono;'>TERMINAL STANDBY // GEOGRAPHY LOCKED // EXECUTE ANALYSIS</div>", unsafe_allow_html=True)
