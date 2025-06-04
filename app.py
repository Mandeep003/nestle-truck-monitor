import streamlit as st
import pandas as pd
from config import get_user_role

CSV_FILE = "trucks.csv"

def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# === Load Data
df = load_data()

# === Display Global Table (Always Visible)
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    styled_df = df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    )
    st.dataframe(styled_df, use_container_width=True)

# === Filter Search (optional)
with st.expander("🔍 Filter Trucks"):
    search = st.text_input("Search by Truck Number or Driver Phone")
    if search:
        result = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
        st.dataframe(result if not result.empty else "No matching entries.")

# === Sidebar Login
st.sidebar.title("🔐 Staff Login")
password = st.sidebar.text_input("Enter password", type="password")
login_btn = st.sidebar.button("Login")

role = None
if login_btn:
    role = get_user_role(password)

# === SCM: Full Edit Access
if role == "SCM":
    st.success("✅ Logged in as SCM")
    st.subheader("🛠️ Edit Full Truck Table")

    edited_df = st.data_editor(df, use_container_width=True, key="scm_editor")

    if st.button("💾 Save Changes (SCM)"):
        save_data(edited_df)
        st.success("Changes saved successfully.")

# === Parking: Only Status Column Editable
elif role == "Parking":
    st.success("✅ Logged in as Parking Staff")
    st.subheader("🛠️ Edit Truck Status Only")

    status_only_df = df[["Status"]].copy()
    updated_status = st.data_editor(status_only_df, use_container_width=True, key="parking_editor")

    if st.button("💾 Save Status Changes (Parking)"):
        df["Status"] = updated_status["Status"]
        save_data(df)
        st.success("Status updated successfully.")
