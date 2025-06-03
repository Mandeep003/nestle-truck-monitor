import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")

# Title
st.title("🚛 Nestlé Truck Monitoring Dashboard")

# Load credentials and authorize
credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = gspread.authorize(credentials)

# Access the Google Sheet
sheet_url = st.secrets["GOOGLE_SHEET_URL"]
sheet = client.open_by_url(sheet_url)

# Display sheet names
worksheet_names = [ws.title for ws in sheet.worksheets()]
selected_ws = st.sidebar.selectbox("Select a worksheet to view/edit:", worksheet_names)
worksheet = sheet.worksheet(selected_ws)

# Load sheet data into DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Display DataFrame
st.subheader(f"📄 Data from: {selected_ws}")
st.dataframe(df)

# Optional: Basic stats or filters
if not df.empty:
    st.markdown(f"**Total Rows:** {len(df)}")
    if "Status" in df.columns:
        st.markdown("**Status Breakdown:**")
        st.write(df["Status"].value_counts())

# Add new entry (SCM team can use this)
st.subheader("➕ Add New Entry")
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    truck_no = col1.text_input("Truck Number")
    driver_contact = col2.text_input("Driver Contact")
    status = st.selectbox("Status", ["Inside", "Ready to Leave", "Dispatched"])
    submit = st.form_submit_button("Submit")

    if submit:
        worksheet.append_row([truck_no, driver_contact, status])
        st.success("Entry added successfully. Please refresh to see updates.")

# Footer
st.markdown("---")
st.caption("Built for Nestlé SCM monitoring | Powered by Streamlit + Google Sheets")
