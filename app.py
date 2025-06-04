import streamlit as st
import pandas as pd
from config import get_user_role

CSV_FILE = "trucks.csv"

def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# Load Data
df = load_data()

# ========== GLOBAL TABLE (Always Visible) ==========
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    styled_df = df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

# Optional Filter
with st.expander("🔍 Filter Trucks"):
    search = st.text_input("Search by Truck Number or Driver Phone")
    if search:
        result = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
        st.dataframe(result if not result.empty else "No matching entries.")

# ========== SIDEBAR LOGIN ==========
st.sidebar.title("🔐 Staff Login")
password = st.sidebar.text_input("Enter password", type="password")
login_btn = st.sidebar.button("Submit")

role = None
if login_btn:
    role = get_user_role(password)

# ========== SCM STAFF ==========
if role == "SCM":
    st.success("✅ Logged in as SCM Staff")

    # Add New Entry Form
    st.subheader("➕ Add New Truck Entry")
    with st.form("add_truck_form"):
        truck_number = st.text_input("Truck Number")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time")
        status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"])
        submitted = st.form_submit_button("Add Entry")

        if submitted:
            new_row = {
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": entry_time.strftime("%H:%M"),
                "Status": status,
                "Updated By": "SCM"
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("New truck entry added successfully.")

    # Edit Existing Table
    st.subheader("🛠️ Edit Full Truck Table")
    edited_df = st.data_editor(df, use_container_width=True, key="scm_editor")

    if st.button("💾 Save All Changes"):
        save_data(edited_df)
        st.success("Changes saved successfully.")

# ========== PARKING STAFF ==========
elif role == "Parking":
    st.success("✅ Logged in as Parking Staff")

    st.subheader("🛠️ Edit Truck Status Only")
    status_only_df = df[["Status"]].copy()
    updated_status = st.data_editor(status_only_df, use_container_width=True, key="parking_editor")

    if st.button("💾 Save Status Changes (Parking)"):
        df["Status"] = updated_status["Status"]
        save_data(df)
        st.success("Status updated successfully.")
