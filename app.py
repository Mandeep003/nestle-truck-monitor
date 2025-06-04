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

# === Global view (no login) ===
df = load_data()
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    st.dataframe(df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    ))

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
    st.subheader("🟧 Update Truck Status (Parking Staff Only)")
    
    # Create a new DataFrame with only Status editable
    editable_df = df.copy()
    editable_df["Status"] = st.data_editor(df["Status"], use_container_width=True, key="parking_edit")

    if st.button("Save Status Changes"):
        df["Status"] = editable_df["Status"]
        save_data(df)
        st.success("Status updated.")

# === SCM Full Access ===
elif role == "SCM":
    st.sidebar.success("Logged in as: SCM Staff")
    st.subheader("🟩 Edit Full Truck Data (SCM Only)")

    editable_df = st.data_editor(df, use_container_width=True, key="scm_edit")

    if st.button("Save All Changes"):
        save_data(editable_df)
        st.success("All changes saved.")