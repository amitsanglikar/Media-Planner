import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. DIGITAL BENCHMARKS (India 2026) ---
DIGITAL_BENCHMARKS = {
    "A1": {"avg_cpm": 350, "bench_ctr": 1.2, "bench_vtr": 45},
    "A2": {"avg_cpm": 280, "bench_ctr": 1.0, "bench_vtr": 35},
    "B1": {"avg_cpm": 180, "bench_ctr": 0.8, "bench_vtr": 25}
}

st.set_page_config(page_title="Virtual Media Planner", layout="wide")
st.markdown("<h1 style='text-align: center;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)

# --- 2. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Campaign & Market Data")
    nccs = st.selectbox("NCCS Tier", ["A1", "A2", "B1"])
    market = st.selectbox("Market", ["Maharashtra", "Tamil Nadu", "Karnataka", "Delhi NCR"])
    total_budget = st.number_input("Your Digital Budget (INR)", value=1000000, min_value=100000)
    
    st.divider()
    st.header("Competitive & SOV")
    cat_monthly_imps = st.number_input("Estimated Category Monthly Impressions", value=50000000)
    avg_cat_cpm = st.number_input("Avg. Category CPM (INR)", value=220)
    
    st.divider()
    reach_goal = st.slider("Target Reach %", 10, 95, 60)
    
    submit = st.button("Generate Digital Plan", type="primary")

# --- 3. EXECUTION LOGIC ---
if submit:
    # A. Efficiency Calculations
    bench = DIGITAL_BENCHMARKS.get(nccs)
    est_impressions = (total_budget / bench['avg_cpm']) * 1000
    cprc = total_budget / reach_goal  # Cost Per Reach Point
    sov = (est_impressions / cat_monthly_imps) * 100
    
    # B. KPI & SOV Dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Est. Impressions", f"{round(est_impressions/1000000, 2)}M")
    col2.metric("CPRC (Cost Per Reach Point)", f"₹{int(cprc):,}")
    col3.metric("Digital SOV", f"{round(sov, 2)}%")

    # C. Benchmarking Chart
    st.divider()
    st.subheader("📊 Performance Benchmarks vs. Market")
    
    bench_data = pd.DataFrame({
        "Metric": ["Avg. CPM (INR)", "Expected CTR (%)", "Expected VTR (%)"],
        "Market Benchmark": [bench['avg_cpm'], bench['bench_ctr'], bench['bench_vtr']],
        "Your Plan Proxy": [round(total_budget/(est_impressions/1000), 2), bench['bench_ctr'], bench['bench_vtr']]
    })
    st.table(bench_data)

    # D. Reach Curve & Operating Levels
    st.subheader("📈 Reach Distribution Curve (1+ to 10+)")
    freqs = [f"{i}+" for i in range(1, 11)]
    # Beta-Binomial approximation for Digital Reach
    reach_vals = [reach_goal * (0.82**(i-1)) for i in range(1, 11)]
    fig_curve = px.area(x=freqs, y=reach_vals, labels={'x': 'Frequency', 'y': 'Reach %'},
                        title="Incremental Reach Decay")
    st.plotly_chart(fig_curve, use_container_width=True)

    # E. Genre Mix & Budget Bifurcation
    st.divider()
    st.subheader("🎯 Genre Strategy & Funnel Split")
    
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        genres = {"A1": "Business, Luxury, Tech, Global News", 
                  "A2": "Infotainment, Sports, Lifestyle", 
                  "B1": "Regional GEC, Music, Comedy"}
        st.write(f"**Recommended Genre Clusters for {nccs}:**")
        st.success(genres.get(nccs))
    
    with g_col2:
        fig_pie = px.pie(values=[total_budget*0.5, total_budget*0.3, total_budget*0.2], 
                         names=['Awareness (Video)', 'Consideration (Social)', 'Conversion (Search/WA)'],
                         hole=0.4, title="Budget Bifurcation")
        st.plotly_chart(fig_pie)

    # F. Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_summary = pd.DataFrame({"Metric": ["Budget", "Reach %", "CPRC", "SOV %"], 
                                   "Value": [total_budget, reach_goal, cprc, sov]})
        df_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
        bench_data.to_excel(writer, sheet_name='Benchmarks', index=False)

    st.download_button("📥 Download Digital Media Plan", buffer.getvalue(), f"Digital_Plan_{market}.xlsx")
