import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(
    page_title="Pro Digital Planner 2026", 
    layout="wide", 
    page_icon="📊"
)

# --- 2. ENHANCED CSS STYLING ---
st.markdown("""
    <style>
    /* Professional Background & Font */
    .stApp { background-color: #F1F5F9 !important; }
    
    /* Branding Header */
    .header-container {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
    }
    .logo-icon { font-size: 2.5rem; margin-right: 15px; }
    .brand-title { 
        color: #1E3A8A; 
        font-size: 2rem; 
        font-weight: 800; 
        font-family: 'Inter', sans-serif;
        margin: 0;
    }

    /* Glassmorphic Filter Section */
    .filter-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }

    /* KPI Result Box */
    .kpi-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border-left: 8px solid #3B82F6;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* Force Label Colors for Readability */
    label, p, h1, h2, h3, h4, .stMarkdown {
        color: #1E3A8A !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Primary Button Styling */
    .stButton>button {
        background: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 3.5rem !important;
        font-
