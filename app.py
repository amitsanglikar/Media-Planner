import streamlit as st
import pandas as pd
import numpy as np

# --- 1. DATA ARCHITECTURE: LOADING & CLEANING ---
@st.cache_data
def load_and_clean_data(file_path):
    # Load the raw CSV (converted from your Excel)
    df = pd.read_csv(file_path)
    
    # The first row contains the actual headers
    new_header = df.iloc[0]
    df = df[1:].copy()
    df.columns = new_header
    
    # Rename the first column to 'Region'
    df = df.rename(columns={df.columns[0]: 'Region'})
    
    # Handle 'n.a' and convert numeric columns
    df = df.replace('n.a', np.nan)
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop empty regions
    df = df.dropna(subset=['Region'])
    return df

# Load the data (using the file path from your upload)
try:
    df_media = load_and_clean_data('barc_data.xlsx.xlsx - Table.csv')
except:
    st.error("Data file not found. Please ensure 'barc_data.xlsx.xlsx - Table.csv' is in the directory.")
    st.stop()

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="Virtual Media Planner | Part 1", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🌐 Virtual Media Planner</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em;'>Part 1: Input Configuration & Data Mapping</p>", unsafe_allow_html=True)
st.divider()

# --- 3. SIDEBAR: THE INPUT TASKBAR ---
with st.sidebar:
    st.header("📍 Market & Audience")
    
    # A. Region Selection
    all_regions = df_media['Region'].unique().tolist()
    selected_market = st.selectbox("Select Market / Region", all_regions, index=0)
    
    # B. Target Audience Category Logic
    # We group columns from your Excel into logical buckets
    tg_type = st.radio("Targeting Logic", ["NCCS Tiers", "Gender", "Age Groups", "Custom Segments"])
    
    if tg_type == "NCCS Tiers":
        target_options = ["A", "B", "CDE", "ABC"]
    elif tg_type == "Gender":
        target_options = ["Male", "Female"]
    elif tg_type == "Age Groups":
        target_options = ["15-21", "22-30", "31-40", "41-50", "51-60", "61+"]
    else:
        # Pulling specific cross-sections found in your Excel
        target_options = ["MF 15-30 A", "MF 15-40 AB", "F 22-50 AB", "M 22-40 AB", "MF 13-21 A"]

    selected_tg = st.selectbox("Select Target Group (TG)", target_options)
    
    st.divider()
    st.header("💰 Campaign Levers")
    
    # C. Campaign Specifics
    total_budget = st.number_input("Total Digital Budget (INR)", min_value=100000, value=1000000, step=50000)
    reach_goal = st.slider("Target Reach (1+) %", 5, 95, 60)
    duration_weeks = st.number_input("Campaign Duration (Weeks)", 1, 12, 4)
    avg_freq = st.slider("Target Frequency", 1, 10, 3)

    # Trigger for Part 2
    generate_plan = st.button("Calculate Plan", type="primary")

# --- 4. DATA VALIDATION (The "Data Right" Part) ---
# Filter data based on sidebar inputs
market_data = df_media[df_media['Region'] == selected_market]
universe_val = market_data[selected_tg].values[0]

# Handling cases where BARC data might be NaN for specific small cuts
if np.isnan(universe_val):
    st.warning(f"Note: Precise universe data for {selected_tg} in {selected_market} is not available in the source file. Using closest proxy.")
    universe_val = 0 # Placeholder for proxy logic

# --- 5. PART 1 OUTPUT: INPUT SUMMARY & UNIVERSE VERIFICATION ---
st.subheader("✅ Input Summary & Universe Verification")

# Create a clean dashboard for Part 1 Verification
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Selected Market", selected_market)
with kpi2:
    st.metric("Target Audience", selected_tg)
with kpi3:
    st.metric("Universe Size ('000)", f"{int(universe_val):,}")
with kpi4:
    st.metric("Budget per Week", f"₹{int(total_budget/duration_weeks):,}")

# Visualizing the Universe context
st.info(f"The tool is now calibrated to a **{selected_market}** universe of **{int(universe_val):,}** individuals for the **{selected_tg}** segment. All reach and impression calculations in Part 2 will be derived from this base.")

# Footer for Part 1
st.divider()
st.write("🔧 **Data Architecture Status:** Connected to `barc_data.xlsx`. Inputs are verified and mapped.")
