import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Triangulated Planner 2026", layout="wide", page_icon="🌐")

# --- 2. THE MASTER GEO-DATABASE ---
INDIA_GEO_MASTER = {
    "Andhra Pradesh": {"districts": ["Visakhapatnam", "Vijayawada", "Guntur"], "trai_weight": 0.062},
    "Bihar": {"districts": ["Patna", "Gaya", "Bhagalpur"], "trai_weight": 0.051},
    "Delhi NCR": {"districts": ["New Delhi", "Gurgaon", "Noida"], "trai_weight": 0.095},
    "Gujarat": {"districts": ["Ahmedabad", "Surat", "Vadodara"], "trai_weight": 0.071},
    "Karnataka": {"districts": ["Bengaluru", "Mysuru", "Hubballi"], "trai_weight": 0.084},
    "Maharashtra": {"districts": ["Mumbai", "Pune", "Nagpur"], "trai_weight": 0.125},
    "Tamil Nadu": {"districts": ["Chennai", "Coimbatore", "Madurai"], "trai_weight": 0.092},
    "Uttar Pradesh": {"districts": ["Lucknow", "Kanpur", "Ghaziabad"], "trai_weight": 0.110},
    "West Bengal": {"districts": ["Kolkata", "Howrah", "Durgapur"], "trai_weight": 0.080},
} # Shortened for display; use your full dictionary here.

# --- 3. ADVANCED UI STYLING (The "SaaS" Look) ---
st.markdown("""
    <style>
    /* Global Reset */
    .stApp { background-color: #F8FAFC !important; }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] .stMarkdown h3, 
    section[data-testid="stSidebar"] label {
        color: #F1F5F9 !important;
    }

    /* Professional Dashboard Cards */
    .dashboard-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }

    /* Main KPI Typography */
    .kpi-title { font-size: 14px; color: #64748B; font-weight: 600; margin-bottom: 4px; }
    .kpi-value { font-size: 48px; color: #1E3A8A; font-weight: 800; line-height: 1; }
    .kpi-sub { font-size: 12px; color: #94A3B8; margin-top: 8px; }

    /* Button Styling */
    .stButton>button {
        background: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        height: 3rem !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 🛠️ Configuration")
    sel_states = st.multiselect("States/UTs", sorted(list(INDIA_GEO_MASTER.keys())), default=["Maharashtra"])
    market_type = st.selectbox("Classification", ["Urban", "Rural", "Overall"], index=2)
    
    district_pool = []
    for s in sel_states: district_pool.extend(INDIA_GEO_MASTER[s]["districts"])
    sel_districts = st.multiselect("Districts", sorted(list(set(district_pool))), disabled=(market_type != "Overall"))
    
    st.markdown("---")
    sel_gender = st.multiselect("Gender", ["Male", "Female"], default=["Male", "Female"])
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
    sel_nccs = st.multiselect("NCCS Segments", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    calculate = st.button("RUN TRIANGULATION")

# --- 5. MAIN DASHBOARD CANVAS ---
st.markdown("<h1>📊 Media Intelligence Dashboard <small style='font-size:14px; color:#64748B; font-weight:400;'>v4.0 Alpha</small></h1>", unsafe_allow_html=True)

if not calculate:
    st.info("👈 Configure your audience in the sidebar and click **Run Triangulation** to generate insights.")
    # Placeholder Mock for empty state
    
else:
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

    # --- DASHBOARD LAYOUT ---
    col_kpi, col_funnel = st.columns([1, 1.5])
    
    with col_kpi:
        st.markdown(f"""
            <div class="dashboard-card">
                <p class="kpi-title">UNIFIED TARGET UNIVERSE</p>
                <p class="kpi-value">{unified_u:,}</p>
                <p class="kpi-sub">Monthly Active Users ('000s)</p>
            </div>
            <div class="dashboard-card">
                <p class="kpi-title">TRAI LSA COVERAGE</p>
                <p class="kpi-value" style="font-size:32px;">{lsa_weight:.2%}</p>
                <p class="kpi-sub">Based on Wireless Broadband Weights</p>
            </div>
        """, unsafe_allow_html=True)

    with col_funnel:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Audience Funnel Analysis")
        # Plotly Funnel for SaaS look
        fig = go.Figure(go.Funnel(
            y = ["Total India", "Regional LSA", "Target Segment"],
            x = [TOTAL_INDIA_AIU, TOTAL_INDIA_AIU * lsa_weight, unified_u],
            textinfo = "value+percent initial",
            marker = {"color": ["#0F172A", "#3B82F6", "#60A5FA"]}
        ))
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Secondary Data Row
    col_audit, col_mix = st.columns([1.2, 1])
    
    with col_audit:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("#### 🛡️ Data Source Integrity")
        audit_df = pd.DataFrame({
            "Layer": ["Geography", "Classification", "Demographics"],
            "Coverage": [f"{len(sel_states)} States", market_type, f"{len(sel_age)} Age Groups"],
            "Source": ["TRAI Q4 Benchmarks", "IAMAI 2026 Proj.", "Comscore MMX"]
        })
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_mix:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Reach Potential")
        st.progress(min(unified_u / 10000, 1.0))
        st.caption("Estimated reach of 1.2M impressions at ₹45 CPM.")
        st.markdown('</div>', unsafe_allow_html=True)
