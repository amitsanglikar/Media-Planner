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
    model = genai.GenerativeModel('gemini-2.0-flash') 
except Exception as e:
    st.error("Setup Error: Please ensure GEMINI_API_KEY is in your .streamlit/secrets.toml")
    st.stop()

# --- 3. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #020617 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; min-width: 380px !important; }
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
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(59, 130, 246, 0), rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0)); margin: 30px 0; }
    .stDataFrame { background: rgba(30, 41, 59, 0.2); border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. EXHAUSTIVE GEOGRAPHY DATABASE (SOURCE OF TRUTH) ---
INDIA_GEO_DATABASE = {
    "North": {
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Shahdara", "North West Delhi", "South East Delhi"],
        "Haryana": ["Gurugram", "Faridabad", "Ambala", "Panipat", "Rohtak", "Hisar", "Karnal", "Sonipat", "Panchkula"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Hoshiarpur", "Pathankot"],
        "Uttar Pradesh": ["Lucknow", "Kanpur Nagar", "Ghaziabad", "Agra", "Varanasi", "Meerut", "Prayagraj", "Noida", "Aligarh", "Bareilly", "Gorakhpur"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara", "Alwar", "Sikar"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Haldwani", "Roorkee"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Himachal Pradesh": ["Shimla", "Solan", "Dharamshala"]
    },
    "West": {
        "Maharashtra": ["Mumbai City", "Mumbai Suburban", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati", "Navi Mumbai", "Kolhapur"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Junagadh", "Anand"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Rewa", "Ratlam"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
        "Goa": ["North Goa", "South Goa"]
    },
    "South": {
        "Karnataka": ["Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi", "Ballari", "Udupi"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore", "Thoothukudi"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Rajahmundry", "Tirupati", "Kakinada"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Malappuram", "Kollam", "Palakkad"]
    },
    "East/NE": {
        "West Bengal": ["Kolkata", "Howrah", "Asansol", "Siliguri", "Durgapur", "Bardhaman", "Malda", "Baharampur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Bihar Sharif"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
        "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur", "Tinsukia"],
        "Arunachal Pradesh": ["Itanagar", "Tawang", "Naharlagun", "Pasighat"],
        "Manipur": ["Imphal East", "Imphal West", "Thoubal", "Churachandpur"],
        "Meghalaya": ["Shillong", "Tura", "Jowai"],
        "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
        "Nagaland": ["Dimapur", "Kohima", "Mokokchung", "Tuensang"],
        "Tripura": ["Agartala", "Dharmanagar", "Udaipur"],
        "Sikkim": ["Gangtok", "Namchi", "Geyzing"]
    }
}

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Media Command</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Overall", "Urban", "Rural"], horizontal=True)
    
    sel_zones = st.multiselect("1. Regions", list(INDIA_GEO_DATABASE.keys()))
    
    # State Logic based on Zone
    avail_states = []
    for z in sel_zones:
        avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
    sel_states = st.multiselect("2. States", sorted(avail_states))

    # District Logic based on State
    avail_districts = []
    FLAT_MAP = {}
    for z in INDIA_GEO_DATABASE:
        FLAT_MAP.update(INDIA_GEO_DATABASE[z])
    for s in sel_states:
        avail_districts.extend(FLAT_MAP.get(s, []))
    sel_districts = st.multiselect("3. Districts", sorted(list(set(avail_districts))))

    st.markdown("---")
    sel_age = st.multiselect("4. Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24"])
    sel_gender = st.radio("5. Gender Focus", ["Both", "Male", "Female"], horizontal=True)
    sel_nccs = st.multiselect("6. NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.markdown("---")
    exp_reach = st.slider("Reach Goal (%)", 5, 100, 45)
    eff_freq_n = st.number_input("Effective Freq (N+)", 1, 10, 4)
    run_calc = st.button("EXECUTE ANALYSIS")

# --- 6. MAIN OUTPUT ---
st.markdown("<h1 style='color:white;'>Digital Media <span style='color:#3B82F6;'>Terminal 2026</span></h1>", unsafe_allow_html=True)

if run_calc:
    with st.spinner('📡 Gemini AI is fetching dual-layer media data...'):
        # 1. KPI MATH (Simulated Baseline)
        state_count = len(sel_states) if sel_states else 1
        age_count = len(sel_age) if sel_age else 1
        qual_u = int(1250000 * (state_count * 0.15) * (age_count * 0.2))
        planned_reach_abs = int(qual_u * (exp_reach/100))
        total_imps_val = int(planned_reach_abs * eff_freq_n * 1.25)
        
        # 2. KPI CARDS
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="label-text">Universe</div><div class="value-text">{qual_u:,}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="label-text">Reach Target</div><div class="value-text">{planned_reach_abs:,}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-orange"><div class="label-text">Freq Cap</div><div class="value-text">{eff_freq_n}+</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="label-text">Total Imps</div><div class="value-text" style="color:#10B981;">{total_imps_val:,}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # 3. AI DUAL-TABLE PROMPT
        prompt = f"""
        Act as a 2026 India Media Planner.
        Context: {m_type} market in {sel_states}, Districts: {sel_districts}.
        Target Audience: {sel_gender}, Age: {sel_age}, NCCS: {sel_nccs}.
        
        Generate:
        1. Top 10 Media Genres (Content Categories)
        2. Top 10 Media Platforms (Publishers/Apps)
        
        Include: Name, Reach%, Affinity Index, Time Spent (Daily), and Ranking.
        Return ONLY a Python dictionary with keys "genres" and "platforms".
        Format: {{"genres": [{{...}}], "platforms": [{{...}}]}}
        No prose, no markdown code blocks.
        """
        
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            if "```" in raw_text:
                raw_text = raw_text.split("```")[1].replace("python", "").replace("json", "").strip()
            
            data = ast.literal_eval(raw_text)
            
            # 4. DATA DISPLAY
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("<p class='label-text'>Top 10 Media Genres</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data["genres"]), hide_index=True, use_container_width=True)
            with col_b:
                st.markdown("<p class='label-text'>Top 10 Media Platforms</p>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(data["platforms"]), hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"AI Bridge Failed: {e}")
else:
    st.markdown("<div style='text-align:center; padding-top:100px; color:#64748B;'>READY FOR COMMAND // SOURCE MARKETS LOCKED</div>", unsafe_allow_html=True)
