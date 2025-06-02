import streamlit as st
import requests
from datetime import datetime
import os

# Firebase config from secrets
FIREBASE_URL = st.secrets["FIREBASE_URL"]
API_KEY = st.secrets["API_KEY"]
SCM_PASSWORD = st.secrets["SCM_PASSWORD"]

# Helper: Get full path for REST API
def db_path():
    return f"{FIREBASE_URL}/trucks.json?auth={API_KEY}"

# Load truck entries
def load_data():
    res = requests.get(db_path())
    if res.status_code == 200 and res.json():
        data = res.json()
        return [{**v, "id": k} for k, v in data.items()]
    return []

# Save or update truck entry
def save_entry(truck_number, phone, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "Truck Number": truck_number,
        "Driver Phone": phone,
        "Entry Time": timestamp,
        "Status": status
    }
    res = requests.post(db_path(), json=payload)
    return res.ok

# Update a specific entry (used by SCM editor)
def update_entry(entry_id, data):
    url = f"{FIREBASE_URL}/trucks/{entry_id}.json?auth={API_KEY}"
    res = requests.put(url, json=data)
    return res.ok

# Page UI
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Status Monitor")

# Login
with st.sidebar.form("login_form"):
    st.subheader("🔐 SCM Login")
    password = st.text_input("Enter SCM password", type="password")
    login = st.form_submit_button("Login")

is_scm = password == SCM_PASSWORD if login else False
data = load_data()

# SCM section
if is_scm:
    st.success("Logged in as SCM ✅")
    st.subheader("➕ Add New Truck")

    with st.form("new_entry"):
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submit = st.form_submit_button("Submit")

        if submit:
            if truck_no and phone:
                if save_entry(truck_no, phone, status):
                    st.success("Truck entry saved.")
                    st.experimental_rerun()
                else:
                    st.error("Failed to save entry.")

    st.subheader("🛠️ Edit Existing Entries")

    for item in data:
        with st.expander(f"Truck: {item['Truck Number']}"):
            new_phone = st.text_input(f"Phone ({item['id']})", item["Driver Phone"], key=item["id"]+"phone")
            new_status = st.selectbox("Status", ["Inside", "Ready to Leave"], index=0 if item["Status"] == "Inside" else 1, key=item["id"]+"status")
            if st.button("💾 Update", key=item["id"]+"save"):
                item["Driver Phone"] = new_phone
                item["Status"] = new_status
                if update_entry(item["id"], item):
                    st.success("Updated successfully.")
                    st.experimental_rerun()

# Public View
st.subheader("📋 Live Truck Dashboard")
if data:
    st.dataframe([{k: v for k, v in i.items() if k != "id"} for i in data], use_container_width=True)
else:
    st.info("No entries yet.")
