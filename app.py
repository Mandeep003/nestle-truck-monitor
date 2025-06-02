import streamlit as st
import pandas as pd
from datetime import datetime
SCM_PASSWORD = "nestle123"

st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")

# Load CSV
@st.cache_data
def load_data():
    return pd.read_csv("trucks.csv")

# Save Data
def save_data(df):
    df.to_csv("trucks.csv", index=False)

# Title
st.title("🚛 Nestlé Truck Status Monitor")

# Login Section
st.sidebar.subheader("🔐 SCM Login")
password = st.sidebar.text_input("Enter SCM password", type="password")
is_scm = password == SCM_PASSWORD

# Load current data
df = load_data()

# If SCM Logged In
if is_scm:
    st.success("Logged in as SCM Staff ✅")
    
    with st.form("truck_form"):
        st.subheader("➕ Add or Update Truck Status")
        truck_no = st.text_input("Truck Number")
        phone = st.text_input("Driver Phone")
        status = st.selectbox("Status", ["Inside", "Ready to Leave"])
        submit = st.form_submit_button("Submit")

        if submit:
            entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Check if truck exists
            index = df[df["Truck Number"] == truck_no].index
            if len(index) > 0:
                df.loc[index[0], ["Driver Phone", "Entry Time", "Status"]] = [phone, entry_time, status]
                st.success("Truck updated successfully!")
            else:
                df.loc[len(df)] = [truck_no, phone, entry_time, status]
                st.success("Truck added successfully!")
            save_data(df)

# Everyone can view dashboard
st.subheader("📋 Current Truck Status")
st.dataframe(df, use_container_width=True)

