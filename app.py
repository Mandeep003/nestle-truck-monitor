import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- Firebase Setup from secrets ---
FIREBASE_URL = st.secrets["FIREBASE_URL"]  # e.g. "https://your-project.firebaseio.com"

# --- Page Config ---
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Monitoring System")

# --- Login Form ---
with st.sidebar.form("login_form"):
    st.subheader("🔐 SCM Login")
    password = st.text_input("Enter SCM password", type="password")
    login_submit = st.form_submit_button("Submit")
    is_scm = password == "nestle123" if login_submit else False

# --- Firebase Helpers ---
def fetch_data():
    try:
        res = requests.get(f"{FIREBASE_URL}/trucks.json")
        st.write("🟢 GET status:", res.status_code)
        if res.status_code == 200 and res.json():
            raw = res.json()
            return [{"id": k, **v} for k, v in raw.items()]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    return []

def post_data(truck_data):
    try:
        res = requests.post(f"{FIREBASE_URL}/trucks.json", json=truck_data)
        st.write("🔁 POST status:", res.status_code)
        st.write("🔁 POST response:", res.text)
        return res.ok
    except Exception as e:
        st.error(f"Error posting data: {e}")
        return False

# --- SCM Dashboard (after login) ---
if is_scm:
    st.success("Logged in as SCM ✅")
    st.subheader("➕ Add or Update Truck Entry")

    with st.form("entry_form"):
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            st.write("🟢 Form submitted.")
            if truck_no.strip() and phone.strip():
                entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                truck_data = {
                    "Truck Number": truck_no,
                    "Driver Phone": phone,
                    "Status": status,
                    "Entry Time": entry_time
                }

                st.json(truck_data)
                result = post_data(truck_data)
                if result:
                    st.success("✅ Truck entry saved.")
                    st.rerun()
                else:
                    st.error("❌ Failed to save truck entry.")
            else:
                st.warning("Please enter both Truck Number and Phone.")

# --- Public View (everyone sees this) ---
st.subheader("📋 Current Truck Status (Live View)")
data = fetch_data()

if data:
    df = pd.DataFrame([{k: str(v) for k, v in row.items() if k != "id"} for row in data])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No truck entries yet.")
