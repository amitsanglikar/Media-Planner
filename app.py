import streamlit as st
import pandas as pd
import numpy as np

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Virtual Media Planner", layout="wide", page_icon="🌐")

# --- 2. THE "MOCK-FAITHFUL" CSS OVERRIDE ---
st.markdown("""
    <style>
    :root {
        --primary-color: #1E3A8A;
        --bg-color: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-color: #1E293B;
    }

    .stApp {
        background-color: var(--bg-color) !important;
    }

    /* Force all text elements to the Navy Blue from the mock */
    label, .stMarkdown, p, h1, h2, h3, h4, h5, [data-testid="stWidgetLabel"] p {
        color: #1E3A8A !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* The White Box Container for inputs */
    .filter-section {
        background-color: #FFFFFF !important;
        padding: 30px !important;
        border-radius: 15px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 25px !important;
    }

    /* Widget Backgrounds */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Professional Metric Cards */
    .kpi-card {
        background-color: white !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border-left: 6px solid #1E3A8A !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        margin-bottom: 15px !important;
    }

    /* Action Button (Coral/Red) */
    .stButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
        margin-top: 25px !important;
        transition: 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #E03E3E !important;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ENGINE: MARKET MASTER ---
MARKET_MASTER = {
    "India (Total)": {"base": 1400000, "internet_pen": 0.55},
    "Mumbai": {"base": 21000, "internet_pen": 0.85},
    "Delhi NCR": {"base": 32000, "internet_pen": 0.82},
    "Bangalore": {"base": 13000, "internet_pen": 0.88},
    "Chennai": {"base": 11000, "internet_pen": 0.84},
    "Kolkata": {"base": 15000, "internet_pen": 0.75},
    "Hyderabad": {"base": 10500, "internet_pen": 0.80},
    "Maharashtra": {"base": 95000, "internet_pen": 0.65},
    "Uttar Pradesh": {"base": 240000, "internet_pen": 0.45},
}

def calculate_universe(market, gender, age, nccs):
    data = MARKET_MASTER.get(market, {"base": 50000, "internet_pen": 0.50})
    base_digital = data['base'] * data['internet_pen']
    
    g_w = 0.50 if gender != "Both" else 1.0
    a_map = {"15-30": 0.45, "15-21": 0.18, "22-30": 0.27, "31-40": 0.20, "41-5
