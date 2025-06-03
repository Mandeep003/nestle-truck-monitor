import streamlit as st
import pandas as pd
import datetime
from config import get_user_role

# CSV path
CSV_FILE = "trucks.csv"

# Load and Save
def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Streamlit config
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# Login Section
st.info("🔒 SCM editors can log in to update truck status.")
password = st.text_input("Enter SCM password to enable editing (optional):", type="password")
login_btn = st.button("Login as SCM")

role = get_user_role(password) if login_btn else "Viewer"

if role == "Viewer":
    st.success("Viewer mode: Read-only access enabled.")
elif role == "SCM":
    st.success("SCM mode: Editing access enabled.")

# Load data
df = load_data()

# ==================== SCM MODE ====================
if role == "SCM":
    st.subheader("📝 Edit Truck Data")

    # Allow editing the table directly
    edited_df = st.data_editor(df, use_container_width=True, key="edit_table")

    if st.button("Save Changes"):
        # Ask if user wants to auto-remove trucks marked as Left
        left_trucks = edited_df[edited_df["Status"] == "Left (✅)"]

        if not left_trucks.empty:
            confirm_removal = st.checkbox("Remove trucks marked as 'Left (✅)'?", value=True)
            if confirm_removal:
                st.warning(f"{len(left_trucks)} trucks marked 'Left (✅)' will be removed.")
                if st.button("Confirm Removal"):
                    edited_df = edited_df[edited_df["Status"] != "Left (✅)"]
                    st.success(f"Removed {len(left_trucks)} truck(s).")

        save_data(edited_df)
        st.success("Changes saved.")

# ==================== ALL USERS ====================
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    st.dataframe(df.style.applymap(
        lambda val: 'background-color: #FFF176' if "🟡" in val else
                    'background-color: #81C784' if "🟢" in val else
                    'background-color: #B2DFDB' if "✅" in val else '',
        subset=["Status"]
    ))

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")
