import streamlit as st

def get_user_role(password):
    roles = {
        "master123": "MasterUser",
        "scm2025": "SCM",
        "gate123": "Gate",
        "parking123": "Parking"
    }
    return roles.get(password, None)

def get_api_key():
    return st.secrets["AIRTABLE_API_KEY"]
