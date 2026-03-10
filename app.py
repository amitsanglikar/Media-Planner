import streamlit as st
import pandas as pd
import google.generativeai as genai
import ast

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="🏛️")

# --- 2. SECURE API CONFIGURATION ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # FIX: Using the 2026 stable model name
    # Fallback list in case of regional unavailability
    AVAILABLE_MODELS = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-3-flash-preview']
    
    model = genai.GenerativeModel(AVAILABLE_MODELS[0])
except Exception as e:
    st.error("Setup Error: Please ensure GEMINI_API_KEY is in your .streamlit/secrets.toml")
    st.stop()

# --- 3. ELITE-UI CSS (Keep your styling) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    .metric-card {
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 1.5rem; border-radius: 16px; border-left: 4px solid #3B82F6;
    }
    .label-text { color: #94A3B8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .value-text { color: #F8FAFC; font-size: 2.1rem; font-weight: 800; }
    hr { border: 0; height: 1px; background: rgba(59, 130, 246, 0.2); margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GEOGRAPHY DATABASE ---
INDIA_GEO_DATABASE = {
    "North": {"Delhi": ["Central Delhi", "New Delhi"], "Uttar Pradesh": ["Lucknow", "Noida"]},
    "West": {"Maharashtra": ["Mumbai City", "Pune"], "Gujarat": ["Ahmedabad"]},
    "South": {"Karnataka": ["Bengaluru Urban"], "Tamil Nadu": ["Chennai"]},
    "East/NE": {"West Bengal": ["Kolkata"], "Bihar": ["Patna"]}
}

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    sel_zones = st.multiselect("1. Regions", list(INDIA_GEO_DATABASE.keys()))
    
    avail_states = []
    for z in sel_zones: avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. States", sorted(avail_states))
    
    sel_age = st.multiselect("3. Age", ["15-24", "25-34", "35-44", "45+"], default=["15-24"])
    sel_gender = st.radio("4. Gender", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("NCCS", ["A", "B", "C", "D"], default=["A"])
    
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 6. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 Connecting to Gemini 2.5 Intelligence...'):
        prompt = f"""
        Return a Python dictionary with two keys: "genres" and "platforms".
        Audience: {sel_gender}, Age {sel_age}, NCCS {sel_nccs} in {sel_states}.
        Provide Top 10 for each. Include keys: "Name", "Reach%", "Affinity", "TimeSpent".
        Return ONLY the dictionary. No conversation, no markdown code blocks.
        """
        
        try:
            response = model.generate_content(prompt)
            clean_text = response.text.strip()
            
            # Remove any markdown formatting if AI includes it
            if "```" in clean_text:
                clean_text = clean_text.split("```")[1].replace("python", "").replace("json", "").strip()
            
            res_dict = ast.literal_eval(clean_text)
            
            # Display KPIs
            c1, c2 = st.columns(2)
            with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Model Engaged</div><div class="value-text">Gemini 2.5</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Market</div><div class="value-text">{m_type}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Tables
            col_left, col_right = st.columns(2)
            with col_left:
                st.subheader("Top 10 Genres")
                st.dataframe(pd.DataFrame(res_dict["genres"]), use_container_width=True, hide_index=True)
            with col_right:
                st.subheader("Top 10 Platforms")
                st.dataframe(pd.DataFrame(res_dict["platforms"]), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error: {e}. Try changing the model name to 'gemini-2.0-flash' in the code.")
else:
    st.info("Select parameters and click Execute.")
