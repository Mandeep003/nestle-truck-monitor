import streamlit as st
import pandas as pd
import datetime
from config import get_user_role

# === File path ===
CSV_FILE = "trucks.csv"

# === Load or create CSV ===
def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# === Page config ===
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# === Load truck data
df = load_data()

# ========== GLOBAL DASHBOARD (Visible to All) ==========
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    styled_df = df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")

# ========== SIDEBAR LOGIN ==========
st.sidebar.title("🔐 Staff Login")
password = st.sidebar.text_input("Enter your access password:", type="password")
login_button = st.sidebar.button("Submit")

role = get_user_role(password) if login_button else None

# ========== SCM FORM UI ========== 
if role == "SCM":
    st.sidebar.success("Logged in as: SCM Staff")
    st.subheader("📥 Add / Update Truck Status")

    with st.form("truck_form"):
        truck_number = st.text_input("Truck Number (e.g. DL01AB1234)")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time", value=datetime.datetime.now().time())
        status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_entry = {
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": entry_time.strftime("%H:%M"),
                "Status": status,
                "Updated By": "SCM"
            }

            existing_index = df[df["Truck Number"] == truck_number].index
            if not existing_index.empty:
                df.loc[existing_index[0]] = new_entry
                st.info("Truck entry updated.")
            else:
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                st.success("New truck entry added.")

            save_data(df)
            st.experimental_rerun()
