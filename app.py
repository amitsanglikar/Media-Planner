# --- 5. Budget Allocation Logic ---
st.subheader("💰 Recommended Budget Allocation")

# Inputs for budget
total_budget = st.number_input("Enter Total Campaign Budget (INR)", min_value=100000, value=1000000, step=50000)

# Allocation Logic based on "Stage"
# Awareness: 40% | Consideration: 40% | Conversion: 20% (Standard 2026 India Mix)
aware_amt = total_budget * 0.40
consid_amt = total_budget * 0.40
conver_amt = total_budget * 0.20

b_col1, b_col2, b_col3 = st.columns(3)
with b_col1:
    st.metric("Awareness (TOFU)", f"₹{int(aware_amt):,}")
    st.caption("Focus: YouTube, Meta Reach, JioCinema")
with b_col2:
    st.metric("Consideration (MOFU)", f"₹{int(consid_amt):,}")
    st.caption("Focus: Influencers, OTT, Retargeting")
with b_col3:
    st.metric("Conversion (BOFU)", f"₹{int(conver_amt):,}")
    st.caption("Focus: Google Search, WhatsApp, Meta CAPI")

# Visualization: Allocation Pie Chart
import plotly.express as px
fig = px.pie(
    values=[aware_amt, consid_amt, conver_amt], 
    names=['Awareness', 'Consideration', 'Conversion'],
    color_discrete_sequence=px.colors.sequential.RdBu,
    hole=0.4
)
st.plotly_chart(fig, use_container_width=True)
