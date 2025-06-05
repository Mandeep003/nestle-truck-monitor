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
        df = pd.DataFrame(columns=[
            "Date", "Truck Number", "Driver Phone", "Entry Time",
            "Vendor / Material", "Status", "Updated By"
        ])
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# UI starts here
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# ===== Login with Session State + Submit Button =====
if "role" not in st.session_state:
    with st.form("login_form"):
        password = st.text_input("Enter your access password:", type="password")
        login_btn = st.form_submit_button("Submit")
    if not login_btn:
        st.stop()
    role = get_user_role(password)
    if not role:
        st.warning("Please enter a valid password.")
        st.stop()
    st.session_state.role = role
    st.success(f"Logged in as: {role}")
else:
    role = st.session_state.role
    st.success(f"Logged in as: {role}")

# Load CSV data
df = load_data()

# ========== SCM and Gate Staff Shared Logic ==========
if role in ["SCM", "Gate"]:
    st.subheader("📥 Add / Update Truck Status")

    with st.form("truck_form"):
        truck_number = st.text_input("Truck Number (e.g. DL01AB1234)")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time", value=datetime.datetime.now().time())
        vendor_material = st.text_input("Vendor / Material in Truck")

        # SCM has full access, Gate only partial
        if role == "SCM":
            status_options = ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"]
        else:
            status_options = ["Inside (🟡)", "Left (✅)"]

        status = st.selectbox("Status", status_options)

        submitted = st.form_submit_button("Submit")

        if submitted:
            new_entry = {
                "Date": datetime.date.today().strftime("%Y-%m-%d"),
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": entry_time.strftime("%H:%M"),
                "Vendor / Material": vendor_material,
                "Status": status,
                "Updated By": role
            }

            existing_index = df[df["Truck Number"] == truck_number].index

            if not existing_index.empty:
                df.loc[existing_index[0]] = new_entry
                st.info("Truck entry updated.")
            else:
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                st.success("New truck entry added.")

            save_data(df)
            df = load_data()

    # ========= Inline Status Editing =========
    st.subheader("✏️ Modify Truck Status")
    for idx, row in df.iterrows():
        st.markdown(f"**Truck Number:** {row['Truck Number']} | **Current Status:** {row['Status']}")

        if role == "SCM":
            status_options = ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"]
        else:  # Gate
            status_options = ["Inside (🟡)", "Left (✅)"]

        new_status = st.selectbox(
            f"Change Status for {row['Truck Number']}",
            status_options,
            index=status_options.index(row["Status"]) if row["Status"] in status_options else 0,
            key=f"status_select_{idx}"
        )
        if st.button(f"Update Status for {row['Truck Number']}", key=f"update_button_{idx}"):
            df.at[idx, "Status"] = new_status
            df.at[idx, "Updated By"] = role
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
    st.dataframe(df.style.applymap(
        lambda val: 'background-color: #797979' if "🟡" in val else 
                    'background-color: #81C784' if "🟢" in val else
                    'background-color: #797979' if "✅" in val else '',
        subset=["Status"]
    ))

    with st.expander("🔍 Filter Options", expanded=False):
        search_truck = st.text_input("Search by Truck Number")
        if search_truck:
            filtered_df = df[df["Truck Number"].str.contains(search_truck, case=False)]
            st.dataframe(filtered_df if not filtered_df.empty else "No matching trucks.")
