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
# --- Products feature state ---
    "opp_id": None,              # Id of the created opportunity (populated after successful create)
    "opp_name_created": "",      # Name of the created opportunity (for display)
    "cart": {},                  # {line_id: {product_id, library_name, name, qty, category, globals, locals}}
    "cart_line_counter": 0,      # Monotonic counter used to build unique line_ids (duplicates allowed)
    "products_cache": None,      # List of product dicts from /api/products (fetched once per session)
    "dev_skip_opp": None,        # Dev-mode toggle to skip requiring an opportunity (None = use default)
    # --- Variable catalogs (fetched once per session, used across all cart items) ---
    "variable_sets_cache": None,  # Globals catalog from /api/v2-unstable/libraries/variable-sets
    "variables_cache": None,      # Locals catalog from /api/v2-unstable/libraries/variables
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# --- ROUTER: decide which page to render ---
if not st.session_state.authenticated:
    render_login_page()
else:
    render_main_page()