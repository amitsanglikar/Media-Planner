import streamlit as st
import pandas as pd
import google.generativeai as genai
import math
import numpy as np
from scipy import stats

# --- 1. SYSTEM & API CONFIG ---
st.set_page_config(page_title="Virtual Media Terminal 2026", layout="wide", page_icon="📡")

try:
    # Attempt to load from Streamlit Secrets
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Using 1.5 Flash as the standard stable 2026 workhorse
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error("Setup Error: Ensure GEMINI_API_KEY is in secrets.")
    st.stop()

# --- 2. TERMINAL & MODAL STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;900&display=swap');
    
    .stApp { background-color: #050505 !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #0a0a0a !important; border-right: 1px solid #00f2ff33; min-width: 380px !important; }
    
    .metric-card, .metric-card-impact {
        background: rgba(0, 0, 0, 0.6); border: 1px solid #00f2ff33;
        padding: 1.5rem; border-radius: 12px; border-left: 5px solid #00f2ff;
        min-height: 160px; margin-bottom: 10px;
    }
    .metric-card-impact { border-color: #bc13fe33; border-left: 5px solid #bc13fe; }
    
    .label { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    .value { color: #ffffff; font-size: 2.1rem; font-weight: 900; margin-top: 5px; }
    .sub-value { font-size: 0.8rem; color: #888; margin-top: 8px; font-weight: 500; }
    
    .section-header {
        background: linear-gradient(90deg, #00f2ff11 0%, transparent 100%);
        padding: 10px 20px; border-left: 3px solid #00f2ff;
        color: #00f2ff; font-weight: 800; margin: 30px 0 15px 0; font-size: 0.9rem; letter-spacing: 2px;
    }
    
    .glossary-content {
        background: #0f172a; border: 1px solid #00f2ff; padding: 25px; border-radius: 15px;
        color: #f8fafc; line-height: 1.6;
    }
    .glossary-term { color: #00f2ff; font-weight: 700; font-family: 'JetBrains Mono'; display: block; margin-top: 12px; }
    
    .sov-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; margin-top: 10px; display: inline-block; color: white; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE (LOCKED) ---
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
METROS = ["Mumbai", "Delhi", "Bengaluru", "Kolkata", "Chennai", "Hyderabad", "Ahmedabad", "Pune"]

# --- 4. ENGINE ---
def calculate_physics(reach_goal_n, n_plus, weeks, m_type):
    l_final = 0
    # Iterative solver for Poisson distribution
    for l in np.arange(0.1, 150.0, 0.1):
        # We solve for the tail probability: P(X >= n_plus)
        if (1 - stats.poisson.cdf(n_plus - 1, l)) * 100 >= reach_goal_n:
            l_final = l
            break
    
    # 1.3x Wastage/Recall Multiplier is applied to the raw Lambda
    l_impact = l_final * 1.3
    
    reach_1p = (1 - math.exp(-l_impact)) * 100
    capacity = 60 if m_type == "Urban" else 35
    sov = (l_impact / (capacity * weeks)) * 100
    
    base_ecpm = 175 if m_type == "Urban" else 105
    dynamic_ecpm = base_ecpm * (1 + (sov / 100))
    
    if sov < 5: tier, color, impact = "MAINTENANCE", "#64748B", "Low recall threshold."
    elif sov < 15: tier, color, impact = "CHALLENGER", "#00f2ff", "Solid breakthrough."
    elif sov < 25: tier, color, impact = "DOMINANT", "#bc13fe", "Top of Mind dominance."
    else: tier, color, impact = "MONOPOLY", "#EF4444", "Category ownership."
    
    return round(l_impact, 1), round(reach_1p, 1), round(sov, 1), tier, color, impact, round(dynamic_ecpm, 2)

# --- 5. TOP BAR & MODAL ---
@st.dialog("GLOSSARY & INTELLIGENCE LOGIC")
def open_glossary():
    st.markdown("""
    <div class="glossary-content">
        <span class="glossary-term">Digital Universe (TAM)</span>
        The estimated total digital population. <b>Source:</b> IAMAI 2026 Internet in India Projection (950M Base).
        
        <span class="glossary-term">Actual Frequency</span>
        The raw average exposure (Lambda) needed to break market noise. Solved via the <b>Poisson distribution</b> to satisfy the user's N+ tail goal.
        [Image of Poisson distribution curve showing frequency of ad exposures]
        
        <span class="glossary-term">Reach @ 1+ (Derived)</span>
        Percentage of the audience touched at least once. <b>Formula:</b> $(1 - e^{-\lambda}) \\times 100$.
        
        <span class="glossary-term">Market SOV (Share of Voice)</span>
        Percentage of total weekly inventory capacity consumed by the campaign.
        
        <span class="glossary-term">Dynamic eCPM</span>
        Inventory pricing that adjusts based on demand. High SOV targets inflate the base CPM to reflect auction saturation.
    </div>
    """, unsafe_allow_html=True)

if st.button("🔍 OPEN GLOSSARY & LOGIC"):
    open_glossary()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00f2ff; font-family:JetBrains Mono;'>PLANNING_COMMAND</h2>", unsafe_allow_html=True)
    m_type = st.radio("Market Type", ["Urban", "Rural"], horizontal=True)
    
    st.markdown("---")
    zone_options = ["8 Metros"] + list(INDIA_GEO_DATABASE.keys())
    sel_zones = st.multiselect("Select Zones", zone_options)
    
    sel_districts = []
    if "8 Metros" in sel_zones:
        sel_metros = st.multiselect("Top 8 Metros", sorted(METROS), default=METROS)
        sel_districts.extend(sel_metros)
    
    # Filter out "8 Metros" to handle standard state/district selection
    standard_zones = [z for z in sel_zones if z != "8 Metros"]
    if standard_zones or (not sel_zones):
        avail_states = []
        target_zones = standard_zones if standard_zones else INDIA_GEO_DATABASE.keys()
        for z in target_zones:
            avail_states.extend(list(INDIA_GEO_DATABASE[z].keys()))
        
        sel_states = st.multiselect("Select States", sorted(list(set(avail_states))))
