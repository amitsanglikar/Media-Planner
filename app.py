import streamlit as st
import pandas as pd

# --- 1. CONFIG & DATA ---
st.set_page_config(page_title="Pro Digital Planner 2026", layout="wide")

# Industry Benchmarks (IAMAI 2025/2026)
TOTAL_DIGITAL_UNIVERSE = 958000 # '000s (958 Million)

# State & District Hierarchy (Sample Mapping)
GEOGRAPHY = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane", "Solapur"],
    "Delhi NCR": ["Central Delhi", "North Delhi", "South Delhi", "Gurgaon", "Noida", "Ghaziabad"],
    "Karnataka": ["Bangalore Urban", "Bangalore Rural", "Mysore", "Hubli-Dharwad", "Belgaum"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Prayagraj"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"]
}

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stMultiSelect div[data-baseweb="select"] { background-color: white !important; }
    .kpi-box {
        background: #ffffff; padding: 20px; border-radius: 10px;
        border-top: 5px solid #3B82F6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .sidebar-header { color: #1E3A8A; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. UI LAYOUT ---
st.title("📊 Advanced Media Planner (IAMAI 2026)")

with st.container():
    st.markdown("### 🌍 Geographic & Demographic Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sel_states = st.multiselect("Select States", list(GEOGRAPHY.keys()), default=["Maharashtra"])
        # Urban/Rural Split
        geo_type = st.radio("Market Type", ["Overall", "Urban Only", "Rural Only"], horizontal=True)
    
    with col2:
        # Get districts for all selected states
        available_districts = []
        for s in sel_states:
            available_districts.extend(GEOGRAPHY[s])
        
        sel_districts = st.multiselect("Select Districts", sorted(list(set(available_districts))))
        sel_gender = st.multiselect("Gender", ["Male", "Female"], default=["Male", "Female"])
        
    with col3:
        sel_age = st.multiselect("Age Groups", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
        sel_nccs = st.multiselect("NCCS", ["A", "B", "C", "D", "E"], default=["A", "B"])

# --- 4. CALCULATION ENGINE ---
def run_planner():
    # 1. Base Weight by State (Approximate Digital Share)
    state_weights = {"Maharashtra": 0.14, "Delhi NCR": 0.09, "Karnataka": 0.08, "Tamil Nadu": 0.09, "Uttar Pradesh": 0.16, "West Bengal": 0.08, "Gujarat": 0.07}
    
    total_weight = sum([state_weights.get(s, 0.05) for s in sel_states])
    base_u = TOTAL_DIGITAL_UNIVERSE * total_weight
    
    # 2. Urban/Rural Adjust (IAMAI 2025: 43% Urban / 57% Rural)
    if geo_type == "Urban Only": base_u *= 0.43
    elif geo_type == "Rural Only": base_u *= 0.57
    
    # 3. Demographic Weights
    # Age Split
    age_map = {"15-24": 0.35, "25-34": 0.30, "35-44": 0.20, "45+": 0.15}
    age_w = sum([age_map.get(a, 0) for a in sel_age])
    
    # NCCS Split
    nccs_map = {"A": 0.15, "B": 0.20, "C": 0.25, "D": 0.20, "E": 0.20}
    nccs_w = sum([nccs_map.get(n, 0) for n in sel_nccs])
    
    # Gender (IAMAI: 54% M / 46% F)
    gender_w = 0
    if "Male" in sel_gender: gender_w += 0.54
    if "Female" in sel_gender: gender_w += 0.46
    
    # Final Calculation
    final_universe = int(base_u * age_w * nccs_w * gender_w)
    return final_universe

# --- 5. RESULTS DISPLAY ---
if st.button("Calculate Plan", type="primary"):
    universe = run_planner()
    
    

    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown(f"""
        <div class="kpi-box">
            <p style="color:gray; margin:0;">Target Universe Size</p>
            <h1 style="color:#1E3A8A; margin:0;">{universe:,}</h1>
            <p style="font-size:12px;">Active Monthly Users (in '000s)</p>
        </div>
        """, unsafe_allow_html=True)

    with res_col2:
        st.markdown("### 📊 Audience Split")
        # Quick bar chart of Age distribution
        age_data = pd.DataFrame({"Age": sel_age, "Weight": [35, 30, 20, 15][:len(sel_age)]})
        st.bar_chart(age_data.set_index("Age"))
