import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ----------------------------
# CONFIGURATION
# ----------------------------
SCM_PASSWORD = "scm2025"
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1W9LecXoIscTZ1okRPOe_gYUUN_-L8Jrvmgp8rU93Ma0/edit"

# ----------------------------
# GOOGLE SHEETS AUTH
# ----------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("gcreds.json", scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(GOOGLE_SHEET_URL)
worksheet = sheet.sheet1

# ----------------------------
# STREAMLIT SETUP
# ----------------------------
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚛 Nestlé Truck Monitoring System")

# ----------------------------
# SIDEBAR LOGIN
# ----------------------------
with st.sidebar:
    st.subheader("🔐 SCM Login")
    password = st.text_input("Enter SCM password", type="password")
    if st.button("Submit") and password == SCM_PASSWORD:
        st.session_state.logged_in = True

# ----------------------------
# DATA HANDLING
# ----------------------------
def fetch_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def add_or_update_entry(truck_no, driver_phone, status):
    df = fetch_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if truck_no in df["Truck Number"].values:
        row = df[df["Truck Number"] == truck_no].index[0] + 2  # +2 because gspread is 1-indexed and row 1 is header
        worksheet.update(f"B{row}:D{row}", [[driver_phone, status, now]])
    else:
        worksheet.append_row([truck_no, driver_phone, status, now])

# ----------------------------
# IF LOGGED IN
# ----------------------------
if st.session_state.get("logged_in", False):
    st.success("Logged in as SCM ✅")

    with st.form("entry_form"):
        st.subheader("➕ Add or Update Truck Entry")
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submitted = st.form_submit_button("Submit")

        if submitted and truck_no.strip() and phone.strip():
            add_or_update_entry(truck_no.strip(), phone.strip(), status)
            st.success(f"✅ Entry for {truck_no} saved.")
            st.experimental_rerun()

# ----------------------------
# LIVE TABLE VIEW
# ----------------------------
st.subheader("📋 Current Truck Status (Live View)")
data_df = fetch_data()
if data_df.empty:
    st.info("No truck entries yet.")
else:
    st.dataframe(data_df, use_container_width=True)
