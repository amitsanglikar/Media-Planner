import streamlit as st
import pandas as pd
import numpy as np

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. ELITE-UI CSS (FINALIZED) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #3B82F6;
    }
    .metric-card-orange {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(251, 146, 60, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #FB923C;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .stTable { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GENERATIVE PLANNING LOGIC ENGINE ---
def get_dynamic_media_mix(age, market, gender, nccs, total_imps):
    """
    Generative function that assigns Reach, Affinity, and Time Spent 
    based on demographic profiles.
    """
    # Base Data Structure
    genres = ["Short Video", "Social Media", "OTT Video", "News/Info", "Gaming", "Music Streaming"]
    
    # Heuristic Logic for Affinity & Reach
    # Example: If age is 15-24, Gaming and Short Video affinity spikes
    is_young = any(a in ["15-24", "25-34"] for a in age)
    is_urban = (market == "Urban")
    is_female = (gender == "Female")
    
    data = []
    for g in genres:
        # Base stats modified by inputs
        reach = np.random.randint(40, 75)
        affinity = np.random.randint(90, 130)
        time_spent = np.random.randint(20, 90)
        
        if g == "Short Video" and is_young: 
            reach += 20; affinity += 30; time_spent += 40
        if g == "Gaming" and is_young and not is_female: 
            reach += 15; affinity += 40; time_spent += 60
        if g == "OTT Video" and is_urban: 
            reach += 10; affinity += 20; time_spent += 50
        if g == "News/Info" and not is_young: 
            reach += 25; affinity += 35; time_spent += 20
            
        # Scoring for Ranking
        score = (reach * 0.4) + (affinity * 0.4) + (time_spent * 0.2)
        
        data.append({
            "Media Channel": g,
            "Reach%": f"{min(reach, 98)}%",
            "Affinity Index": min(affinity, 190),
            "Time Spent (Min)": f"{time_spent}m",
            "Score": round(score, 1)
        })
    
    df = pd.DataFrame(data).sort_values(by="Score", ascending=False)
    df["Ranking"] = range(1, len(genres) + 1)
    return df.drop(columns=["Score"])

# --- 4. SIDEBAR INPUTS ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    st.markdown("---")
    sel_states = st.multiselect("Select States", ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "UP", "Bihar", "West Bengal"])
    sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24"])
    sel_gender = st.radio("Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    weeks_on_air = st.slider("Weeks on Air", 1, 52, 4)
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 5. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 GENERATING AI-LED MEDIA PLAN...'):
        # Calculation for Top KPIs
        qual_u = int(962500 * (len(sel_states)*0.1 if sel_states else 1.0) * (len(sel_age)*0.25))
        planned_reach_abs = int(qual_u * (exp_reach/100))
        total_imps_val = int(planned_reach_abs * 5.2)

        # KPI ROW
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Universe</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Planned Reach</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Avg Freq</div><div class="value-text">5.2</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Total Imps</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- DYNAMIC AI-LED TABLES ---
        st.markdown("<p class='label-text'>Input-Led Media Affinity Matrix</p>", unsafe_allow_html=True)
        dynamic_df = get_dynamic_media_mix(sel_age, m_type, sel_gender, sel_nccs, total_imps_val)
        st.table(dynamic_df)

else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>TERMINAL STANDBY // SELECT DEMOGRAPHICS TO GENERATE AFFINITY DATA</div>", unsafe_allow_html=True)
