import streamlit as st 
from pyairtable import Table
import os
from config import get_user_role
import pandas as pd

# Load Airtable API credentials
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Airtable connection
airtable = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

# Page config
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Monitoring System")

# Session login
if "role" not in st.session_state:
    with st.form("login"):
        password = st.text_input("Enter your access password:", type="password")
        submitted = st.form_submit_button("Submit")
        if submitted:
            role = get_user_role(password)
            if role:
                st.session_state.role = role
                st.success(f"Logged in as: {role}")
            else:
                st.warning("Invalid password.")
                st.stop()
        else:
            st.stop()

role = st.session_state.role
st.success(f"Logged in as: {role}")

# Airtable functions
def load_data():
    return airtable.all()

def add_entry(entry_data):
    required_fields = ["Truck Number", "Driver Phone", "Entry Time", "Date", "Vendor / Material", "Status", "Updated By"]
    if any(not entry_data.get(field) for field in required_fields):
        return False
    airtable.create(entry_data)
    return True

def update_entry_status(record_id, new_status):
    try:
        airtable.update(record_id, {"Status": new_status, "Updated By": role})
        return True
    except:
        return False

def delete_entry(record_id):
    try:
        airtable.delete(record_id)
        return True
    except:
        return False

# Gate Entry Form
if role == "Gate":
    st.subheader("🛃 Gate Entry (Inside only)")
    with st.form("gate_form"):
        date = st.text_input("Entry Date (YYYY-MM-DD)")
        truck = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        entry_time = st.text_input("Entry Time (HH:MM)")
        vendor = st.text_input("Vendor / Material in Truck")
        status = "Inside (🟡)"
        submit = st.form_submit_button("Submit")
        if submit:
            entry = {
                "Date": date.strip(),
                "Truck Number": truck.strip(),
                "Driver Phone": phone.strip(),
                "Entry Time": entry_time.strip(),
                "Vendor / Material": vendor.strip(),
                "Status": status,
                "Updated By": role
            }
            if add_entry(entry):
                st.success("Truck entry added.")
                st.rerun()
            else:
                st.error("Failed to add entry. All fields are required.")

# SCM Section
elif role == "SCM":
    st.subheader("🛠 SCM - Status Update (for Gate Entries)")
    records = load_data()
    for i, record in enumerate(records):
        fields = record["fields"]
        if fields.get("Updated By") == "Gate":
            truck = fields.get("Truck Number", "Unknown")
            current_status = fields.get("Status", "")
            st.markdown(f"**Truck:** {truck} | *Status:* {current_status}")
            new_status = st.selectbox(f"Update Status for {truck}", ["Inside (🟡)", "Ready to Leave (🟢)"], key=f"{truck}_{i}")
            if st.button(f"Update {truck}", key=f"update_{i}"):
                if update_entry_status(record["id"], new_status):
                    st.success("Status updated.")
                    st.rerun()
                else:
                    st.error("Update failed.")

# Parking Section
elif role == "Parking":
    st.subheader("🚗 Parking - Mark Trucks as Left")
    records = load_data()
    for i, record in enumerate(records):
        fields = record["fields"]
        truck = fields.get("Truck Number", "")
        status = fields.get("Status", "")
        if status != "Left (✅)":
            st.markdown(f"**Truck:** {truck} | *Current:* {status}")
            new_status = st.selectbox(f"Set Status for {truck}", ["Ready to Leave (🟢)", "Left (✅)"], key=f"{truck}_p_{i}")
            if st.button(f"Update {truck}", key=f"update_p_{i}"):
                if update_entry_status(record["id"], new_status):
                    st.success("Status updated.")
                    st.rerun()
                else:
                    st.error("Update failed.")

# MasterUser Full Access
elif role == "MasterUser":
    st.subheader("🧠 MasterUser: Full Control")
    with st.expander("➕ Add New Entry"):
        with st.form("master_add"):
            date = st.text_input("Date")
            truck = st.text_input("Truck Number")
            phone = st.text_input("Driver Phone")
            entry_time = st.text_input("Entry Time (HH:MM)")
            vendor = st.text_input("Vendor / Material")
            status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"])
            submit = st.form_submit_button("Add Entry")
            if submit:
                entry = {
                    "Date": date.strip(),
                    "Truck Number": truck.strip(),
                    "Driver Phone": phone.strip(),
                    "Entry Time": entry_time.strip(),
                    "Vendor / Material": vendor.strip(),
                    "Status": status,
                    "Updated By": role
                }
                if add_entry(entry):
                    st.success("Entry added.")
                    st.rerun()
                else:
                    st.error("All fields required.")

    st.subheader("📋 Current Truck Status")
    records = load_data()
    for i, record in enumerate(records):
        fields = record["fields"]
        truck = fields.get("Truck Number", "Unknown")
        current_status = fields.get("Status", "")
        st.markdown(f"**Truck:** {truck} | *Status:* {current_status}")
        new_status = st.selectbox(f"Change Status for {truck}", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"], key=f"{record['id']}_m")
        if st.button(f"Update Status: {truck}", key=f"update_m_{i}"):
            if update_entry_status(record["id"], new_status):
                st.success("Status updated.")
                st.rerun()
            else:
                st.error("Failed.")
        if st.button(f"🗑 Delete {truck}", key=f"delete_{i}"):
            if delete_entry(record["id"]):
                st.success("Deleted successfully.")
                st.rerun()
            else:
                st.error("Deletion failed.")

    # ✅ Delete All Left Trucks Button
    if st.button("🧹 Delete All 'Left (✅)' Trucks"):
        deleted = 0
        for record in records:
            if record["fields"].get("Status") == "Left (✅)":
                if delete_entry(record["id"]):
                    deleted += 1
        st.success(f"Deleted {deleted} trucks marked as 'Left (✅)'")
        st.rerun()

# View for All
st.subheader("📄 Current Truck Status")
records = load_data()
if not records:
    st.info("No entries yet.")
else:
    df = []
    for record in records:
        fields = record["fields"]
        df.append({
            "Truck Number": fields.get("Truck Number", "").strip(),
            "Driver Phone": fields.get("Driver Phone", "").strip(),
            "Entry Time": fields.get("Entry Time", "").strip(),
            "Date": fields.get("Date", "").strip(),
            "Vendor / Material": fields.get("Vendor / Material", "").strip(),
            "Status": fields.get("Status", "").strip(),
            "Updated By": fields.get("Updated By", "").strip()
        })
    df = pd.DataFrame(df)
    df = df.fillna("").sort_values(by="Date", ascending=False).reset_index(drop=True)
    st.dataframe(df)
