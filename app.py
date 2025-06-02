import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Constants ---
CSV_FILE = "trucks.csv"
SCM_PASSWORD = "nestle123"  # hardcoded for now

# --- Load/Save Data ---
def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status"])
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- Page Setup ---
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck-Monitoring System")

# --- Login Form ---
with st.sidebar.form("login_form"):
    st.subheader("🔐 SCM Login")
    entered_password = st.text_input("Enter SCM password", type="password")
    login_submit = st.form_submit_button("Login")

is_scm = (entered_password == SCM_PASSWORD) if login_submit else False

# --- Load and Display Data ---
df = load_data()

# --- SCM Add or Edit Entries ---
if is_scm:
    st.success("Logged in as SCM ✅")
    st.subheader("➕ Add or Edit Truck Entry")

    with st.form("edit_form"):
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submitted = st.form_submit_button("Submit")

        if submitted and truck_no.strip():
            entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            match = df["Truck Number"] == truck_no
            if match.any():
                df.loc[match, ["Driver Phone", "Status", "Entry Time"]] = [phone, status, entry_time]
                st.success("Truck updated successfully.")
            else:
                df.loc[len(df.index)] = [truck_no, phone, entry_time, status]
                st.success("Truck added successfully.")
            save_data(df)

    st.subheader("🛠️ Edit Existing Entries")
    edited_df = st.data_editor(df, num_rows="dynamic", key="editable")
    if st.button("💾 Save Changes"):
        save_data(edited_df)
        st.success("Changes saved successfully.")
        st.experimental_rerun()

# --- View for Everyone ---
st.subheader("📋 Current Truck Status (Live View)")
st.dataframe(df, use_container_width=True)
