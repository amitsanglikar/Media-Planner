import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast
import re
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM CONFIG ---
st.set_page_config(page_title="Impact Media Terminal 2026", layout="wide", page_icon="📡")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') 
except:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. THE BREAKTHROUGH ENGINE ---
def calculate_impact_physics(reach_goal_n, n_plus, weeks, m_type):
    """
    Solves for Lambda using Breakthrough Logic:
    1. Solve Poisson for N+ Goal.
    2. Apply 1.3x Wastage Multiplier (Clutter Buffer).
    """
    l_raw = 0
    # Solve for the raw statistical average needed to hit the N+ Reach goal
    for l in np.arange(0.1, 150.0, 0.1):
        if (stats.poisson.sf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_raw = l
            break
    
    # Apply the 1.3x Wastage Multiplier for real-world impact
    l_impact = l_raw * 1.3
    
    reach_1p = (1 - math.exp(-l_impact)) * 100
    capacity = 60 if m_type == "Urban" else 35
    sov = (l_impact / (capacity * weeks)) * 100
    
    # Pricing logic stays dynamic
    base_ecpm = 175 if m_type == "Urban" else 105
    dynamic_ecpm = base_ecpm * (1 + (sov / 100))
    
    if l_impact < 6: tier, color, impact = "FORGETTABLE", "#64748B", "Lost in the scroll."
    elif 10 <= l_impact <= 12: tier, color, impact = "SWEET SPOT", "#00f2ff", "Optimal Brand Recall."
    elif l_impact > 15: tier, color, impact = "DOMINANT", "#bc13fe", "Maximum Market Impact."
    else: tier, color, impact = "CHALLENGER", "#94a3b8", "Breaking through noise."
    
    return round(l_impact, 1), round(reach_1p, 1), round(sov, 1), tier, color, impact, round(dynamic_ecpm, 2)

# --- 3. TERMINAL UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 380px !important; }
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 160px;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; }
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 10px 20px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 30px 0 15px 0; font-size: 0.9rem; letter-spacing: 2px;
    }
    .sov-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. TOP BAR & MODAL ---
st.markdown('<p style="font-size:2.8rem; font-weight:900; color:white; margin-bottom:0;">BREAKTHROUGH <span style="color:#00f2ff;">MEDIA TERMINAL</span></p>', unsafe_allow_html=True)

@st.dialog("GLOSSARY & IMPACT LOGIC")
def open_glossary():
    st.markdown("""
    <div style="color:#f8fafc; line-height:1.6;">
        <b style="color:#00f2ff;">Actual Frequency (Impact-Weighted):</b><br>
        The total average weight required after applying a <b>1.3x Wastage Multiplier</b>. This accounts for non-viewable impressions and ad blindness.
        <br><br>
        <b style="color:#00f2ff;">The 3-5-10 Rule:</b><br>
        - <b>< 6:</b> Threshold of Forgetfulness.<br>
        - <b>10-12:</b> Brand Recall "Sweet Spot".<br>
        - <b>> 15:</b> Maximum Breakthrough.
        <br><br>
        <b style="color:#00f2ff;">Dynamic eCPM:</b><br>
        Market-adjusted rate based on SOV. Higher SOV targets lead to premium "Impact Pricing."
    </div>
    """, unsafe_allow_html=True)

if st.button("🔍 OPEN GLOSSARY & LOGIC"):
    open_glossary()

# --- 5. SIDEBAR (GEO & INPUTS) ---
# [Note: INDIA_GEO_DATABASE remains as per your previous locked configuration]
# (Skipping database repetition for brevity in this snippet)

with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff;'>PLANNING_COMMAND</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    st.markdown("---")
    # ... [Geo Selection Logic as previously implemented] ...
    r_goal = st.slider("Reach Target % @ N+", 5, 95, 45)
    n_eff = st.number_input("Freq Threshold (N+)", 1, 15, 4)
    weeks = st.slider("Duration (Weeks)", 1, 12, 4)
    execute = st.button("EXECUTE IMPACT PLAN", use_container_width=True)

# --- 6. OUTPUT DASHBOARD ---
if execute:
    freq, r1_perc, sov_val, tier, t_color, t_impact, dynamic_ecpm = calculate_impact_physics(r_goal, n_eff, weeks, m_type)
    
    # Calculation for Budget/Imps based on Impact Frequency
    # (Using a standard universe scale for this example)
    universe = 12500000 
    r1_abs = int(universe * (r1_perc / 100))
    total_imps = int(r1_abs * freq)
    est_budget = (total_imps / 1000) * dynamic_ecpm

    st.markdown('<div class="section-header">IMPACT METRICS (CLUTTER ADJUSTED)</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card"><div class="label">Actual Frequency</div><div class="value">{freq}</div><div class="sub-value">Incl. 1.3x Wastage</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card"><div class="label">Net Reach @ 1+</div><div class="value">{r1_perc}%</div><div class="sub-value">{r1_abs:,} People</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card-impact"><div class="label">Impact Grade</div><div class="value" style="color:{t_color};">{tier}</div><div class="sub-value">{t_impact}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card"><div class="label">Total Imps</div><div class="value">{total_imps:,}</div><div class="sub-value">Total Weight</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">FINANCIALS</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: st.markdown(f'<div class="metric-card"><div class="label">Total Budget</div><div class="value">₹{int(est_budget):,}</div></div>', unsafe_allow_html=True)
    with f2: st.markdown(f'<div class="metric-card"><div class="label">Impact eCPM</div><div class="value">₹{dynamic_ecpm}</div></div>', unsafe_allow_html=True)
    with f3: st.markdown(f'<div class="metric-card"><div class="label">Cost / Unique</div><div class="value">₹{round(est_budget/r1_abs, 2)}</div></div>', unsafe_allow_html=True)
