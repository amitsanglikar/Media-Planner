import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="📈")

# --- 2. ELITE-UI CSS (The "Glow" Architecture) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');
    
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    
    /* Neumorphic / Glassmorphic Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border: 1px solid #3B82F6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
    }
    
    /* Terminal Typography */
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .value-text { color: #F8FAFC; font-size: 2.5rem; font-weight: 800; margin-top: 8px; font-family: 'Inter', sans-serif; }
    .sub-text { color: #3B82F6; font-size: 0.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    /* Button Override */
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #3B82F6 100%) !important;
        border: none !important; border-radius: 8px !important; color: white !important;
        font-weight: 800 !important; height: 3.5rem !important; letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE DATA MASTER ---
METRO_DATA = {"Mumbai": 0.065, "Delhi": 0.072, "Bengaluru": 0.048, "Chennai": 0.038, "Kolkata": 0.035, "Hyderabad": 0.042, "Ahmedabad": 0.028, "Pune": 0.031}
INDIA_GEO_MASTER = {
    "North": {"Delhi NCR": ["New Delhi", "Gurgaon", "Noida"], "Punjab": ["Ludhiana", "Amritsar"], "UP": ["Lucknow", "Kanpur"]},
    "West": {"Maharashtra": ["Mumbai", "Pune", "Nagpur"], "Gujarat": ["Surat", "Ahmedabad"], "MP": ["Indore", "Bhopal"]},
    "South": {"Karnataka": ["Bengaluru", "Mysuru"], "Tamil Nadu": ["Chennai", "Coimbatore"], "Kerala": ["Kochi"]},
    "East/NE": {"West Bengal": ["Kolkata", "Howrah"], "Assam": ["Guwahati"], "Bihar": ["Patna"]}
}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Audience Terminal</h2>", unsafe_allow_html=True)
    sel_metros = st.multiselect("Elite Metros", list(METRO_DATA.keys()))
    st.markdown("---")
    sel_regions = st.multiselect("Regions", ["North", "West", "South", "East/NE"], disabled=bool(sel_metros))
    
    available_states = []
    if not sel_metros:
        for r in sel_regions: available_states.extend(list(INDIA_GEO_MASTER[r].keys()))
    sel_states = st.multiselect("State Filter", sorted(available_states), disabled=bool(sel_metros))
    
    m_type = st.segmented_control("Market Cut", ["Urban", "Rural", "Overall"], default="Urban")
    
    st.markdown("---")
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("NCCS Grade", ["A", "B", "C", "D", "E"], default=["A", "B"])
    budget = st.number_input("Budget (INR)", 500000, 100000000, step=500000)
    
    run_calc = st.button("EXECUTE PLANNING ENGINE")

# --- 5. MAIN TERMINAL ---
st.markdown("<h1 style='color:white; letter-spacing:-1px;'>Media Intelligence <span style='color:#3B82F6;'>Terminal</span></h1>", unsafe_allow_html=True)

if run_calc:
    # Calculations
    TOTAL_INDIA_DIGITAL = 958000
    base_w = sum([METRO_DATA[m] for m in sel_metros]) if sel_metros else (len(sel_states) * 0.042)
    age_w = sum([{"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}.get(a) for a in sel_age])
    class_mult = {"Urban": 0.43, "Rural": 0.57, "Overall": 1.0}[m_type] if not sel_metros else 1.0
    
    pop_size = int(TOTAL_INDIA_DIGITAL * base_w * class_mult * age_w * (len(sel_nccs)*0.2))
    targeted_reach = int(pop_size * 0.72)

    # 1. KPI GRID
    c1, c2, c3, c4 = st.columns(4)
    for col, lab, val, sub in zip([c1, c2, c3, c4], 
                                ["Unified Audience", "LSA Weight", "Net Reach", "CPM Index"],
                                [f"{pop_size:,}", f"{base_w:.2%}", f"{targeted_reach:,}", "₹142.00"],
                                ["Active '000s", "Market Share", "72% Efficiency", "Est. Industry Avg"]):
        col.markdown(f"""<div class="metric-card"><div class="label-text">{lab}</div><div class="value-text">{val}</div><div class="sub-text">⚡ {sub}</div></div>""", unsafe_allow_html=True)

    # 2. ANALYTICS ROW
    st.markdown("<br>", unsafe_allow_html=True)
    v1, v2 = st.columns([1.5, 1])
    
    with v1:
        st.markdown("<div class='metric-card'><p class='label-text'>Reach Diminishing Returns (Saturation Curve)</p>", unsafe_allow_html=True)
        # S-Curve Logic
        x_budget = np.linspace(0, budget * 2.5, 100)
        y_reach = pop_size * (1 - np.exp(-0.0000005 * x_budget))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_budget, y=y_reach, mode='lines', line=dict(color='#3B82F6', width=4), name='Reach Curve'))
        fig.add_hline(y=targeted_reach, line_dash="dash", line_color="#94A3B8", annotation_text="Target Milestone")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(t=20, b=20, l=10, r=10), xaxis_title="Budget (INR)", yaxis_title="Reach ('000)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with v2:
        st.markdown("<div class='metric-card'><p class='label-text'>Platform Affinity Matrix</p>", unsafe_allow_html=True)
        # Radar Chart for Professional Media Mix
        categories = ['YT Search', 'Meta Feed', 'Insta Reels', 'Smart TV', 'Programmatic']
        fig_r = go.Figure(data=go.Scatterpolar(r=[80, 70, 95, 40, 60], theta=categories, fill='toself', line=dict(color='#3B82F6'), fillcolor='rgba(59, 130, 246, 0.3)'))
        fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), height=350, margin=dict(t=50, b=30, l=0, r=0))
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. INTERACTIVE MEDIA ALLOCATION TABLE
    st.markdown("<br><p class='label-text'>Optimized Channel Allocation & Strategic Justification</p>", unsafe_allow_html=True)
    
    # Calculate Splits dynamically based on budget
    channels = ["YouTube Shorts", "Instagram Reels", "Smart TV (CTV)", "Google Search"]
    splits = [35, 45, 10, 10]
    
    # 
    
    plan_data = pd.DataFrame({
        "Channel": channels,
        "Spend Allocation": [f"₹{(budget * s / 100):,.0f}" for s in splits],
        "Est. Impressions": [f"{(pop_size * s / 10):,.0f}" for s in splits],
        "Frequency Goal": ["4.2x", "5.8x", "2.1x", "1.5x"],
        "Strategic Justification": ["Mass awareness via lean-forward video", "High-frequency engagement for Gen-Z/Millennials", "Premium high-impact branding", "Capturing high-intent search volume"]
    })
    
    st.dataframe(plan_data, use_container_width=True, hide_index=True)

else:
    st.markdown("""
        <div style='text-align:center; padding-top:100px;'>
            <h2 style='color:#334155;'>Awaiting Command</h2>
            <p style='color:#64748B;'>Select audience parameters in the left terminal to generate intelligence.</p>
        </div>
    """, unsafe_allow_html=True)
