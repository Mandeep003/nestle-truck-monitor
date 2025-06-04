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

# Login with submit button
with st.form("login_form"):
    password = st.text_input("Enter your access password:", type="password")
    login_submit = st.form_submit_button("Login")

if not login_submit:
    st.stop()

role = get_user_role(password)

if not role:
    st.warning("Invalid password. Please try again.")
    st.stop()

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
            df = load_data()  # reload after save

    # ========= Inline Status Editing Below =========
    st.subheader("✏️ Modify Truck Status")
    for idx, row in df.iterrows():
        st.markdown(f"**Truck Number:** {row['Truck Number']} | **Current Status:** {row['Status']}")
        new_status = st.selectbox(
            f"Change Status for {row['Truck Number']}",
            ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"],
            index=["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"].index(row["Status"]),
            key=f"status_select_{idx}"
        )
        if st.button(f"Update Status for {row['Truck Number']}", key=f"update_button_{idx}"):
            df.at[idx, "Status"] = new_status
            df.at[idx, "Updated By"] = "SCM"
            save_data(df)
            st.success(f"Updated status for Truck {row['Truck Number']}")
            st.rerun()

# ========== Parking UI ==========
elif role == "Parking":
    st.subheader("🚗 Update Trucks to 'Left (✅)' Only")

    for idx, row in df.iterrows():
        st.markdown(f"**Truck Number:** {row['Truck Number']} | Current Status: {row['Status']}")
        
        if row["Status"] != "Left (✅)":
            selected_status = st.selectbox(
                f"Set Status for {row['Truck Number']}",
                ["Left (✅)"],
                key=f"parking_select_{idx}"
            )
            if st.button(f"Mark as Left for {row['Truck Number']}", key=f"parking_button_{idx}"):
                df.at[idx, "Status"] = selected_status
                df.at[idx, "Updated By"] = "Parking"
                save_data(df)
                st.success(f"Truck {row['Truck Number']} marked as Left.")
                st.rerun()
        else:
            st.info("Already marked as Left ✅")

# ========== Viewer UI ==========
st.subheader("📋 Current Truck Status")

if df.empty:
    st.info("No truck data available yet.")
else:
    # Only green color for "Ready to Leave"
    styled_df = df.style.applymap(
        lambda val: 'background-color: #81C784' if "🟢" in val else '',
        subset=["Status"]
    )

    st.dataframe(styled_df)

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")
