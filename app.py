import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Firebase Config ---
FIREBASE_URL = st.secrets["FIREBASE_URL"]  # Add this to secrets.toml

# --- Page Config ---
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Monitoring System")

# --- Login Form ---
with st.sidebar.form("login_form"):
    st.subheader("🔐 SCM Login")
    password = st.text_input("Enter SCM password", type="password")
    login_submit = st.form_submit_button("Submit")
    is_scm = password == "nestle123" if login_submit else False

# --- Firebase Functions ---
def fetch_data():
    res = requests.get(f"{FIREBASE_URL}/trucks.json")
    if res.status_code == 200 and res.json():
        data = res.json()
        data_list = [{"id": k, **v} for k, v in data.items()]
        return data_list
    return []

def post_data(truck_data):
    requests.post(f"{FIREBASE_URL}/trucks.json", json=truck_data)

def update_data(entry_id, updated_data):
    requests.patch(f"{FIREBASE_URL}/trucks/{entry_id}.json", json=updated_data)

# --- SCM Section ---
if is_scm:
    st.success("Logged in as SCM ✅")
    st.subheader("➕ Add or Update Truck Entry")

    with st.form("entry_form"):
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submitted = st.form_submit_button("Submit")

        if submitted and truck_no.strip():
            entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing_data = fetch_data()

            existing = next((entry for entry in existing_data if entry["Truck Number"] == truck_no), None)

            new_data = {
                "Truck Number": truck_no,
                "Driver Phone": phone,
                "Status": status,
                "Entry Time": entry_time
            }

            if existing:
                update_data(existing["id"], new_data)
                st.success("Truck updated successfully.")
            else:
                post_data(new_data)
                st.success("Truck added successfully.")
            st.rerun()

# --- Display Live Table for All ---
st.subheader("📋 Current Truck Status (Live View)")

fetched_data = fetch_data()
if fetched_data:
    df = pd.DataFrame([{k: str(v) for k, v in entry.items() if k != "id"} for entry in fetched_data])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No truck entries yet.")
