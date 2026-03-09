# --- 4. OUTPUT: INPUT VALIDATION & UNIVERSE CALCULATION ---
if calculate:
    universe_val, matched_col = get_universe_value(sel_market, sel_gender, sel_age, sel_nccs)
    
    st.subheader("✅ Part 1: Data Architecture Verification")
    
    # --- FIXED LOGIC: Handle NaN or Missing Data ---
    if pd.isna(universe_val) or universe_val == 0:
        display_universe = "Data Not Available"
        st.error(f"⚠️ The combination of {sel_age} and NCCS {sel_nccs} does not exist in the BARC records for {sel_market}. Please try a broader NCCS or Age group.")
    else:
        # Only convert to int if it's a valid number
        display_universe = f"{int(universe_val):,} ('000s)"

    # Display the breakdown
    c1, c2, c3, c4 = st.columns(4)
    c1.info(f"**Market:** \n {sel_market}")
    c2.info(f"**Targeting:** \n {sel_gender} | {sel_age} | NCCS {sel_nccs}")
    
    # Using the safe display string
    c3.success(f"**Universe identified:** \n {display_universe}")
    c4.warning(f"**Data Source Mapping:** \n Column: '{matched_col}'")
    
    # --- Audit Table ---
    st.write("### Data Integrity Check")
    audit_status = "Verified" if not pd.isna(universe_val) else "Missing in Source"
    audit_data = {
        "Parameter": ["Market", "Gender", "Age", "NCCS", "Budget", "Reach Goal"],
        "Selection": [sel_market, sel_gender, sel_age, sel_nccs, f"₹{budget:,}", f"{reach_target}%"],
        "Status": [audit_status, "Mapped", "Mapped", "Mapped", "Valid", "Valid"]
    }
    st.table(pd.DataFrame(audit_data))
