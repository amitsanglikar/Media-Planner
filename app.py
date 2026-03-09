import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. GLOBAL CONFIGURATION & MOCK DATA ---
# This dictionary simulates the "Synthetic Benchmark" mode
SYNTHETIC_BENCHMARKS = {
    "A1": {"reach": 0.85, "affinity": 1.2, "time": 0.9},
    "A2": {"reach": 0.75, "affinity": 1.0, "time": 0.8},
    "B1": {"reach": 0.65, "affinity": 0.9, "time": 0.7},
    "B2": {"reach": 0.55, "affinity": 0.8, "time": 0.6}
}

REGIONAL_BOOSTS = {
    "Tamil Nadu": ["SunNXT", "Aha", "YouTube Tamil"],
    "West Bengal": ["Hoichoi", "YouTube Bengali"],
    "Maharashtra": ["Zee5", "YouTube Marathi"]
}

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide", page_icon="📈")

# Header Section
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.1em; color: #666;'>Senior Digital Media Planning Engine | Indian Market Edition</p>", unsafe_allow_html=True)
st.divider()

# --- 3. UI SIDEBAR (Input Section) ---
with st.sidebar:
    st.header("Campaign Parameters")
    tg = st.selectbox("Target Group (TG)", ["All 15+", "Male 18-34", "Female 25-44", "Gen Z (15-24)"])
    market = st.selectbox("Market", ["Pan India", "Maharashtra", "Tamil Nadu", "Karnataka", "West Bengal"])
    nccs = st.selectbox("NCCS Tier", ["A1", "A2", "B1", "B2"])
    creative = st.selectbox("Creative Format", ["Video", "Static", "Social/Influencer", "Impact"])
    
    st.divider()
    total_budget = st.number_input("Total Budget (INR)", min_value=100000, value=1000000, step=50000)
    reach_goal = st.slider("Target Reach (%)", 10, 100, 60)
    eff_freq = st.number_input("Effective Frequency", 1, 10, 3)
    woa = st.number_input("Weeks on Air", 1, 12, 4)
    
    submit = st.button("Generate Final Media Plan", type="primary")

# --- 4. CALCULATION & OUTPUT LOGIC ---
if submit:
    # A. Platform Scoring Logic
    base_stats = SYNTHETIC_BENCHMARKS.get(nccs, SYNTHETIC_BENCHMARKS["A2"])
    
    platforms = ["YouTube", "Meta", "WhatsApp", "JioCinema", "Local OTT"]
    # Dynamic name for local OTT
    if market == "Tamil Nadu": platforms[-1] = "SunNXT"
    elif market == "West Bengal": platforms[-1] = "Hoichoi"
    elif market == "Maharashtra": platforms[-1] = "Zee5"

    results = []
    for p in platforms:
        p_reach = base_stats["reach"] * np.random.uniform(0.8, 1.1) # Simulate variance
        p_affinity = base_stats["affinity"]
        
        # Apply Regional Boost
        if market in REGIONAL_BOOSTS and p in REGIONAL_BOOSTS[market]:
            p_affinity *= 1.2
            
        # Formula: (Reach*0.4) + (Affinity*0.4) + (Time*0.2)
        score = (p_reach * 40) + (p_affinity * 40) + (base_stats["time"] * 20)
        results.append({"Platform": p, "Reach%": round(p_reach*100, 1), "Score": round(score, 2)})

    df_ranking = pd.DataFrame(results).sort_values(by="Score", ascending=False)

    # B. Layout Columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🏆 Top Platform Rankings")
        st.dataframe(df_ranking, use_container_width=True, hide_index=True)
        
        st.subheader("⚙️ Operating Levels")
        grps = reach_goal * eff_freq
        st.metric("Total GRPs", f"{grps}")
        st.metric("Weekly GRP Goal", f"{round(grps/woa, 2)}")
        st.write(f"**Target AOTS:** {round(eff_freq * 1.3, 1)}")

    with col2:
        st.subheader("📈 Reach Distribution (1+ to 10+)")
        freq_indices = [f"{i}+" for i in range(1, 11)]
        # Logarithmic reach decay simulation
        reach_vals = [reach_goal * (0.83**(i-1)) for i in range(1, 11)]
        df_curve = pd.DataFrame({"Frequency": freq_indices, "Reach %": reach_vals})
        st.line_chart(df_curve.set_index("Frequency"))

    st.divider()

    # C. Budget Allocation Section
    st.subheader("💰 Recommended Budget Allocation")
    aware_amt, consid_amt, conver_amt = total_budget * 0.5, total_budget * 0.3, total_budget * 0.2
    
    b_col1, b_col2, b_col3 = st.columns(3)
    b_col1.metric("Awareness (50%)", f"₹{int(aware_amt):,}")
    b_col2.metric("Consideration (30%)", f"₹{int(consid_amt):,}")
    b_col3.metric("Conversion (20%)", f"₹{int(conver_amt):,}")

    fig = px.pie(
        values=[aware_amt, consid_amt, conver_amt], 
        names=['Awareness', 'Consideration', 'Conversion'],
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    st.plotly_chart(fig, use_container_width=True)

    # D. Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_ranking.to_excel(writer, sheet_name='Rankings', index=False)
        df_curve.to_excel(writer, sheet_name='Reach_Curve', index=False)
        pd.DataFrame({
            "Metric": ["TG", "Market", "NCCS", "Total Budget", "Weekly GRPs"],
            "Value": [tg, market, nccs, total_budget, round(grps/woa, 2)]
        }).to_excel(writer, sheet_name='Summary', index=False)

    st.download_button(
        label="📥 Download Plan as Excel",
        data=buffer.getvalue(),
        file_name=f"VMP_Plan_{market}.xlsx",
        mime="application/vnd.ms-excel"
    )

    st.success("Strategy Orchestrated Successfully!")
