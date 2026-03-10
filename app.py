import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. SECURE API CONFIGURATION ---
# This pulls the key from secrets.toml locally or from the Cloud Secrets dashboard
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("Missing API Key. Please add GEMINI_API_KEY to your secrets.")
    st.stop()

# --- 3. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 350px !important; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(15px); padding: 1.5rem; border-radius: 16px; border-left: 4px solid #3B82F6;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; margin-top: 4px; }
    .stDataFrame { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GEOGRAPHY DATABASE (FROZEN) ---
INDIA_GEO_DATABASE = {
    "North": {"Delhi": ["Central Delhi", "New Delhi"], "Haryana": ["Gurugram", "Faridabad"], "Punjab": ["Ludhiana", "Amritsar"], "Uttar Pradesh": ["Lucknow", "Noida"]},
    "West": {"Maharashtra": ["Mumbai City", "Pune", "Nagpur"], "Gujarat": ["Ahmedabad", "Surat"]},
    "South": {"Karnataka": ["Bengaluru Urban", "Mysuru"], "Tamil Nadu": ["Chennai", "Coimbatore"], "Telangana": ["Hyderabad"]},
    "East/NE": {"West Bengal": ["Kolkata", "Howrah"], "Bihar": ["Patna"]}
}

# --- 5. SIDEBAR INPUTS ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    sel_zones = st.multiselect("1. Regions", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. States", sorted(avail_states))
    
    sel_age = st.multiselect("3. Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24"])
    sel_gender = st.radio("4. Gender", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("5. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    run_calc = st.button("EXECUTE DUAL-LAYER ANALYSIS")

# --- 6. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 Gemini AI is fetching dual-layer media data...'):
        prompt = f"""
        Act as a Media Planner for the India market in 2026. 
        Target: {m_type} market in {sel_states}. Audience: {sel_gender}, Age {sel_age}, NCCS {sel_nccs}.
        Provide:
        1. Top 10 MEDIA GENRES (Content focus)
        2. Top 10 MEDIA PLATFORMS (Placement focus)
        For each entry, include: Reach%, Affinity Index, Time Spent (Daily), and Ranking (1-10).
        Return ONLY a Python dictionary with keys "genres" and "platforms". 
        Example: {{"genres": [{{...}}], "platforms": [{{...}}]}}
        Strictly no conversation or markdown code blocks.
        """
        
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            # Cleaning AI noise
            if "```" in raw_text: raw_text = raw_text.split("```")[1].replace("python", "").replace("json", "").strip()
            
            data = ast.literal_eval(raw_text)
            df_genres = pd.DataFrame(data["genres"])
            df_platforms = pd.DataFrame(data["platforms"])

            # KPI Header
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Market</div><div class="value-text">{m_type}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Target</div><div class="value-text">{", ".join(sel_age)}</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><div class="label-text">Gender</div><div class="value-text">{sel_gender}</div></div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)

            # Dual Tables
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("<p class='label-text'>Top 10 Media Genres</p>", unsafe_allow_html=True)
                st.dataframe(df_genres, hide_index=True, use_container_width=True)
            
            with col_b:
                st.markdown("<p class='label-text'>Top 10 Media Platforms</p>", unsafe_allow_html=True)
                st.dataframe(df_platforms, hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"AI Connection Failed: {e}")
else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>READY FOR COMMAND // USING SECURE API BRIDGE</div>", unsafe_allow_html=True)
