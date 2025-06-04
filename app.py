import streamlit as st
import pandas as pd
import datetime
from config import get_user_role

# === File path ===
CSV_FILE = "trucks.csv"

# === Data loading/saving ===
def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# === Page setup ===
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# === Load data
df = load_data()

# === Global view (no login) ===
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    styled_df = df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")

# === Side login ===
st.sidebar.title("🔐 Staff Login")
password = st.sidebar.text_input("Enter Password", type="password")
login_button = st.sidebar.button("Submit")

role = get_user_role(password) if login_button else None

# === Parking Staff Access ===
if role == "Parking":
    st.sidebar.success("Logged in as: Parking Staff")
    st.subheader("🟧 Update Truck Status Only (Parking Staff)")

    editable_status_df = df.copy()
    editable_status_df["Status"] = st.data_editor(
        df["Status"],
        use_container_width=True,
        key="parking_editor"
    )

    if st.button("Save Status Changes"):
        df["Status"] = editable_status_df["Status"]
        save_data(df)
        st.success("Status updated.")
        st.experimental_rerun()

# === SCM Staff Access ===
elif role == "SCM":
    st.sidebar.success("Logged in as: SCM Staff")

    # Add new truck entry
    st.subheader("➕ Add New Truck Entry")
    with st.form("add_form"):
        truck_number = st.text_input("Truck Number")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time")
        status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"])
        submit = st.form_submit_button("Add Entry")

        if submit:
            new_row = {
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": entry_time.strftime("%H:%M"),
                "Status": status,
                "Updated By": "SCM"
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("New truck entry added.")
            st.experimental_rerun()

    # Full table edit
    st.subheader("🟩 Edit Full Truck Table (SCM Only)")
    edited_df = st.data_editor(df, use_container_width=True, key="scm_editor")

    if st.button("Save All Changes"):
        save_data(edited_df)
        st.success("Changes saved.")
        st.experimental_rerun()
