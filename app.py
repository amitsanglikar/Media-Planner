import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (SaaS Terminal Theme + Visibility Fixes) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    
    /* Sidebar Foundation & Visibility Fix */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    [data-testid="stSidebar"] .stWidgetLabel p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] h2 {
        color: #F8FAFC !important; 
        font-weight: 600 !important;
    }
    
    /* Neumorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.3);
    }
    
    /* Typography */
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .value-text { color: #F8FAFC; font-size: 2.3rem; font-weight: 800; margin-top: 8px; }
    .sub-text { color: #3B82F6; font-size: 0.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    /* Locking Indicators */
    .lock-msg { color: #EF4444; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; display: block; }
    
    /* CTA Button */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE PERMANENT MASTER DATABASE ---
# Grouped by Region for better UX filtering
INDIA_REGIONAL_DATA = {
    "North": {
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Shahdara"],
        "Haryana": ["Ambala", "Faridabad", "Gurugram", "Hisar", "Karnal", "Panipat", "Rohtak", "Sonipat"],
        "Punjab": ["Amritsar", "Bathinda", "Jalandhar", "Ludhiana", "Mohali", "Patiala"],
        "Uttar Pradesh": ["Agra", "Aligarh", "Ayodhya", "Bareilly", "Ghaziabad", "Gorakhpur", "Jhansi", "Kanpur Nagar", "Lucknow", "Meerut", "Prayagraj", "Varanasi"],
        "Rajasthan": ["Ajmer", "Alwar", "Bikaner", "Jaipur", "Jodhpur", "Kota", "Sikar", "Udaipur"],
        "Himachal Pradesh": ["Chamba", "Hamirpur", "Kangra", "Kullu", "Mandi", "Shimla", "Solan"],
        "Jammu and Kashmir": ["Anantnag", "Baramulla", "Jammu", "Kathua", "Pulwama", "Srinagar", "Udhampur"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Nainital", "Udham Singh Nagar"],
        "Chandigarh": ["Chandigarh"], "Ladakh": ["Leh", "Kargil"]
    },
    "West": {
        "Maharashtra": ["Akola", "Amravati", "Aurangabad", "Kolhapur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nashik", "Pune", "Solapur", "Thane"],
        "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Bhavnagar", "Gandhinagar", "Jamnagar", "Kutch", "Rajkot", "Surat", "Vadodara"],
        "Goa": ["North Goa", "South Goa"],
        "Dadra and Nagar Haveli and Daman and Diu": ["Dadra and Nagar Haveli", "Daman", "Diu"],
        "Madhya Pradesh": ["Bhopal", "Gwalior", "Indore", "Jabalpur", "Rewa", "Sagar", "Ujjain"],
        "Chhattisgarh": ["Bastar", "Bilaspur", "Durg", "Korba", "Raigarh", "Raipur", "Rajnandgaon"]
    },
    "South": {
        "Andhra Pradesh": ["Alluri Sitharama Raju", "Anakapalli", "Ananthapuramu", "Annamayya", "Bapatla", "Chittoor", "Guntur", "Kakinada", "Krishna", "Kurnool", "NTR", "Palnadu", "Visakhapatnam", "Vizianagaram"],
        "Karnataka": ["Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Dharwad", "Kalaburagi", "Mysuru", "Udupi", "Vijayapura"],
        "Kerala": ["Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kochi", "Kozhikode", "Malappuram", "Thiruvananthapuram", "Thrissur"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Thanjavur", "Tiruchirappalli", "Tirunelveli", "Vellore"],
        "Telangana": ["Hyderabad", "Karimnagar", "Khammam", "Nizamabad", "Rangareddy", "Warangal"],
        "Puducherry": ["Karaikal", "Mahe", "Puducherry", "Yanam"], "Lakshadweep": ["Lakshadweep"]
    },
    "East/NE": {
        "West Bengal": ["Asansol", "Darjeeling", "Howrah", "Kolkata", "North 24 Parganas", "Paschim Medinipur", "Siliguri"],
        "Bihar": ["Araria", "Bhagalpur", "Darbhanga", "Gaya", "Muzaffarpur", "Nalanda", "Patna", "Purnia", "Rohtas", "Vaishali"],
        "Odisha": ["Balasore", "Bhubaneswar", "Cuttack", "Ganjam", "Puri", "Sambalpur", "Sundargarh"],
        "Jharkhand": ["Bokaro", "Deoghar", "Dhanbad", "East Singhbhum", "Hazaribagh", "Ranchi"],
        "Assam": ["Baksa", "Barpeta", "Cachar", "Dibrugarh", "Guwahati", "Jorhat", "Kamrup", "Kokrajhar", "Nagaon", "Tinsukia"],
        "Arunachal Pradesh": ["Anjaw", "Changlang", "Dibang Valley", "East Kameng", "Itanagar", "Lohit", "Namsai", "Papum Pare", "Tawang"],
        "Manipur": ["Bishnupur", "Churachandpur", "Imphal East", "Imphal West", "Thoubal"],
        "Meghalaya": ["East Khasi Hills", "Ri Bhoi", "West Garo Hills"],
        "Mizoram": ["Aizawl", "Lunglei"], "Nagaland": ["Dimapur", "Kohima", "Mokokchung"],
        "Tripura": ["Agartala", "West Tripura"], "Sikkim": ["Gangtok", "Namchi"],
        "Andaman and Nicobar": ["Port Blair"]
    }
}

METRO_DATA = {"Mumbai": 0.065, "Delhi": 0.072, "Bengaluru": 0.048, "Chennai": 0.038, "Kolkata": 0.035, "Hyderabad": 0.042, "Ahmedabad": 0.028, "Pune": 0.031}

# --- 4. SIDEBAR COMMAND CENTER ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Targeting Command</h2>", unsafe_allow_html=True)
    
    m_type = st.radio("Market Classification", ["Overall", "Urban", "Rural"], horizontal=True)
    lock_geo = m_type in ["Urban", "Rural"]
    
    st.markdown("---")
    
    if lock_geo: st.markdown("<span class='lock-msg'>Locked by Market Cut</span>", unsafe_allow_html=True)
    sel_metros = st.multiselect("Elite Metros", list(METRO_DATA.keys()), disabled=lock_geo)
    is_metro = len(sel_metros) > 0
    
    if is_metro: st.markdown("<span class='lock-msg'>Locked by Metro Focus</span>", unsafe_allow_html=True)
    
    # NEW: Region filter for better UX
    sel_regions = st.multiselect("Region Filter", list(INDIA_REGIONAL_DATA.keys()), disabled=is_metro)
    
    available_states = []
    if sel_regions:
        for r in sel_regions: available_states.extend(list(INDIA_REGIONAL_DATA[r].keys()))
    else:
        for r in INDIA_REGIONAL_DATA: available_states.extend(list(INDIA_REGIONAL_DATA[r].keys()))
        
    sel_states = st.multiselect("States/UTs", sorted(available_states), disabled=is_metro)
    
    # Flatten master for district search
    FLAT_MASTER = {}
    for r in INDIA_REGIONAL_DATA: FLAT_MASTER.update(INDIA_REGIONAL_DATA[r])
    
    available_districts = []
    for s in sel_states: available_districts.extend(FLAT_MASTER.get(s, []))
    
    if lock_geo or is_metro: st.markdown("<span class='lock-msg'>District Granularity Disabled</span>", unsafe_allow_html=True)
    sel_districts = st.multiselect("Filter Districts", sorted(list(set(available_districts))), 
                                   disabled=(lock_geo or is_metro or not sel_states))
    
    st.markdown("---")
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("Income (NCCS)", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white; letter-spacing:-1px;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B;'>Standardized Intelligence Engine • Figures in '000s</p>", unsafe_allow_html=True)

if run_calc:
    TOTAL_INDIA_DIGITAL = 958000
    
    if is_metro:
        geo_weight = sum([METRO_DATA[m] for m in sel_metros])
        market_label = "Metro Targeted"
    elif lock_geo:
        state_base = (len(sel_states) * 0.038) if sel_states else 1.0
        geo_weight = state_base * (0.43 if m_type == "Urban" else 0.57)
        market_label = f"{m_type} Segment"
    else:
        # Overall mode defaults to full India when no state/district filters are selected.
        if not sel_states:
            geo_weight = 1.0
            market_label = "Overall India"
        else:
            geo_weight = len(sel_states) * 0.038
            if sel_districts:
                geo_weight *= (len(sel_districts) / max(1, len(available_districts)))
                market_label = "District Focus"
            else:
                market_label = "State Focus"

    # Keep weight within valid bounds.
    geo_weight = max(0.0, min(geo_weight, 1.0))

    market_size = int(TOTAL_INDIA_DIGITAL * geo_weight)
    
    # Demographic Filtering Logic
    age_map = {"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}
    age_w = sum([age_map.get(a) for a in sel_age])
    nccs_w = len(sel_nccs) * 0.20
    final_u = int(market_size * age_w * nccs_w)

    # DYNAMIC MEDIA OPTIMIZER (UX FIX)
    if "45+" in sel_age and len(sel_age) == 1:
        mix = [0.60, 0.10, 0.20, 0.10] # Heavy YouTube/CTV for older
    elif "15-24" in sel_age:
        mix = [0.30, 0.55, 0.05, 0.10] # Heavy Meta for younger
    else:
        mix = [0.40, 0.35, 0.15, 0.10] # Standard balance

    # KPI GRID
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("National AIU", f"{TOTAL_INDIA_DIGITAL:,}", "India Base"),
        ("Market Potential", f"{market_size:,}", market_label),
        ("Qualified Target", f"{final_u:,}", "Target Audience"),
        ("Efficiency Score", f"{(final_u/max(1,market_size)*100):.1f}%", "Selection Ratio")
    ]
    for col, (lab, val, sub) in zip([c1, c2, c3, c4], metrics):
        col.markdown(f"""<div class="metric-card"><div class="label-text">{lab}</div><div class="value-text">{val}</div><div class="sub-text">⚡ {sub}</div></div>""", unsafe_allow_html=True)

    # HERO VISUAL: THE FUNNEL
    st.markdown("<br><div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<p class='label-text' style='text-align:center;'>Audience Sizing Funnel</p>", unsafe_allow_html=True)
    
    fig_f = go.Figure(go.Funnel(
        y=["National Universe", "Selected Market", "Qualified Audience"],
        x=[TOTAL_INDIA_DIGITAL, market_size, final_u],
        textinfo="value+percent initial",
        marker={"color": ["#1E293B", "#3B82F6", "#60A5FA"], "line": {"width": 2, "color": "white"}}
    ))
    fig_f.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), height=450, margin=dict(t=30, b=30))
    st.plotly_chart(fig_f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # MEDIA MIX TABLE
    st.markdown("<br><p class='label-text'>Recommended Media Deployment (Optimized for Selected Age)</p>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame({
        "Channel": ["YouTube Shorts", "Meta (FB/IG)", "Smart TV", "Search"],
        "Allocation": [f"{int(x*100)}%" for x in mix],
        "Reach ('000)": [f"{int(final_u*x):,}" for x in mix],
        "Objective": ["Awareness", "Engagement", "Impact", "Intent"]
    }), use_container_width=True, hide_index=True)

else:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h3 style='color:#334155;'>SYSTEM STANDBY</h3>
            <p style='color:#64748B;'>Select parameters and click EXECUTE to start the analysis.</p>
        </div>
    """, unsafe_allow_html=True)
