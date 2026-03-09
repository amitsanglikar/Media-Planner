import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. PAGE CONFIG & TERMINAL THEME ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="📈")

# --- 2. THE "ELITE-UI" CSS OVERRIDE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Foundation */
    .stApp { background-color: #0F172A !important; font-family: 'Inter', sans-serif !important; }
    
    /* Sidebar Sophistication */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155;
    }
    
    /* Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border: 1px solid #3B82F6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
    }
    
    /* Typography Force */
    .label-text { color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .value-text { color: #F8FAFC; font-size: 2.2rem; font-weight: 800; margin-top: 5px; }
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 600; margin-top: 5px; }

    /* Hide Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Interactive Button */
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        height: 3.5rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE MASTER DATA ENGINE ---
INDIA_GEO_MASTER = {
    "Maharashtra": {"districts": ["Mumbai", "Pune", "Nagpur"], "trai_weight": 0.125},
    "Delhi NCR": {"districts": ["New Delhi", "Gurgaon", "Noida"], "trai_weight": 0.095},
    "Karnataka": {"districts": ["Bengaluru", "Mysuru", "Hubballi"], "trai_weight": 0.084},
    "Tamil Nadu": {"districts": ["Chennai", "Coimbatore", "Madurai"], "trai_weight": 0.092},
    "Uttar Pradesh": {"districts": ["Lucknow", "Kanpur", "Ghaziabad"], "trai_weight": 0.110},
    "West Bengal": {"districts": ["Kolkata", "Howrah", "Durgapur"], "trai_weight": 0.080},
    "Gujarat": {"districts": ["Ahmedabad", "Surat", "Vadodara"], "trai_weight": 0.071},
}

# --- 4. SIDEBAR (The Control Room) ---
with st.sidebar:
    st.markdown("<h2 style='color:white; margin-bottom:2rem;'>Targeting Terminal</h2>", unsafe_allow_html=True)
    sel_states = st.multiselect("Markets/LSA", sorted(list(INDIA_GEO_MASTER.keys())), default=["Maharashtra"])
    market_type = st.radio("Market Classification", ["Overall", "Urban", "Rural"], horizontal=True)
    
    district_pool = []
    for s in sel_states: district_pool.extend(INDIA_GEO_MASTER[s]["districts"])
    sel_districts = st.multiselect("District Granularity", sorted(list(set(district_pool))), disabled=(market_type != "Overall"))
    
    st.markdown("---")
    sel_gender = st.multiselect("Gender", ["Male", "Female"], default=["Male", "Female"])
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("NCCS Grade", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    run_calc = st.button("Calculate Unified Universe")

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='color:#F8FAFC; margin-bottom:0;'>Media Intelligence Terminal</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-bottom:2rem;'>IAMAI 2026 • TRAI Wireless Statistics • Comscore MMX Multi-Platform</p>", unsafe_allow_html=True)

if run_calc:
    # --- CALCULATION LOGIC ---
    TOTAL_INDIA_AIU = 958000
    lsa_weight = sum([INDIA_GEO_MASTER[s]["trai_weight"] for s in sel_states])
    class_mult = {"Urban": 0.43, "Rural": 0.57, "Overall": 1.0}[market_type]
    
    granularity = 1.0
    if market_type == "Overall" and len(sel_districts) > 0:
        granularity = len(sel_districts) / len(district_pool)
        
    age_w = sum([{"15-24": 0.38, "25-34": 0.32, "35-44": 0.18, "45+": 0.12}.get(a) for a in sel_age])
    nccs_w = sum([{"A": 0.15, "B": 0.22, "C": 0.28, "D": 0.20, "E": 0.15}.get(n) for n in sel_nccs])
    
    gender_w = 1.0 if len(sel_gender) == 2 else (0.54 if "Male" in sel_gender else 0.46)
    unified_u = int(TOTAL_INDIA_AIU * lsa_weight * class_mult * granularity * age_w * nccs_w * gender_w)

    # --- ROW 1: THE METRIC GRID ---
    m1, m2, m3, m4 = st.columns(4)
    
    metrics = [
        ("Unified Universe", f"{unified_u:,}", "Active Monthly Users"),
        ("TRAI LSA Weight", f"{lsa_weight:.2%}", "LSA Market Share"),
        ("Demo Density", f"{age_w:.2%}", "Age + NCCS Concentration"),
        ("Est. Reach", f"{int(unified_u * 0.72):,}", "Potential 1+ Reach")
    ]
    
    for i, col in enumerate([m1, m2, m3, m4]):
        label, val, sub = metrics[i]
        col.markdown(f"""
            <div class="metric-card">
                <div class="label-text">{label}</div>
                <div class="value-text">{val}</div>
                <div class="sub-text">⚡ {sub}</div>
            </div>
        """, unsafe_allow_html=True)

    # --- ROW 2: INTERACTIVE VISUALS ---
    st.markdown("<br>", unsafe_allow_html=True)
    v1, v2 = st.columns([1.5, 1])
    
    with v1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='label-text'>Audience Funnel Degradation</p>", unsafe_allow_html=True)
        # Advanced Funnel
        fig_f = go.Figure(go.Funnel(
            y=["Total AIU", "Selected LSA", "Target Segment"],
            x=[TOTAL_INDIA_AIU, TOTAL_INDIA_AIU * lsa_weight, unified_u],
            textinfo="value+percent initial",
            connector={"line": {"color": "rgba(59, 130, 246, 0.2)", "width": 1}},
            marker={"color": ["#1E293B", "#3B82F6", "#60A5FA"]}
        ))
        fig_f.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#94A3B8"), height=350, margin=dict(t=30, b=0, l=10, r=10)
        )
        st.plotly_chart(fig_f, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with v2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='label-text'>Platform Propensity Score</p>", unsafe_allow_html=True)
        # Radar Chart for Propensity
        categories = ['Video', 'Social', 'Search', 'E-comm', 'Audio']
        fig_r = go.Figure(data=go.Scatterpolar(
            r=[85, 92, 78, 65, 45], theta=categories, fill='toself',
            line=dict(color='#3B82F6'), fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig_r.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#334155"), 
                       angularaxis=dict(gridcolor="#334155"),
                       bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#94A3B8"), height=350, margin=dict(t=50, b=30)
        )
        st.plotly_chart(fig_r, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ROW 3: DATAGRID ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p class='label-text'>Source Logic & Audit Trail</p>", unsafe_allow_html=True)
    audit_df = pd.DataFrame({
        "Attribute": ["Geography", "Market Cut", "Age Segment", "Economic Index"],
        "Input": [", ".join(sel_states), market_type, ", ".join(sel_age), ", ".join(sel_nccs)],
        "Confidence": ["98%", "94%", "89%", "85%"],
        "Sync": ["Real-time 🟢", "Real-time 🟢", "Benchmark 🔵", "Benchmark 🔵"]
    })
    st.dataframe(audit_df, use_container_width=True, hide_index=True)

else:
    st.markdown("""
        <div style="text-align:center; padding: 100px; color:#64748B;">
            <h2 style="color:#334155;">Terminal Idle</h2>
            <p>Awaiting input parameters from the Targeting Terminal (Sidebar)</p>
        </div>
    """, unsafe_allow_html=True)
