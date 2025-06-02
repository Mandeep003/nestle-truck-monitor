import streamlit as st
import requests
from datetime import datetime

# Load credentials
FIREBASE_URL = st.secrets["FIREBASE_URL"]
SCM_PASSWORD = st.secrets["SCM_PASSWORD"]

# Firebase paths
def db_path():
    return f"{FIREBASE_URL}/trucks.json"

def entry_path(entry_id):
    return f"{FIREBASE_URL}/trucks/{entry_id}.json"

# Firebase operations
def load_data():
    res = requests.get(db_path())
    st.write("GET status:", res.status_code)
    if res.status_code == 200 and res.json():
        data = res.json()
        return [{**v, "id": k} for k, v in data.items()]
    return []

def save_entry(truck_number, phone, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "Truck Number": truck_number,
        "Driver Phone": phone,
        "Entry Time": timestamp,
        "Status": status
    }
    res = requests.post(db_path(), json=payload)
    st.write("POST status:", res.status_code)
    st.write("POST response:", res.text)
    return res.ok

def update_entry(entry_id, data):
    res = requests.put(entry_path(entry_id), json=data)
    return res.ok

# Streamlit UI
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Status Monitor")

# --- Persistent SCM login ---
if "is_scm" not in st.session_state:
    st.session_state["is_scm"] = False

with st.sidebar.form("login_form"):
    st.subheader("🔐 SCM Login")
    password = st.text_input("Enter SCM password", type="password")
    login = st.form_submit_button("Login")

    if login:
        if password == SCM_PASSWORD:
            st.session_state["is_scm"] = True
            st.success("Logged in successfully.")
            st.experimental_rerun()
        else:
            st.error("Incorrect password.")

is_scm = st.session_state["is_scm"]
data = load_data()

# --- SCM dashboard ---
if is_scm:
    st.success("Logged in as SCM ✅")
    st.subheader("➕ Add New Truck Entry")

    with st.form("add_truck"):
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submit = st.form_submit_button("Submit")

        if submit:
            if truck_no and phone:
                result = save_entry(truck_no, phone, status)
                st.write("Save result:", result)
                if result:
                    st.success("Truck entry saved.")
                    st.experimental_rerun()
                else:
                    st.error("❌ Failed to save truck entry.")
            else:
                st.warning("Please fill both Truck Number and Phone.")

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

# --- Public View ---
st.subheader("📋 Live Truck Dashboard")
if data:
    st.dataframe([{k: v for k, v in i.items() if k != "id"} for i in data], use_container_width=True)
else:
    st.info("No entries yet.")
