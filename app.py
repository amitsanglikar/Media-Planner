import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (FROZEN) ---
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
    .stTable { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    .lock-msg { color: #EF4444; font-size: 0.65rem; font-weight: 800; text-transform: uppercase; margin-bottom: -15px; }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. EXHAUSTIVE GEOGRAPHY DATABASE (RESTORED & FROZEN) ---
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

# --- 4. INPUT-LED GENERATIVE ENGINE ---
def get_media_affinity_matrix(age, gender, nccs, market_type, regions):
    """
    Calculates Reach, Affinity, and Time Spent based on the intersection 
    of Demographics and Geography (Region/Market Type).
    """
    genres = ["Short Video", "Social Media", "OTT Video", "News/Information", "Gaming", "E-Commerce/Search"]
    
    # Logic Weights
    is_young = any(a in ["15-24", "25-34"] for a in age)
    is_urban = (market_type == "Urban")
    is_south = ("South" in regions)
    is_female = (gender == "Female")
    
    results = []
    for g in genres:
        # Base industry standard baseline
        reach = 45; affinity = 100; time_m = 35
        
        # Applying AI Modifiers based on Sidebar Inputs
        if g == "Short Video" and is_young: reach += 35; affinity += 40; time_m += 45
        if g == "OTT Video" and is_urban: reach += 20; affinity += 25; time_m += 60
        if g == "News/Information" and not is_young: reach += 40; affinity += 35; time_m += 15
        if g == "Social Media" and is_female: reach += 15; affinity += 20; time_m += 25
        if g == "OTT Video" and is_south: reach += 10; affinity += 15 # High OTT penetration in South India
        
        score = (reach * 0.4) + (affinity * 0.4) + (time_m * 0.2)
        
        results.append({
            "Media Channel": g,
            "Reach%": f"{min(reach, 98)}%",
            "Affinity Index": min(affinity, 195),
            "Time Spent (Daily)": f"{time_m}m",
            "Score": score
        })
    
    df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    df["Ranking"] = range(1, len(genres) + 1)
    return df.drop(columns=["Score"])

# --- 5. SIDEBAR (RESTORED GEOGRAPHY LOGIC) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    # Zone/State/District Selection Logic
    state_filled = len(st.session_state.get('state_selector', [])) > 0
    sel_zones = st.multiselect("1. Select Regions/Zones", list(INDIA_GEO_DATABASE.keys()), disabled=state_filled, key="zone_selector")
    
    avail_states = []
    for z in INDIA_GEO_DATABASE: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. Select States", sorted(avail_states), disabled=len(sel_zones)>0, key="state_selector")

    avail_districts = []
    FLAT_MAP = {}
    for z in INDIA_GEO_DATABASE: FLAT_MAP.update(INDIA_GEO_DATABASE[z])
    for s in sel_states: avail_districts.extend(FLAT_MAP.get(s, []))
    sel_districts = st.multiselect("3. Select Districts", sorted(list(set(avail_districts))), disabled=len(sel_zones)>0 or not sel_states, key="dist_selector")

    st.markdown("---")
    sel_age = st.multiselect("4. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24"])
    sel_gender = st.radio("5. Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("6. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 6. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 GENERATING AI-LED MEDIA PLAN...'):
        # Universe Calculation Logic
        qual_u = int(962500 * (len(sel_zones)*0.22 if sel_zones else len(sel_states)*0.045) * (len(sel_age)*0.25))
        planned_reach_abs = int(qual_u * (exp_reach/100))
        total_imps_val = int(planned_reach_abs * 5.2)

        # KPI ROW
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Universe</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Reach</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Avg Freq</div><div class="value-text">5.2</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Total Imps</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # GENERATIVE MATRIX
        st.markdown("<p class='label-text'>Media Affinity Matrix (Input-Led)</p>", unsafe_allow_html=True)
        affinity_df = get_media_affinity_matrix(sel_age, sel_gender, sel_nccs, m_type, sel_zones)
        st.table(affinity_df)

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>TERMINAL STANDBY // GEOGRAPHY & DEMOGRAPHICS LOCKED</div>", unsafe_allow_html=True)
