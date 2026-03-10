import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (SaaS Dark Theme) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] .stWidgetLabel p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h2 {
        color: #F8FAFC !important; 
        font-weight: 600 !important;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.3);
    }
    
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .value-text { color: #F8FAFC; font-size: 2.3rem; font-weight: 800; margin-top: 8px; }
    .sub-text { color: #3B82F6; font-size: 0.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; width: 100%; transition: 0.3s;
    }
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

# --- 4. SIDEBAR LOGIC (PERMANENTLY LOCKED) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Targeting Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Classification", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")

    # Cascading Selection Logic
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
    # NEW KPI INPUTS
    exp_reach = st.slider("Expected Reach %", 5, 100, 45, step=5)
    eff_freq = st.number_input("Effective Frequency (N+)", 1, 15, 3)
    
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white; letter-spacing:-1px;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B;'>Standardized Intelligence Engine • Figures in '000s</p>", unsafe_allow_html=True)

if run_calc:
    # DATA ENGINE
    INDIA_UNIVERSE = 958000
    state_ratio = (len(sel_states) / 36) if sel_states else 1.0
    dist_ratio = (len(sel_districts) / max(1, len(avail_districts))) if sel_districts else 1.0
    
    market_pot = int(INDIA_UNIVERSE * state_ratio * dist_ratio)
    age_weights = {"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}
    qual_u = int(market_pot * sum([age_weights[a] for a in sel_age]) * (len(sel_nccs)*0.2))
    planned_reach_abs = int(qual_u * (exp_reach / 100))

    # KPI GRID
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="label-text">Qualified Target</div><div class="value-text">{qual_u:,}</div><div class="sub-text">Audience Base</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="label-text">Planned Reach</div><div class="value-text">{planned_reach_abs:,}</div><div class="sub-text">{exp_reach}% Coverage</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="label-text">Freq Goal</div><div class="value-text">{eff_freq}x</div><div class="sub-text">Effective N+</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="label-text">Impressions</div><div class="value-text">{(planned_reach_abs * eff_freq):,}</div><div class="sub-text">Total Volume</div></div>', unsafe_allow_html=True)

    

    # DEPLOYMENT FUNNEL
    st.markdown("<br><div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label-text' style='text-align:center;'>Audience Sizing Funnel</p>", unsafe_allow_html=True)
    fig = go.Figure(go.Funnel(
        y=["Market Potential", "Qualified Target", "Planned Reach"],
        x=[market_pot, qual_u, planned_reach_abs],
        textinfo="value+percent initial",
        marker={"color": ["#1E293B", "#3B82F6", "#60A5FA"], "line": {"width": 2, "color": "white"}}
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), height=400, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h3 style='color:#334155;'>SYSTEM READY</h3>
            <p style='color:#64748B;'>Geography locked. Adjust targeting parameters and click EXECUTE.</p>
        </div>
    """, unsafe_allow_html=True)
