import streamlit as st
import pandas as pd
import io
import numpy as np

# --- 1. Page Configuration ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide", page_icon="📈")

# --- 2. Custom Header ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>Data-Driven Digital Strategy for the Indian Market</p>", unsafe_allow_html=True)
st.divider()

# --- 3. Sidebar Inputs (Based on your UI requirements) ---
with st.sidebar:
    st.header("Campaign Configuration")
    tg = st.selectbox("Target Group (TG)", ["All 15+", "Male 15-24", "Female 25-44", "Gen Z", "Working Professionals"])
    market = st.selectbox("Market", ["Pan India", "Maharashtra", "Tamil Nadu", "Karnataka", "West Bengal", "Delhi NCR"])
    nccs = st.selectbox("NCCS Tier", ["A1", "A2", "B1", "B2", "C"])
    creative_format = st.selectbox("Creative Format", ["Video (15s/30s)", "Static Banners", "Social/Reels", "Impact Mastheads"])
    
    st.divider()
    reach_goal = st.slider("Target Reach (%)", 10, 100, 60)
    eff_freq = st.number_input("Required Effective Frequency", 1, 10, 3)
    woa = st.number_input("Weeks on Air (WOA)", 1, 12, 4)
    
    st.info("The logic accounts for NCCS benchmarks and Regional Language Multipliers.")
    submit = st.button("Generate Strategy", type="primary")

# --- 4. Logic & Output Generation ---
if submit:
    # --- A. Scoring Logic & Top 5 Platforms ---
    # Formula: (Reach*0.4) + (Affinity*0.4) + (Time*0.2)
    # Regional Multiplier: +20% Affinity for local apps in specific states
    platforms = ["YouTube", "Meta", "JioCinema", "WhatsApp", "SunNXT" if market == "Tamil Nadu" else "Zee5"]
    reach_stats = [88, 82, 70, 94, 52]
    affinity_stats = [1.1, 1.0, 1.2, 1.1, 1.4] # 1.4 includes regional boost
    time_stats = [0.9, 0.8, 0.7, 0.95, 0.6]

    # Calculate Weighted Scores
    scores = [(r*0.4 + a*40 + t*20) for r, a, t in zip(reach_stats, affinity_stats, time_stats)]
    
    df_ranking = pd.DataFrame({
        "Rank": [1, 2, 3, 4, 5],
        "Platform":
