import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

# Title
st.set_page_config(page_title="🚛 Nestlé Truck Monitoring Dashboard", layout="wide")
st.title("🚛 Nestlé Truck Monitoring Dashboard")

# Authenticate with Google Sheets using correct scope
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# Access the Google Sheet
sheet_url = st.secrets["GOOGLE_SHEET_URL"]
sheet = client.open_by_url(sheet_url)

# Display sheet names
worksheet_names = [ws.title for ws in sheet.worksheets()]
selected_sheet = st.selectbox("Select a sheet to view:", worksheet_names)

# Load selected worksheet into a dataframe
worksheet = sheet.worksheet(selected_sheet)
data = pd.DataFrame(worksheet.get_all_records())

# Display table
st.subheader(f"📄 Data from Sheet: {selected_sheet}")
st.dataframe(data, use_container_width=True)

# Optional: Basic filtering or other features
with st.expander("🔍 Filter Data (Optional)"):
    search_text = st.text_input("Search for a truck number or driver:")
    if search_text:
        filtered_data = data[
            data.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)
        ]
        st.dataframe(filtered_data, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Built by Mandeep Bawa | Nestlé SCM Intern")
