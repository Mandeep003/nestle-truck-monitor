import streamlit as st
from pyairtable import Table
import os

# Load secrets from Streamlit Cloud environment
AIRTABLE_API_KEY = st.secrets["AIRTABLE_API_KEY"]
AIRTABLE_BASE_ID = st.secrets["AIRTABLE_BASE_ID"]
AIRTABLE_TABLE_NAME = st.secrets["AIRTABLE_TABLE_NAME"]

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)

def get_user_role(password):
    return {
        "master2025": "MasterUser",
        "scm2025": "SCM",
        "gate123": "Gate",
        "123": "Parking"
    }.get(password)

st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Monitoring System")

if "role" not in st.session_state:
    with st.form("login_form"):
        password = st.text_input("Enter your access password:", type="password")
        login_btn = st.form_submit_button("Submit")
    if not login_btn:
        st.stop()
    role = get_user_role(password)
    if not role:
        st.warning("Please enter a valid password.")
        st.stop()
    st.session_state.role = role
    st.success(f"Logged in as: {role}")
else:
    role = st.session_state.role
    st.success(f"Logged in as: {role}")

records = table.all()
df_data = []
for rec in records:
    fields = rec.get("fields", {})
    fields["RecordID"] = rec["id"]
    df_data.append(fields)

import pandas as pd
df = pd.DataFrame(df_data)
df = df[["Truck Number", "Driver Phone", "Entry Time", "Date", "Vendor / Material", "Status", "Updated By", "RecordID"]]
df_display = df.drop(columns=["RecordID"])

if role == "Gate":
    st.subheader("🛂 Gate Entry (Inside only)")
    with st.form("add_entry"):
        date = st.text_input("Entry Date (YYYY-MM-DD)")
        truck_number = st.text_input("Truck Number")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.text_input("Entry Time (HH:MM)")
        vendor_material = st.text_input("Vendor / Material")
        status = "Inside (🟡)"
        submitted = st.form_submit_button("Submit")
        if submitted:
            try:
                table.create({
                    "Date": date,
                    "Truck Number": truck_number,
                    "Driver Phone": driver_phone,
                    "Entry Time": entry_time,
                    "Vendor / Material": vendor_material,
                    "Status": status,
                    "Updated By": "Gate"
                })
                st.success("New truck entry added.")
                st.rerun()
            except:
                st.error("Failed to add entry.")

elif role == "SCM":
    st.subheader("🛠️ SCM - Status Update (for Gate Entries)")
    scm_entries = df[df["Updated By"] == "Gate"]
    for i, row in scm_entries.iterrows():
        st.markdown(f"*Truck:* {row['Truck Number']} | *Status:* {row['Status']}")
        status_option = st.selectbox(
            f"Update Status for {row['Truck Number']}",
            ["Inside (🟡)", "Ready to Leave (🟢)"],
            key=f"scm_select_{i}"
        )
        if st.button(f"Update {row['Truck Number']}", key=f"scm_btn_{i}"):
            try:
                table.update(row["RecordID"], {
                    "Status": status_option,
                    "Updated By": "SCM"
                })
                st.success("Status updated.")
                st.rerun()
            except:
                st.error("Update failed.")

elif role == "Parking":
    st.subheader("🚗 Parking Staff - Mark Trucks as Left")
    for i, row in df[df["Status"] != "Left (✅)"].iterrows():
        if st.button(f"Mark {row['Truck Number']} as Left", key=f"park_{i}"):
            try:
                table.update(row["RecordID"], {
                    "Status": "Left (✅)",
                    "Updated By": "Parking"
                })
                st.success("Truck marked as Left.")
                st.rerun()
            except:
                st.error("Failed to update status.")

elif role == "MasterUser":
    st.subheader("👑 Master Control Panel")
    for i, row in df.iterrows():
        st.markdown(f"**Truck:** {row['Truck Number']} | **Status:** {row['Status']}")
        with st.expander(f"Edit or Delete {row['Truck Number']}"):
            new_status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"], index=0, key=f"edit_status_{i}")
            new_date = st.text_input("Date", row["Date"], key=f"edit_date_{i}")
            new_time = st.text_input("Time", row["Entry Time"], key=f"edit_time_{i}")
            if st.button(f"Update {row['Truck Number']}", key=f"master_update_{i}"):
                try:
                    table.update(row["RecordID"], {
                        "Status": new_status,
                        "Date": new_date,
                        "Entry Time": new_time,
                        "Updated By": "MasterUser"
                    })
                    st.success("Updated.")
                    st.rerun()
                except:
                    st.error("Failed to update.")
            if st.button(f"❌ Delete {row['Truck Number']}", key=f"delete_{i}"):
                try:
                    table.delete(row["RecordID"])
                    st.warning(f"Deleted {row['Truck Number']}.")
                    st.rerun()
                except:
                    st.error("Delete failed.")

st.subheader("📋 Current Truck Status")
st.dataframe(df_display)
