import streamlit as st
import pandas as pd
import requests
import json
from config import get_user_role

# Airtable Config
AIRTABLE_BASE_ID = "appQDrGqz77AYH2yc"
AIRTABLE_TABLE_NAME = "Trucks"
AIRTABLE_API_KEY = "path6oZ4K8mOHMntI.f7acaf1894ca9fa28b224b9cf5a47ca1c0a65e283fbb91b99e2a0db093487479"
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

# UI Config
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# Login
if "role" not in st.session_state:
    with st.form("login_form"):
        password = st.text_input("Enter your access password:", type="password")
        submit = st.form_submit_button("Submit")
    if not submit:
        st.stop()
    role = get_user_role(password)
    if not role:
        st.warning("Please enter a valid password.")
        st.stop()
    st.session_state.role = role
st.success(f"Logged in as: {st.session_state.role}")
role = st.session_state.role

# Airtable interaction
def add_entry(data):
    try:
        response = requests.post(AIRTABLE_API_URL, headers=HEADERS, data=json.dumps({"fields": data}))
        response.raise_for_status()
        return True, "New truck entry added."
    except requests.exceptions.HTTPError as e:
        return False, str(e)

def get_entries():
    response = requests.get(AIRTABLE_API_URL, headers=HEADERS)
    records = response.json().get("records", [])
    return pd.DataFrame([rec["fields"] for rec in records])

def update_entry(record_id, updated_data):
    try:
        url = f"{AIRTABLE_API_URL}/{record_id}"
        response = requests.patch(url, headers=HEADERS, data=json.dumps({"fields": updated_data}))
        response.raise_for_status()
        return True
    except:
        return False

# Gate Entry
if role == "Gate":
    st.subheader("🛂 Gate Entry (Inside only)")
    with st.form("gate_form"):
        date = st.text_input("Entry Date (YYYY-MM-DD)")
        truck = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        time = st.text_input("Entry Time (HH:MM)")
        vendor = st.text_input("Vendor / Material")
        status = "Inside (🟡)"
        submitted = st.form_submit_button("Submit")
    if submitted:
        success, msg = add_entry({
            "Date": date,
            "Truck Number": truck,
            "Driver Phone": phone,
            "Entry Time": time,
            "Vendor / Material": vendor,
            "Status": status,
            "Updated By": "Gate"
        })
        if success:
            st.success(msg)
        else:
            st.error(msg)

# SCM - Edit Status Only
elif role == "SCM":
    st.subheader("🛠 SCM - Status Update (for Gate Entries)")
    df = get_entries()
    df = df[df["Updated By"] == "Gate"]
    for i, row in df.iterrows():
        st.markdown(f"*Truck:* {row['Truck Number']} | *Status:* {row['Status']}")
        new_status = st.selectbox(
            f"Update Status for {row['Truck Number']}",
            ["Inside (🟡)", "Ready to Leave (🟢)"],
            key=f"scm_status_{i}"
        )
        if st.button(f"Update {row['Truck Number']}", key=f"scm_btn_{i}"):
            record_id = row["id"] if "id" in row else None
            updated = update_entry(record_id, {"Status": new_status, "Updated By": "SCM"})
            if updated:
                st.success(f"Updated {row['Truck Number']}")
            else:
                st.error("Update failed.")

# Master User - Full Edit
elif role == "MasterUser":
    st.subheader("👑 Master Access - Edit All Fields")
    df = get_entries()
    for i, row in df.iterrows():
        with st.expander(f"Edit: {row.get('Truck Number', '')}"):
            new_date = st.text_input("Date", row.get("Date", ""), key=f"date_{i}")
            new_truck = st.text_input("Truck Number", row.get("Truck Number", ""), key=f"truck_{i}")
            new_phone = st.text_input("Driver Phone", row.get("Driver Phone", ""), key=f"phone_{i}")
            new_time = st.text_input("Entry Time", row.get("Entry Time", ""), key=f"time_{i}")
            new_vendor = st.text_input("Vendor / Material", row.get("Vendor / Material", ""), key=f"vendor_{i}")
            new_status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"],
                                      index=["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"].index(row.get("Status", "Inside (🟡)")),
                                      key=f"status_{i}")
            if st.button("Update Entry", key=f"master_btn_{i}"):
                record_id = row["id"] if "id" in row else None
                updated = update_entry(record_id, {
                    "Date": new_date,
                    "Truck Number": new_truck,
                    "Driver Phone": new_phone,
                    "Entry Time": new_time,
                    "Vendor / Material": new_vendor,
                    "Status": new_status,
                    "Updated By": "MasterUser"
                })
                if updated:
                    st.success("Entry updated successfully.")
                else:
                    st.error("Update failed.")

# Parking Role - Change to Left / Ready
elif role == "Parking":
    st.subheader("🚗 Parking - Update to 'Ready to Leave' or 'Left'")
    df = get_entries()
    for i, row in df.iterrows():
        st.markdown(f"*Truck:* {row['Truck Number']} | *Status:* {row['Status']}")
        if row.get("Status") != "Left (✅)":
            new_status = st.selectbox(
                f"New Status for {row['Truck Number']}",
                ["Ready to Leave (🟢)", "Left (✅)"],
                key=f"parking_status_{i}"
            )
            if st.button(f"Mark {row['Truck Number']}", key=f"parking_btn_{i}"):
                record_id = row["id"] if "id" in row else None
                updated = update_entry(record_id, {"Status": new_status, "Updated By": "Parking"})
                if updated:
                    st.success(f"Truck {row['Truck Number']} marked as {new_status}")
                else:
                    st.error("Update failed.")
        else:
            st.info(f"{row['Truck Number']} already marked as Left.")

# Viewer
st.subheader("📋 Current Truck Status")
df = get_entries()
if df.empty:
    st.info("No data available.")
else:
    st.dataframe(df.fillna(""), use_container_width=True)