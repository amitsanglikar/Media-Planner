import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="📈")

# --- 2. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; border-right: 1px solid #334155; }
    .metric-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
    }
    .label-text { color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .value-text { color: #F8FAFC; font-size: 2.2rem; font-weight: 800; margin-top: 5px; }
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 600; margin-top: 5px; }
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important; border-radius: 6px !important; font-weight: 800 !important; height: 3.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE ABSOLUTE MASTER DATABASE (ALL 36 ENTITIES) ---
METRO_DATA = {
    "Mumbai": 0.065, "Delhi": 0.072, "Bengaluru": 0.048, "Chennai": 0.038, 
    "Kolkata": 0.035, "Hyderabad": 0.042, "Ahmedabad": 0.028, "Pune": 0.031
}

INDIA_GEO_MASTER = {
    "North": {
        "Delhi NCR": ["New Delhi", "Gurgaon", "Noida", "Ghaziabad", "Faridabad"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Mohali"],
        "Haryana": ["Ambala", "Karnal", "Panipat", "Hisar", "Rohtak"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Udaipur", "Bikaner"],
        "Himachal Pradesh": ["Shimla", "Dharamshala", "Solan", "Mandi"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Haldwani", "Roorkee"],
        "Chandigarh": ["Chandigarh City"], "Ladakh": ["Leh", "Kargil"]
    },
    "West": {
        "Maharashtra": ["Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati"],
        "Gujarat": ["Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain"],
        "Goa": ["Panaji", "Margao", "Vasco da Gama"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba"],
        "Dadra & Nagar Haveli / Daman & Diu": ["Silvassa", "Daman", "Diu"]
    },
    "South": {
        "Karnataka": ["Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi"],
        "Tamil Nadu": ["Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tiruppur"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool"],
        "Telangana": ["Warangal", "Nizamabad", "Khammam", "Karimnagar"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam"],
        "Puducherry": ["Puducherry City", "Karaikal"], "Lakshadweep": ["Kavaratti"]
    },
    "East/NE": {
        "West Bengal": ["Howrah", "Durgapur", "Siliguri", "Asansol", "Kharagpur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
        "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon"],
        "Sikkim": ["Gangtok"], "Arunachal Pradesh": ["Itanagar"], "Manipur": ["Imphal"],
        "Meghalaya": ["Shillong"], "Mizoram": ["Aizawl"], "Nagaland": ["Kohima"],
        "Tripura": ["Agartala"], "Andaman & Nicobar": ["Port Blair"]
    }
}

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Targeting Terminal</h2>", unsafe_allow_html=True)
    
    sel_metros = st.multiselect("Top 8 Metros", list(METRO_DATA.keys()))
    is_metro = len(sel_metros) > 0
    
    st.markdown("---")
    
    sel_regions = st.multiselect("Region Filter", ["North", "West", "South", "East/NE"], disabled=is_metro)
    
    available_states = []
    if not is_metro:
        for r in sel_regions:
            available_states.extend(list(INDIA_GEO_MASTER[r].keys()))
    sel_states = st.multiselect("States", sorted(available_states), disabled=is_metro)
    
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True, disabled=is_metro)
    
    available_districts = []
    if not is_metro:
        for r in sel_regions:
            for s in sel_states:
                if s in INDIA_GEO_MASTER[r]:
                    available_districts.extend(INDIA_GEO_MASTER[r][s])
    sel_districts = st.multiselect("Districts", sorted(list(set(available_districts))), disabled=(is_metro or m_type != "Overall"))
    
    st.markdown("---")
    sel_age = st.multiselect("Age Groups", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("Income (NCCS)", ["A", "B", "C", "D", "E"], default=["A", "B"])
    total_budget = st.number_input("Ad Spend (INR)", value=1000000)
    run_calc = st.button("Calculate Plan")

# --- 5. DASHBOARD ---
st.markdown("<h1 style='color:#F8FAFC;'>Media Intelligence Terminal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B;'>Source: IAMAI • TRAI • Comscore (2026) | <b>Figures in '000</b></p>", unsafe_allow_html=True)

if run_calc:
    TOTAL_INDIA_DIGITAL = 958000
    
    # Weight Calculation
    if is_metro:
        base_w = sum([METRO_DATA[m] for m in sel_metros])
        classification = "Metro Targeted"
    else:
        base_w = len(sel_states) * 0.045 if not sel_districts else (len(sel_districts)/len(available_districts)) * (len(sel_states) * 0.045)
        classification = m_type

    # Dynamic Age-Based Media Split Optimizer
    if "45+" in sel_age and len(sel_age) == 1:
        yt_s, meta_s, ctv_s = 60, 15, 25
    elif "15-24" in sel_age:
        yt_s, meta_s, ctv_s = 40, 50, 10
    else:
        yt_s, meta_s, ctv_s = 50, 30, 20

    age_w = sum([{"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}.get(a) for a in sel_age])
    nccs_w = sum([{"A": 0.15, "B": 0.22, "C": 0.28, "D": 0.20, "E": 0.15}.get(n) for n in sel_nccs])
    class_mult = 1.0 if is_metro else {"Urban": 0.43, "Rural": 0.57, "Overall": 1.0}[m_type]
    
    pop_size = int(TOTAL_INDIA_DIGITAL * base_w * class_mult * age_w * nccs_w)
    targeted_reach = int(pop_size * 0.72)

    # KPI GRID
    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        ("Digital Population", f"{pop_size:,}", "People in '000"),
        ("Market Focus", f"{base_w:.1%}", classification),
        ("Likely Reach", f"{targeted_reach:,}", "Reach in '000"),
        ("Ad Frequency", "3.2x", "Optimal Impact")
    ]
    for i, col in enumerate([m1, m2, m3, m4]):
        label, val, sub = metrics[i]
        col.markdown(f'<div class="metric-card"><div class="label-text">{label}</div><div class="value-text">{val}</div><div class="sub-text">⚡ {sub}</div></div>', unsafe_allow_html=True)

    # VISUALS
    v1, v2 = st.columns([1.5, 1])
    with v1:
        st.markdown("<div class='metric-card'><p class='label-text'>Reach Potential (in '000) vs. Budget</p>", unsafe_allow_html=True)
        budgets = np.linspace(0, total_budget * 2, 20)
        reaches = (1 - np.exp(-0.00004 * budgets)) * pop_size
        fig = go.Figure(go.Scatter(x=budgets, y=reaches, mode='lines', line=dict(color='#3B82F6', width=4)))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with v2:
        st.markdown("<div class='metric-card'><p class='label-text'>Optimized Spend Split</p>", unsafe_allow_html=True)
        fig_pie = px.pie(values=[yt_s, meta_s, ctv_s], names=['YouTube', 'Meta', 'Smart TV'], hole=.6, color_discrete_sequence=['#3B82F6', '#1E40AF', '#60A5FA'])
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    

    # CHANNEL TABLE
    st.table(pd.DataFrame({
        "Channel": ["YouTube", "Meta (FB/IG)", "Smart TV"],
        "Budget Split": [f"{yt_s}%", f"{meta_s}%", f"{ctv_s}%"],
        "Reach ('000)": [f"{int(targeted_reach*(yt_s/100)):,}", f"{int(targeted_reach*(meta_s/100)):,}", f"{int(targeted_reach*(ctv_s/100)):,}"],
        "Reasoning": ["Video Consumption", "Social Connectivity", "High Impact Living Room"]
    }))
else:
    st.info("👈 Use the Targeting Terminal. Selecting a Metro City will lock Region/State/District filters.")
