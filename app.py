# --- app.py ---
# Main entry point for the Innergy Product Posting Tool.
# This file stays small on purpose — it just routes between the login page and the main page.

import streamlit as st

from styles import inject_global_styles
from login_page import render_login_page
from main_page import render_main_page


# --- PAGE CONFIG ---
st.set_page_config(page_title="Innergy Product Posting Tool", layout="wide")


# --- GLOBAL STYLES ---
inject_global_styles()


# --- SESSION STATE DEFAULTS ---
for key, default in {
    "api_key": "",
    "authenticated": False,
    "employees_df": None,
    "company_name": "",
    "facility_id": None,
    "facility_name": "",
    "show_opp_form": False,
    "opp_success": False,
    "opp_error": None,
    "debug_payload": None,
    "disconnect": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# --- ROUTER: decide which page to render ---
if not st.session_state.authenticated:
    render_login_page()
else:
    render_main_page()