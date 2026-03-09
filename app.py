import streamlit as st
import pandas as pd

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Triangulated Media Planner 2026", layout="wide")

# --- 2. THE MASTER GEO-DATABASE (TRAI & IAMAI 2026) ---
# Mapping all 36 States/UTs with their respective districts and LSA weights
INDIA_GEO_MASTER = {
    "Andhra Pradesh": {"districts": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Anantapur", "Chittoor", "Tirupati"], "trai_weight": 0.062},
    "Arunachal Pradesh": {"districts": ["Itanagar", "Tawang", "Ziro", "Pasighat"], "trai_weight": 0.002},
    "Assam": {"districts": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon", "Tinsukia"], "trai_weight": 0.028},
    "Bihar": {"districts": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Arrah"], "trai_weight": 0.051},
    "Chandigarh": {"districts": ["Chandigarh City"], "trai_weight": 0.005},
    "Chhattisgarh": {"districts": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Rajnandgaon"], "trai_weight": 0.018},
    "Delhi NCR": {"districts": ["New Delhi", "Gurgaon", "Noida", "Faridabad", "Ghaziabad", "South Delhi", "West Delhi"], "trai_weight": 0.095},
    "Goa": {"districts": ["Panaji", "Margao", "Vasco da Gama", "Mapusa"], "trai_weight": 0.008},
    "Gujarat": {"districts": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar"], "trai_weight": 0.071},
    "Haryana": {"districts": ["Gurugram", "Faridabad", "Ambala", "Karnal", "Panipat", "Hisar", "Rohtak"], "trai_weight": 0.022},
    "Himachal Pradesh": {"districts": ["Shimla", "Dharamshala", "Solan", "Mandi", "Hamirpur"], "trai_weight": 0.009},
    "Jammu & Kashmir": {"districts": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Kathua"], "trai_weight": 0.012},
    "Jharkhand": {"districts": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Deoghar"], "trai_weight": 0.024},
    "Karnataka": {"districts": ["Bengaluru", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi"], "trai_weight": 0.084},
    "Kerala": {"districts": ["Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur", "Kollam", "Kannur"], "trai_weight": 0.045},
    "Ladakh": {"districts": ["Leh", "Kargil"], "trai_weight": 0.001},
    "Madhya Pradesh": {"districts": ["Indore", "Bhopal", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Rewa"], "trai_weight": 0.055},
    "Maharashtra": {"districts": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati"], "trai_weight": 0.125},
    "Manipur": {"districts": ["Imphal", "Thoubal", "Churachandpur"], "trai_weight": 0.003},
    "Meghalaya": {"districts": ["Shillong", "Tura", "Jowai"], "trai_weight": 0.003},
    "Mizoram": {"districts": ["Aizawl", "Lunglei", "Champhai"], "trai_weight": 0.002},
    "Nagaland": {"districts": ["Kohima", "Dimapur", "Mokokchung"], "trai_weight": 0.002},
    "Odisha": {"districts": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri"], "trai_weight": 0.032},
    "Punjab": {"districts": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"], "trai_weight": 0.038},
    "Rajasthan": {"districts": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara"], "trai_weight": 0.062},
    "Sikkim": {"districts": ["Gangtok", "Namchi", "Geyzing"], "trai_weight": 0.002},
    "Tamil Nadu": {"districts": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tiruppur", "Erode"], "trai_weight": 0.092},
    "Telangana": {"districts": ["Hyderabad", "Warangal", "Nizamabad", "Khammam", "Karimnagar", "Ramagundam"], "trai_weight": 0.048},
    "Tripura": {"districts": ["Agartala", "Udaipur", "Dharmanagar"], "trai_weight": 0.003},
    "Uttar Pradesh": {"districts": ["Lucknow", "Kanpur", "Ghaziabad", "Agra", "Meerut", "Varanasi", "Prayagraj", "Bareilly"], "trai_weight": 0.110},
    "Uttarakhand": {"districts": ["Dehradun", "Haridwar", "Haldwani", "Roorkee", "Rudrapur"], "trai_weight": 0.011},
    "West Bengal": {"districts": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Kharagpur"], "trai_weight": 0.080},
    "Andaman & Nicobar": {"districts": ["Port Blair"], "trai_weight": 0.001},
    "Dadra & Nagar Haveli": {"districts": ["Silvassa"], "trai_weight": 0.001},
    "Daman & Diu": {"districts": ["Daman", "Diu"], "trai_weight": 0.001},
    "Lakshadweep": {"districts": ["Kavaratti"], "trai_weight": 0.0005},
    "Puducherry": {"districts": ["Puducherry City", "Karaikal"], "trai_weight": 0.0025}
}

# --- 3. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    .filter-card {
        background: white; padding: 2rem; border-radius: 15px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    .kpi-metric {
        background: white; padding: 1.5rem; border-radius: 12px;
        border-top: 5px solid #2563EB; text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    h1, h3 { color: #1E3A8A !important; font-family: 'Inter', sans-serif; font-weight: 800; }
    .stButton>button {
        background-color: #2563EB !important; color: white !important;
        border-radius: 8px; height: 3.5rem; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INPUT INTERFACE ---
st.title("🌐 Virtual Media Planner (IAMAI + TRAI + Comscore)")
st.markdown("##### Full-Stack Audience Sizing & Market Intelligence Engine")

with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("### 🗺️ Geography")
        # Multi-select for States/UTs
        sel_states = st.multiselect("Select States/UTs", sorted(list(INDIA_GEO_MASTER.keys())), default=["Maharashtra"])
        
        # Classification Dropdown
        market_type = st.selectbox("Market Classification", ["Urban", "Rural", "Overall"], index=2)

    with c2:
        st.markdown("### 🏘️ Granularity")
        # BARC Logic: Lock districts if Urban/Rural is selected
        is_disabled = True if market_type in ["Urban", "Rural"] else False
        
        # Dynamic district pool
        district_pool = []
        for s in sel_states:
            district_pool.extend(INDIA_GEO_MASTER[s]["districts"])
        district_pool = sorted(list(set(district_pool)))
        
        # District Select
        sel_districts = st.multiselect(
            "Select Districts (Overall only)", 
            options=district_pool,
            disabled=is_disabled,
            help="Districts are auto-selected based on Classification logic for Urban/Rural."
        )
        
        sel_gender = st.multiselect("Gender", ["Male", "Female"], default=["Male", "Female"])

    with c3:
        st.markdown("### 👤 Demographics")
        sel_age = st.multiselect("Age Cohorts", ["15-24", "25-34", "35-44", "45+"], default=["15-24", "25-34"])
        sel_nccs = st.multiselect("NCCS Segments", ["A", "B", "C", "D", "E"], default=["A", "B"])
    
    st.divider()
    calculate = st.button("Generate Unified Universe")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. TRIANGULATED CALCULATION ENGINE ---
def run_triangulation():
    # 2026 Baseline: 958M Active Internet Users (IAMAI Projections)
    TOTAL_INDIA_AIU = 958000 
    
    # 1. State/LSA Contribution (TRAI Wireless Broadband Weights)
    lsa_weight = sum([INDIA_GEO_MASTER[s]["trai_weight"] for s in sel_states])
    
    # 2. Classification Logic (IAMAI Urban/Rural Penetration)
    if market_type == "Urban": class_mult = 0.43
    elif market_type == "Rural": class_mult = 0.57
    else: class_mult = 1.0 # Overall
    
    # 3. District Granularity Factor
    granularity = 1.0
