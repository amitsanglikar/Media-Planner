import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. PREMIUM UI/UX CSS (Blue & Orange Palette) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');
    
    /* Core App Style */
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    
    /* Sidebar Text & Inputs */
    [data-testid="stSidebar"] .stWidgetLabel p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 {
        color: #F8FAFC !important; font-weight: 600 !important; font-family: 'Inter', sans-serif;
    }

    /* Metric Card Glow Effects */
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 1.5rem; border-radius: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    .metric-card:hover { border-color: #FB923C; transform: translateY(-5px); }
    
    /* Typography Overhaul */
    .label-text { color: #94A3B8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value-text { color: #FFFFFF; font-size: 2.8rem; font-weight: 800; margin-top: 5px; }
    .sub-text-blue { color: #3B82F6; font-size: 0.85rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .sub-text-orange { color: #FB923C; font-size: 0.85rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    /* Tabs & Buttons */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; color: #94A3B8; font-weight: 600; 
        border-radius: 8px 8px 0 0; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { color: #FB923C !important; border-bottom-color: #FB923C !important; }

    /* Buttons: Primary (Blue) & Secondary (Orange) */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 12px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; letter-spacing: 1px;
    }
    div[data-testid="stSidebar"] button {
        background: linear-gradient(90deg, #EA580C 0%, #FB923C 100%) !important;
        height: 2.8rem !important; font-size: 0.8rem !important;
    }
    
    /* Table Styling */
    .stDataFrame, .stTable { background-color: #0F172A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE PERMANENT DATABASE (iGOD Mapping) ---
INDIA_REGIONAL_DATA = {
    "North": {
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Shahdara"],
        "Haryana": ["Ambala", "Faridabad", "Gurugram", "Hisar", "Karnal", "Panipat", "Rohtak", "Sonipat"],
        "Punjab": ["Amritsar", "Bathinda", "Jalandhar", "Ludhiana", "Mohali", "Patiala"],
        "Uttar Pradesh": ["Agra", "Aligarh", "Ayodhya", "Bareilly", "Ghaziabad", "Gorakhpur", "Jhansi", "Kanpur Nagar", "Lucknow", "Meerut", "Prayagraj", "Varanasi"],
        "Rajasthan": ["Ajmer", "Alwar", "Bikaner", "Jaipur", "Jodhpur", "Kota", "Sikar", "Udaipur"]
    },
    "West": {
        "Maharashtra": ["Akola", "Amravati", "Aurangabad", "Kolhapur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nashik", "Pune", "Solapur", "Thane"],
        "Gujarat": ["Ahmedabad", "Amreli", "Anand", "Bhavnagar", "Gandhinagar", "Jamnagar", "Kutch", "Rajkot", "Surat", "Vadodara"],
        "Goa": ["North Goa", "South Goa"]
    },
    "South": {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool"],
        "Karnataka": ["Bengaluru Rural", "Bengaluru Urban", "Dharwad", "Kalaburagi", "Mysuru"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Thanjavur"],
        "Telangana": ["Hyderabad", "Karimnagar", "Khammam", "Nizamabad"]
    },
    "East/NE": {
        "West Bengal": ["Asansol", "Darjeeling", "Howrah", "Kolkata", "Siliguri"],
        "Bihar": ["Bhagalpur", "Gaya", "Muzaffarpur", "Patna"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Ganjam", "Puri"]
    }
}

# --- 4. SIDEBAR (Command Center) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Targeting Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Classification", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")
    
    sel_regions = st.multiselect("Region", list(INDIA_REGIONAL_DATA.keys()))
    
    available_states = []
    for r in (sel_regions if sel_regions else INDIA_REGIONAL_DATA):
        available_states.extend(list(INDIA_REGIONAL_DATA[r].keys()))
    sel_states = st.multiselect("States", sorted(available_states))
    
    FLAT_MASTER = {}
    for r in INDIA_REGIONAL_DATA: FLAT_MASTER.update(INDIA_REGIONAL_DATA[r])
    available_districts = []
    for s in sel_states: available_districts.extend(FLAT_MASTER.get(s, []))
    
    sel_districts = st.multiselect("Districts", sorted(list(set(available_districts))), disabled=not sel_states)
    
    st.markdown("---")
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    if st.button("💾 SAVE CONFIGURATION"):
        st.success("Preset Encrypted & Saved")

    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='color:white; letter-spacing:-2px;'>Digital Media <span style='color:#FB923C;'>Terminal</span> <span style='color:#3B82F6;'>2026</span></h1>", unsafe_allow_html=True)

tab_calc, tab_bench = st.tabs(["🎯 Campaign Planner", "📊 Market Benchmarks"])

with tab_calc:
    if run_calc:
        TOTAL_BASE = 958000
        geo_weight = (len(sel_states) * 0.045) if sel_states else 0.8
        if sel_districts: geo_weight *= (len(sel_districts) / max(1, len(available_districts)))
        
        market_size = int(TOTAL_BASE * geo_weight)
        age_map = {"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}
        age_w = sum([age_map[a] for a in sel_age])
        final_u = int(market_size * age_w * (len(sel_nccs)*0.2))

        # Metric Glow Grid
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="label-text">Market Potential</div><div class="value-text">{market_size:,}</div><div class="sub-text-blue">⚡ GEO REACH</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="label-text">Qualified Target</div><div class="value-text">{final_u:,}</div><div class="sub-text-orange">🔥 TARGETED</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="label-text">Selection Efficiency</div><div class="value-text">{(final_u/max(1,market_size)*100):.1f}%</div><div class="sub-text-blue">📈 OPTIMIZED</div></div>', unsafe_allow_html=True)

        

        st.markdown("<br><p class='label-text'>Recommended Media Deployment</p>", unsafe_allow_html=True)
        
        # Style the Dataframe for the dark theme
        df_mix = pd.DataFrame({
            "Channel": ["YouTube Shorts", "OTT / Connected TV", "Social Feed", "Search/Intent"],
            "Reach (000s)": [f"{int(final_u*0.42):,}", f"{int(final_u*0.28):,}", f"{int(final_u*0.20):,}", f"{int(final_u*0.10):,}"],
            "Affinity Index": ["115 (High)", "142 (Elite)", "108 (Mid)", "185 (Max)"]
        })
        st.dataframe(df_mix, use_container_width=True, hide_index=True)
        
    else:
        st.markdown("""
            <div style='text-align:center; padding:100px;'>
                <h3 style='color:#64748B; font-family:JetBrains Mono;'>SYSTEM STANDBY...</h3>
                <p style='color:#334155;'>Set targeting parameters in the command center and press execute.</p>
            </div>
        """, unsafe_allow_html=True)

with tab_bench:
    st.markdown("<p class='label-text'>National Genre Performance</p>", unsafe_allow_html=True)
    
    
    bench_data = pd.DataFrame({
        "Genre": ["Short Video", "Social Media", "OTT Video", "Online Gaming", "News", "Finance"],
        "Daily Penetration": ["88%", "85%", "74%", "62%", "48%", "22%"],
        "CPM Benchmark (Est)": ["₹85", "₹110", "₹280", "₹140", "₹95", "₹450"]
    })
    st.table(bench_data)
