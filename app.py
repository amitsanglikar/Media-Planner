import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (SaaS Terminal Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    [data-testid="stSidebar"] .stWidgetLabel p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h2 {
        color: #F8FAFC !important; 
        font-weight: 600 !important;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.3);
    }
    
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; width: 100%; transition: 0.3s;
    }
    
    /* Table Styling */
    .stTable { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    th { color: #3B82F6 !important; text-transform: uppercase; font-size: 0.7rem !important; }
    td { color: #F8FAFC !important; font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PERMANENT FROZEN GEOGRAPHY DATABASE ---
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

# --- 4. SIDEBAR INPUTS (LOCKED STATUS) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Control</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Classification", ["Overall", "Urban", "Rural"], horizontal=True)
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
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("Income (NCCS)", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    exp_reach = st.slider("Expected Reach %", 5, 100, 45, step=5)
    eff_freq = st.number_input("Effective Frequency (N+)", 1, 15, 3)
    
    st.markdown("---")
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN DASHBOARD OUTPUT ---
st.markdown("<h1 style='color:white; letter-spacing:-1px;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    # --- CALCULATION ENGINE ---
    INDIA_BASE_UNIVERSE = 958000 # Population in '000s
    
    # Geographic Weighting
    state_factor = (len(sel_states) / 36) if sel_states else 1.0
    dist_factor = (len(sel_districts) / 766) if sel_districts else 1.0 
    market_potential = int(INDIA_BASE_UNIVERSE * state_factor * dist_factor)
    
    # Digital Ceiling (2026 Market Estimates)
    pen_map = {"Urban": 0.75, "Rural": 0.52, "Overall": 0.64}
    active_digital_u = int(market_potential * pen_map[m_type])
    
    # Demographic Scaling
    age_weights = {"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}
    qual_u = int(active_digital_u * sum([age_weights[a] for a in sel_age]) * (len(sel_nccs) * 0.2))
    
    # DYNAMIC FREQUENCY CALCULATION (Weighted Average)
    # Average Freq = Goal N+ * (Dynamic curve based on Reach goal)
    base_goal = eff_freq
    calculated_avg_freq = round(base_goal * (1 + (exp_reach / 250)), 1)
    
    # Final Campaign Metrics
    planned_reach_abs = int(qual_u * (exp_reach / 100))
    gross_impressions_000 = int(planned_reach_abs * calculated_avg_freq)

    # --- TOP METRIC ROW ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f'''<div class="metric-card"><div class="label-text">Qualified Target</div><div class="value-text">{qual_u:,}</div><div class="sub-text">Universe ('000)</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card"><div class="label-text">Planned Reach</div><div class="value-text">{planned_reach_abs:,}</div><div class="sub-text">{exp_reach}% Reach Goal</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card"><div class="label-text">Avg. Frequency</div><div class="value-text" style="color:#60A5FA;">{calculated_avg_freq}x</div><div class="sub-text">Weighted {base_goal}+ Goal</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card"><div class="label-text">Gross Impressions</div><div class="value-text">{gross_impressions_000:,}</div><div class="sub-text">Total Volume ('000)</div></div>''', unsafe_allow_html=True)

    # --- AUDIENCE QUALIFICATION TABLE ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label-text'>Audience Qualification Lifecycle</p>", unsafe_allow_html=True)
    
    table_data = {
        "Funnel Stage": [
            "1. Market Potential (Total Pop)", 
            "2. Active Digital Universe", 
            "3. Qualified Target (Age/Income)", 
            "4. Planned Campaign Reach"
        ],
        "Audience Size ('000)": [
            f"{market_potential:,}", 
            f"{active_digital_u:,}", 
            f"{qual_u:,}", 
            f"{planned_reach_abs:,}"
        ],
        "Index %": [
            "100%", 
            f"{pen_map[m_type]*100:.0f}%", 
            f"{(qual_u/active_digital_u)*100:.1f}%", 
            f"{exp_reach}%"
        ]
    }
    st.table(pd.DataFrame(table_data))
    st.markdown("</div>", unsafe_allow_html=True)

    

    # --- GEOGRAPHIC CONTRIBUTION ---
    if sel_states:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p class='label-text'>Regional Concentration Map</p>", unsafe_allow_html=True)
        # Simplified contribution bar for clarity
        geo_df = pd.DataFrame({
            "State": sel_states,
            "Target Density (%)": [round(100/len(sel_states), 1)] * len(sel_states)
        })
        st.bar_chart(geo_df.set_index("State"))

else:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h3 style='color:#334155;'>TERMINAL STANDBY</h3>
            <p style='color:#64748B;'>Geography and Inputs Locked. Click EXECUTE to generate media plan data.</p>
        </div>
    """, unsafe_allow_html=True)
