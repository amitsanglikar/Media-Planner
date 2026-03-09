import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. DATA & BENCHMARKS (Estimated for India 2026) ---
MARKET_INTEL = {
    "A1": {"cat_ecpm": 420, "cat_sov_pool_imps": 80000000, "base_cprc": 4500},
    "A2": {"cat_ecpm": 310, "cat_sov_pool_imps": 150000000, "base_cprc": 3200},
    "B1": {"cat_ecpm": 190, "cat_sov_pool_imps": 250000000, "base_cprc": 1800}
}

st.set_page_config(page_title="Virtual Media Planner", layout="wide")

# --- CUSTOM HEADER ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Market Intelligence & Digital Operating Levels</p>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR: ONLY CAMPAIGN INPUTS ---
with st.sidebar:
    st.header("Campaign Controls")
    tg = st.selectbox("Target Group", ["Male 18-34", "Female 25-44", "All 15+"])
    market = st.selectbox("Market", ["Maharashtra", "Tamil Nadu", "Karnataka", "Delhi NCR"])
    nccs = st.selectbox("NCCS", ["A1", "A2", "B1"])
    total_budget = st.number_input("Campaign Budget (INR)", value=1500000, step=50000)
    reach_target = st.slider("Target Reach (1+) %", 10, 95, 60)
    woa = st.number_input("Weeks on Air", 1, 12, 4)
    
    submit = st.button("Generate Strategy", type="primary")

# --- MAIN EXECUTION ---
if submit:
    # A. Calculations
    intel = MARKET_INTEL.get(nccs)
    
    # Brand Metrics
    brand_ecpm = intel['cat_ecpm'] * 0.95 # Assuming 5% optimization for the brand
    brand_imps = (total_budget / brand_ecpm) * 1000
    brand_sov = (brand_imps / (brand_imps + intel['cat_sov_pool_imps'])) * 100
    cprc = total_budget / reach_target

    # B. COMPETITIVE INTELLIGENCE SECTION
    st.subheader("📊 Market Intelligence & Share of Voice")
    
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        # Comparison Table
        intel_df = pd.DataFrame({
            "Metric": ["eCPM (Effective)", "SOV (Share of Voice)", "Estimated Impressions"],
            "Your Brand": [f"₹{round(brand_ecpm, 2)}", f"{round(brand_sov, 2)}%", f"{round(brand_imps/1000000, 2)}M"],
            "Category Average": [f"₹{intel['cat_ecpm']}", "100% (Market Pool)", f"{round(intel['cat_sov_pool_imps']/1000000, 2)}M"]
        })
        st.table(intel_df)
    
    with m_col2:
        # SOV Gauge/Donut
        fig_sov = px.pie(
            values=[brand_imps, intel['cat_sov_pool_imps']], 
            names=['Your Brand SOV', 'Remaining Category'],
            hole=0.6,
            color_discrete_sequence=['#1E3A8A', '#E5E7EB'],
            title="Estimated Market SOV"
        )
        st.plotly_chart(fig_sov, use_container_width=True)

    # C. REACH CURVE & OPERATING LEVELS
    st.divider()
    st.subheader("📈 Operating Levels & Reach Curve")
    
    o_col1, o_col2 = st.columns([1, 2])
    
    with o_col1:
        st.metric("Cost Per Reach Point (CPRC)", f"₹{int(cprc):,}")
        st.metric("Weekly GRP Requirement", round((reach_target * 3)/woa, 1)) # Based on 3+ freq proxy
        st.info(f"Recommended Genres for {nccs}: \n\n **News, Infotainment, OTT Originals**")

    with o_col2:
        freqs = [f"{i}+" for i in range(1, 11)]
        # Logistic Reach build logic
        reach_vals = [reach_target * (0.84**(i-1)) for i in range(1, 11)]
        st.line_chart(pd.DataFrame({"Reach %": reach_vals}, index=freqs))

    # D. EXCEL EXPORT
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        intel_df.to_excel(writer, sheet_name='Market_Intelligence', index=False)
        pd.DataFrame({"Frequency": freqs, "Reach": reach_vals}).to_excel(writer, sheet_name='Reach_Curve', index=False)
    
    st.download_button("📥 Download Media Plan", buffer.getvalue(), f"VMP_Plan_{market}.xlsx")
