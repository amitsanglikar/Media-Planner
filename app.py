import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Media Intelligence Terminal", layout="wide", page_icon="📈")

# --- 2. ELITE-UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0F172A !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; border-right: 1px solid #334155; }
    .metric-card {
        background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
    }
    .label-text { color: #94A3B8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .value-text { color: #F8FAFC; font-size: 2.2rem; font-weight: 800; margin-top: 5px; }
    .sub-text { color: #3B82F6; font-size: 0.75rem; font-weight: 600; margin-top: 5px; }
    .stButton>button {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
        color: white !important; border-radius: 6px !important; font-weight: 800 !important; height: 3.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE ABSOLUTE MASTER DATABASE (ALL 36 ENTITIES) ---
METRO_DATA = {
    "Mumbai": 0.065, "Delhi": 0.072, "Bengaluru": 0.048, "Chennai": 0.038, 
    "Kolkata": 0.035, "Hyderabad": 0.042, "Ahmedabad": 0.028, "Pune": 0.031
}

INDIA_GEO_MASTER = {
    "North": {
        "Delhi NCR": ["New Delhi", "Gurgaon", "Noida", "Ghaziabad", "Faridabad"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Mohali"],
        "Haryana": ["Ambala", "Karnal", "Panipat", "Hisar", "Rohtak"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Udaipur", "Bikaner"],
        "Himachal Pradesh": ["Shimla", "Dharamshala", "Solan", "Mandi"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Haldwani", "Roorkee"],
        "Chandigarh": ["Chandigarh City"], "Ladakh": ["Leh", "Kargil"]
    },
    "West": {
        "Maharashtra": ["Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati"],
        "Gujarat": ["Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
        "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain"],
        "Goa": ["Panaji", "Margao", "Vasco da Gama"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba"],
        "Dadra & Nagar Haveli / Daman & Diu": ["Silvassa", "Daman", "Diu"]
    },
    "South": {
        "Karnataka": ["Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi"],
        "Tamil Nadu": ["Coimbatore", "Madurai", "Salem", "Tiruchirappalli", "Tiruppur"],
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool"],
        "Telangana": ["Warangal", "Nizamabad", "Khammam", "Karimnagar"],
        "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam"],
        "Puducherry": ["Puducherry City", "Karaikal"], "Lakshadweep": ["Kavaratti"]
    },
    "East/NE": {
        "West Bengal": ["Howrah", "Durgapur", "Siliguri", "Asansol", "Kharagpur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar"],
        "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon"],
        "Sikkim": ["Gangtok"], "Arunachal Pradesh": ["Itanagar"], "Manipur": ["Imphal"],
        "Meghalaya": ["Shillong"], "Mizoram": ["Aizawl"], "Nagaland": ["Kohima"],
        "Tripura": ["Agartala"], "Andaman & Nicobar": ["Port Blair"]
    }
}

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>Targeting Terminal</h2>", unsafe_allow_html=True)
    
    sel_metros = st.multiselect("Top 8 Metros", list(METRO_DATA.keys()))
    is_metro = len(sel_metros) > 0
    
    st.markdown("---")
    
    sel_regions = st.multiselect("Region Filter", ["North", "West", "South", "East/NE"], disabled=is_metro)
    
    available_states = []
    if not is_metro:
        for r in sel_regions:
            available_states.extend(list(INDIA_GEO_MASTER[r].keys()))
    sel_states = st.multiselect("States", sorted(available
