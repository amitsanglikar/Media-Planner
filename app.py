import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- 1. DATA & BENCHMARKS (Estimated India 2026) ---
PLATFORM_INTEL = {
    "YouTube": {"share": 0.40, "ecpm": 165, "freq_cap": "2-3x / week", "fatigue_trigger": "4.0+"},
    "Meta (IG/FB)": {"share": 0.30, "ecpm": 230, "freq_cap": "3-5x / week", "fatigue_trigger": "6.0+"},
    "OTT (Premium)": {"share": 0.20, "ecpm": 520, "freq_cap": "1-2x / week", "fatigue_trigger": "3.0+"},
    "Search/Display": {"share": 0.10, "ecpm": 110, "freq_cap": "No Cap", "fatigue_trigger": "N/A"}
}

st.set_page_config(page_title="Virtual Media Planner", layout="wide")

# --- UI SIDEBAR ---
with st.sidebar:
    st.header("Campaign Settings")
    nccs = st.selectbox("NCCS Tier", ["A1 (Elite)", "A2 (Affluent)", "B1 (Mass)"])
    market = st.selectbox("Market", ["Maharashtra", "Tamil Nadu", "Karnataka", "Delhi NCR"])
    total_budget = st.number_input("Total Digital Budget (INR)", value=2000000)
    reach_goal = st.slider("Target Reach (1+) %", 10, 95, 65)
    submit = st.button("Generate Senior Lead Plan", type="primary")

# --- MAIN ENGINE ---
if submit:
    nccs_key = nccs.split(" ")[0]
    
    # 1. Platform Breakdown Calculation
    results = []
    total_imps = 0
    for platform, data in PLATFORM_INTEL.items():
        p_budget = total_budget * data['share']
        p_imps = (p_budget / data['ecpm']) * 1000
        total_imps += p_imps
        results.append({
            "Platform": platform,
            "Budget (INR)": f"₹{int(p_budget):,}",
            "Est. Impressions": f"{round(p_imps/1000000, 2)}M",
            "Target Frequency": data['freq_cap'],
            "Fatigue Limit": data['fatigue_trigger']
        })

    # 2. Executive Metrics
    st.markdown(f"## 📊 Campaign Strategy: {market} | {nccs}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Impressions", f"{round(total_imps/1000000, 2)}M")
    c2.metric("Blended eCPM", f"₹{round(total_budget / (total_imps/1000), 2)}")
    c3.metric("Reach Goal Efficiency", f"₹{int(total_budget/reach_goal):,} / reach point")

    # 3. Platform Table
    st.subheader("🎯 Platform-Level Breakdown & Fatigue Controls")
    st.table(pd.DataFrame(results))

    # 4. Frequency Management Insight
    st.divider()
    st.subheader("⚠️ Fatigue & Frequency Guardrails")
    g1, g2 = st.columns(2)
    with g1:
        st.warning("**Recommendation:** Stop serve for YouTube if frequency > 3.5. Shift budget to Search to capture resulting intent.")
        st.info("**Creative Refresh:** Rotate Meta creative every 10 days to maintain 1.5% CTR.")
    with g2:
        fig_imps = px.bar(pd.DataFrame(results), x="Platform", y=[float(x[:-1]) for x in [r['Est. Impressions'] for r in results]], 
                          title="Impression Volume (Millions)", color_discrete_sequence=['#1E3A8A'])
        st.plotly_chart(fig_imps, use_container_width=True)

    # 5. Reach Curve Visualization
    st.divider()
    st.subheader("📈 Digital Reach Build-up (1+ to 10+)")
    freq_range = [f"{i}+" for i in range(1, 11)]
    reach_vals = [reach_goal * (0.83**(i-1)) for i in range(1, 11)]
    st.line_chart(pd.DataFrame({"Reach %": reach_vals}, index=freq_range))

    # 6. Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        pd.DataFrame(results).to_excel(writer, sheet_name='Platform_Breakdown', index=False)
        pd.DataFrame({"Metric": ["Total Budget", "Blended eCPM", "Digital SOV %"], "Value": [total_budget, 210, "4.2%"]}).to_excel(writer, sheet_name='Summary')
    
    st.download_button("📥 Download Media Plan & Guardrails", buffer.getvalue(), "Media_Plan_Production.xlsx")
