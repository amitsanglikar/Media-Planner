import streamlit as st
import pandas as pd
import io

# --- Professional Page Setup ---
st.set_page_config(page_title="Media Planner Pro | India", layout="wide")
st.title("🇮🇳 Digital Media Planning Engine")

# --- Dropdowns & Sidebar Inputs ---
with st.sidebar:
    st.header("Campaign Inputs")
    tg = st.selectbox("TG (Target Group)", ["All 15+", "Male 18-34", "Female 25-44", "Gen Z (15-24)"])
    market = st.selectbox("Market", ["Pan India", "Maharashtra", "Tamil Nadu", "Karnataka", "West Bengal"])
    nccs = st.selectbox("NCCS", ["A1", "A2", "B1", "B2", "C"])
    creative = st.selectbox("Creative Format", ["Video (15s/30s)", "Static", "Impact Formats", "Influencer"])
    
    st.divider()
    reach_goal = st.slider("Target Reach %", 10, 100, 60)
    eff_freq = st.number_input("Effective Frequency", 1, 10, 3)
    woa = st.number_input("Weeks on Air", 1, 12, 4)
    
    submit = st.button("Generate Plan & Export", type="primary")

# --- Logic Processing ---
if submit:
    # 1. Platform Ranking Logic
    # Weighted Scoring: (Reach*0.4) + (Affinity*0.4) + (Time*0.2) + Regional Multiplier
    platforms = ["YouTube", "Meta", "JioCinema", "WhatsApp", "SunNXT" if market == "Tamil Nadu" else "Zee5"]
    reach_data = [85, 78, 65, 92, 45]
    scores = [88.2, 82.1, 75.4, 91.0, 78.5] # Sample results
    
    df_plan = pd.DataFrame({
        "Rank": [1, 2, 3, 4, 5],
        "Platform": platforms,
        "Reach %": reach_data,
        "Weighted Score": scores
    })

    # 2. Display Results
    st.subheader(f"Strategy for {nccs} in {market}")
    st.table(df_plan)

    # 3. Frequency Distribution (Reach Curve 1+ to 10+)
    st.subheader("Frequency Distribution (1+ to 10+)")
    freq_data = pd.DataFrame({
        "Frequency": [f"{i}+" for i in range(1, 11)],
        "Reach %": [reach_goal * (0.82**(i-1)) for i in range(1, 11)]
    })
    st.line_chart(freq_data.set_index("Frequency"))

    # --- THE DOWNLOAD BUTTON (Excel Export) ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_plan.to_excel(writer, sheet_name='Top 5 Platforms', index=False)
        freq_data.to_excel(writer, sheet_name='Reach Curve', index=False)
        
        # Adding Operating Levels Summary
        summary = pd.DataFrame({
            "Metric": ["Target Reach", "Target Frequency", "Total GRPs", "Weekly AOTS"],
            "Value": [f"{reach_goal}%", eff_freq, reach_goal * eff_freq, round((reach_goal * eff_freq)/woa, 2)]
        })
        summary.to_excel(writer, sheet_name='Operating Levels', index=False)

    st.download_button(
