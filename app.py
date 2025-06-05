import streamlit as st
import pandas as pd
import datetime
import pytz
from config import get_user_role

# File path
CSV_FILE = "trucks.csv"

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

def format_entry_time(entry_time):
    local_tz = pytz.timezone("Asia/Kolkata")
    entry_dt = datetime.datetime.combine(datetime.date.today(), entry_time)
    entry_local = local_tz.localize(entry_dt)
    return entry_local.strftime("%H:%M")

# UI
st.set_page_config(page_title="Nestlé Truck Monitor", layout="wide")
st.title("🚚 Nestlé Truck Monitoring System")

# ===== Login =====
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

df = load_data()

# ========== MasterUser ==========
if role == "MasterUser":
    st.subheader("🛠 MasterUser: Add / Edit Any Entry")

    with st.form("master_form"):
        truck_number = st.text_input("Truck Number")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time", value=datetime.datetime.now().time())
        vendor_material = st.text_input("Vendor / Material in Truck")
        status = st.selectbox("Status", ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"])
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_entry = {
                "Date": datetime.date.today().strftime("%Y-%m-%d"),
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": format_entry_time(entry_time),
                "Vendor / Material": vendor_material,
                "Status": status,
                "Updated By": "MasterUser"
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

    for idx, row in df.iterrows():
        with st.expander(f"✏️ Edit: {row['Truck Number']}"):
            truck_number = st.text_input("Truck Number", row["Truck Number"], key=f"tn{idx}")
            driver_phone = st.text_input("Driver Phone", row["Driver Phone"], key=f"ph{idx}")
            entry_time = st.time_input("Entry Time", value=datetime.datetime.strptime(row["Entry Time"], "%H:%M").time(), key=f"time{idx}")
            vendor_material = st.text_input("Vendor / Material", row["Vendor / Material"], key=f"vm{idx}")
            status = st.selectbox("Status",
                                  ["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"],
                                  index=["Inside (🟡)", "Ready to Leave (🟢)", "Left (✅)"].index(row["Status"]),
                                  key=f"status{idx}")
            if st.button(f"Save for {row['Truck Number']}", key=f"save{idx}"):
                df.at[idx, "Truck Number"] = truck_number
                df.at[idx, "Driver Phone"] = driver_phone
                df.at[idx, "Entry Time"] = format_entry_time(entry_time)
                df.at[idx, "Vendor / Material"] = vendor_material
                df.at[idx, "Status"] = status
                df.at[idx, "Updated By"] = "MasterUser"
                save_data(df)
                st.success("Entry updated.")
                st.rerun()

# ========== Gate ==========
elif role == "Gate":
    st.subheader("🚧 Gate Entry (Inside only)")
    with st.form("gate_form"):
        truck_number = st.text_input("Truck Number")
        driver_phone = st.text_input("Driver Phone")
        entry_time = st.time_input("Entry Time", value=datetime.datetime.now().time())
        vendor_material = st.text_input("Vendor / Material in Truck")
        submitted = st.form_submit_button("Submit")
        if submitted:
            new_entry = {
                "Date": datetime.date.today().strftime("%Y-%m-%d"),
                "Truck Number": truck_number,
                "Driver Phone": driver_phone,
                "Entry Time": format_entry_time(entry_time),
                "Vendor / Material": vendor_material,
                "Status": "Inside (🟡)",
                "Updated By": "Gate"
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success("Gate entry added.")
            st.rerun()

# ========== SCM ==========
elif role == "SCM":
    st.subheader("✏️ SCM: Update Gate Entries Only")
    for idx, row in df.iterrows():
        if row["Updated By"] == "Gate":
            st.markdown(f"**Truck:** {row['Truck Number']} | Status: {row['Status']}")
            status_options = ["Inside (🟡)", "Ready to Leave (🟢)"]
            new_status = st.selectbox(
                f"Update Status for {row['Truck Number']}",
                status_options,
                index=status_options.index(row["Status"]) if row["Status"] in status_options else 0,
                key=f"scm_select_{idx}"
            )
            if st.button(f"Update Status", key=f"scm_button_{idx}"):
                df.at[idx, "Status"] = new_status
                df.at[idx, "Updated By"] = "SCM"
                save_data(df)
                st.success("SCM updated entry")
                st.rerun()

# ========== Parking ==========
elif role == "Parking":
    st.subheader("🅿️ Parking: Update to Ready or Left")
    for idx, row in df.iterrows():
        if row["Status"] != "Left (✅)":
            st.markdown(f"**Truck:** {row['Truck Number']} | Status: {row['Status']}")
            options = ["Ready to Leave (🟢)", "Left (✅)"]
            new_status = st.selectbox(
                f"Set Status",
                options,
                index=options.index(row["Status"]) if row["Status"] in options else 0,
                key=f"parking_select_{idx}"
            )
            if st.button(f"Confirm Update", key=f"parking_button_{idx}"):
                df.at[idx, "Status"] = new_status
                df.at[idx, "Updated By"] = "Parking"
                save_data(df)
                st.success("Parking updated status")
                st.rerun()
        else:
            st.info(f"{row['Truck Number']} is already marked Left ✅")

# ========== Viewer ==========
st.subheader("📋 Current Truck Status")
if df.empty:
    st.info("No truck data available.")
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
