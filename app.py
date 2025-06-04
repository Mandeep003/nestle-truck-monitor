import streamlit as st
import pandas as pd
import datetime
from config import get_user_role

# File path for the CSV
CSV_FILE = "trucks.csv"

# Load or create the CSV
def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# UI setup
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# === Global View (Everyone Sees This First) ===
df = load_data()
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

# === Login Section ===
st.sidebar.title("🔐 Staff Login")
password = st.sidebar.text_input("Enter your access password:", type="password")
login_button = st.sidebar.button("Submit")

role = get_user_role(password) if login_button else None

# === SCM UI ===
if role == "SCM":
    st.sidebar.success("Logged in as: SCM Staff")

    st.subheader("🛠️ Edit Full Truck Table (SCM Only)")
    editable_df = st.data_editor(df, use_container_width=True, key="scm_edit")

    if st.button("💾 Save All Changes (SCM)"):
        save_data(editable_df)
        st.success("Changes saved successfully.")
        st.experimental_rerun()

# === Parking Staff UI ===
elif role == "Parking":
    st.sidebar.success("Logged in as: Parking Staff")

    st.subheader("🛠️ Update Truck Status Only (Parking Staff)")

    editable_status_df = df.copy()
    editable_status_df["Status"] = st.data_editor(df["Status"], use_container_width=True, key="parking_edit")

    if st.button("💾 Save Status Changes (Parking)"):
        df["Status"] = editable_status_df["Status"]
        save_data(df)
        st.success("Status updated successfully.")
        st.experimental_rerun()
