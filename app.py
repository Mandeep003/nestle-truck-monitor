import streamlit as st
import pandas as pd
import datetime
from config import get_user_role

# File path for the CSV
CSV_FILE = "trucks.csv"

# Load or create the CSV
def load_data():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Truck Number", "Driver Phone", "Entry Time", "Status", "Updated By"])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# UI starts here
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# --- Session-based login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    with st.form("login_form"):
        password = st.text_input("Enter your access password:", type="password")
        login_submit = st.form_submit_button("Login")
        if login_submit:
            role = get_user_role(password)
            if role:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.success(f"Logged in as: {role}")
            else:
                st.warning("Invalid password.")
                st.stop()
    st.stop()

role = st.session_state.role
st.success(f"Logged in as: {role}")

# Load CSV data
df = load_data()

# ========== SCM UI ==========
if role == "SCM":
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
            df = load_data()  # reload after saving

# ========== Viewer UI ==========
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    if role == "SCM":
        st.write("✏️ Click to update status inline:")
        for idx, row in df.iterrows():
            cols = st.columns([2, 2, 2, 3, 2])
            cols[0].write(row["Truck Number"])
            cols[1].write(row["Driver Phone"])
            cols[2].write(row["Entry Time"])
            new_status = cols[3].selectbox(
                "", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"],
                index=["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"].index(row["Status"]),
                key=f"status_{idx}"
            )
            if cols[4].button("Update", key=f"update_{idx}"):
                df.at[idx, "Status"] = new_status
                df.at[idx, "Updated By"] = "SCM"
                save_data(df)
                st.success(f"Updated status for {row['Truck Number']}")

    # Styled full table display (read-only for non-SCM)
    styled_df = df.style.applymap(
        lambda val: 'background-color: #FFF176' if "🟡" in val else 
                    'background-color: #81C784' if "🟢" in val else
                    'background-color: #B2DFDB' if "✅" in val else '',
        subset=["Status"]
    )
    st.dataframe(styled_df)

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")
