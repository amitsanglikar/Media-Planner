import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. APP CONFIG ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="⚡")

# --- 2. THE "EXECUTIVE TERMINAL" CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');

    /* Global Foundation: Midnight Navy */
    .stApp { background-color: #020617 !important; color: #F8FAFC; }
    
    /* Sidebar: Steel Blue */
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    
    /* The "SaaS Card" - Glow Effect */
    .saas-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(12px);
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    
    /* Typography: Precision Focus */
    .kpi-label { color: #94A3B8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .kpi-value { color: #3B82F6; font-size: 42px; font-weight: 800; font-family: 'Inter', sans-serif; line-height: 1; }
    .kpi-unit { color: #64748B; font-size: 14px; font-weight: 400; margin-top: 5px; }

    /* Interactive Table Overrides */
    .stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #1E293B; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
MASTER_DATA = {
    "Maharashtra": 0.125, "Delhi NCR": 0.095, "Karnataka": 0.084, 
    "Tamil Nadu": 0.092, "UP": 0.110, "West Bengal": 0.080, "Gujarat": 0.071
}

# --- 4. SIDEBAR (The Command Center) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Audience Terminal</h2>", unsafe_allow_html=True)
    sel_states = st.multiselect("Market Selection", list(MASTER_DATA.keys()), default=["Maharashtra"])
    m_type = st.segmented_control("Classification", ["Urban", "Rural", "Overall"], default="Overall")
    
    st.markdown("---")
    sel_age = st.multiselect("Age Groups", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    run = st.button("RUN ENGINE", use_container_width=True)

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='letter-spacing:-1px;'>Media Intelligence <span style='color:#3B82F6;'>Terminal</span></h1>", unsafe_allow_html=True)

if run:
    # Calculations
    BASE = 958000
    state_w = sum([MASTER_DATA[s] for s in sel_states])
    class_w = {"Urban": 0.43, "Rural": 0.57, "Overall": 1.0}[m_type]
    age_w = len(sel_age) * 0.25 # Simplified for demo
    nccs_w = len(sel_nccs) * 0.20
    
    final_u = int(BASE * state_w * class_w * age_w * nccs_w)

    # UI ROW 1: KPIs
    c1, c2, c3 = st.columns(3)
    
    for col, label, val, unit in zip([c1, c2, c3], 
                                     ["Unified Universe", "Market Share", "Reach Potential"],
                                     [f"{final_u:,}", f"{state_w:.1%}", f"{(final_u*0.82):,.0f}"],
                                     ["Monthly Active Users", "LSA Weighted", "Est. 1+ Monthly Reach"]):
        col.markdown(f"""
            <div class="saas-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val}</div>
                <div class="kpi-unit">{unit}</div>
            </div>
        """, unsafe_allow_html=True)

    # UI ROW 2: INTERACTIVE CHARTS
    v1, v2 = st.columns([1.5, 1])
    
    with v1:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-label'>Audience Funnel Analysis</div>", unsafe_allow_html=True)
        fig = go.Figure(go.Funnel(
            y=["India Digital", "LSA Base", "Targeted"],
            x=[BASE, BASE*state_w, final_u],
            marker={"color": ["#1E293B", "#3B82F6", "#60A5FA"]},
            textinfo="value+percent initial"
        ))
        fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), margin=dict(t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with v2:
        st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
        st.markdown("<div class='kpi-label'>Platform Propensity</div>", unsafe_allow_html=True)
        # Radar Chart for Professional Look
        fig_r = go.Figure(data=go.Scatterpolar(
            r=[90, 80, 40, 70, 30], theta=['Video','Social','Search','eComm','Audio'],
            fill='toself', line=dict(color='#3B82F6')
        ))
        fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)), 
                           paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), height=300, margin=dict(t=40, b=20))
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.image("https://img.freepik.com/free-vector/digital-marketing-concept-illustration_114360-1011.jpg", width=400)
    st.info("Awaiting command. Select parameters in the sidebar and click 'Run Engine'.")
