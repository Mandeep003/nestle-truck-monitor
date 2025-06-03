import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Nestlé Truck-Monitor", layout="wide")

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gcreds.json", scope)
client = gspread.authorize(creds)

sheet_url = "https://docs.google.com/spreadsheets/d/1W9LecXoIscTZ1okRPOe_gYUUN_-L8Jrvmgp8rU93Ma0/edit"
spreadsheet = client.open_by_url(sheet_url)
worksheet = spreadsheet.sheet1

# --- SCM Password ---
st.sidebar.header("🔐 SCM Login")
password = st.sidebar.text_input("Enter SCM Password", type="password")
scm_logged_in = st.sidebar.button("Submit")

if scm_logged_in and password == "scm2025":
    st.success("Logged in as SCM Staff")
    # --- Add Truck Entry Form ---
    st.header("🚛 Add New Truck Entry")
    truck_number = st.text_input("Truck Number")
    driver_number = st.text_input("Driver Phone Number")
    entry_time = st.text_input("Entry Time (HH:MM format)")

    if st.button("Add Entry"):
        worksheet.append_row([truck_number, driver_number, entry_time, "Inside"])
        st.success("✅ Entry added successfully")

    # --- Edit Table View ---
    st.header("📋 Live Dashboard (Editable)")
    df = pd.DataFrame(worksheet.get_all_records())
    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Update Table"):
        worksheet.clear()
        worksheet.append_rows([edited_df.columns.values.tolist()] + edited_df.values.tolist())
        st.success("✅ Google Sheet updated successfully")

else:
    st.warning("Enter password to login as SCM.")
    st.header("📋 Live Dashboard (Read-Only)")
    try:
        df = pd.DataFrame(worksheet.get_all_records())
        st.dataframe(df)
    except Exception as e:
        st.error("Error loading data.")
        st.exception(e)
