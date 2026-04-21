# --- login_page.py ---
# The login card shown before the user is authenticated.
# Includes a developer auto-fill feature: if a DEV_API_KEY is found in
# .streamlit/secrets.toml, the API key field is pre-filled for faster local testing.

import streamlit as st
import base64
from pathlib import Path

from api_helpers import fetch_employees, fetch_company_name, fetch_facility
from styles import inject_login_styles


# --- HELPER: LOAD LOGO ---
def get_logo_base64():
    logo_path = Path("Images/InnergyLogo.jpeg")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/jpeg;base64,{data}"
    return None


# --- HELPER: READ DEV API KEY FROM SECRETS (local only) ---
def get_dev_api_key():
    # Safely read an optional DEV_API_KEY from .streamlit/secrets.toml.
    # On the live Streamlit Cloud app this will not be set, so the key will be blank.
    try:
        return st.secrets.get("DEV_API_KEY", "")
    except Exception:
        return ""


# --- MAIN LOGIN PAGE RENDERER ---
def render_login_page():
    logo_src = get_logo_base64()
    dev_key = get_dev_api_key()

    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        with st.container(border=True):
            inner_l, inner_mid, inner_r = st.columns([0.01, 0.98, 0.01])
            with inner_mid:
                # --- LOGO AND TITLE INSIDE THE CARD ---
                if logo_src:
                    st.markdown(f"""
                        <div class="innergy-title" style="margin-bottom:1rem; margin-top:0.25rem; pointer-events:none;">
                            <img src="{logo_src}" />
                            <span>Product Posting Tool</span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("#### Product Posting Tool")

                # --- LOGIN STYLES (block browser autofill/password save) ---
                inject_login_styles()

                # --- API KEY INPUT (pre-filled when dev key is set locally) ---
                api_key_input = st.text_input(
                    "API Key",
                    value=dev_key,
                    type="password",
                    placeholder="Paste your Innergy API key here...",
                    help="Your API key is stored only for this session and never saved.",
                    label_visibility="collapsed"
                )

                # --- CONNECT BUTTON AND AUTHENTICATION LOGIC ---
                if st.button("Connect", type="primary"):
                    if not api_key_input.strip():
                        st.error("Please enter an API key.")
                    else:
                        with st.spinner("Connecting to Innergy..."):
                            df, error = fetch_employees(api_key_input.strip())
                            company_name = fetch_company_name(api_key_input.strip())
                            facility_id, facility_name = fetch_facility(api_key_input.strip())
                        if error:
                            st.error(error)
                        elif df is not None:
                            st.session_state.api_key = api_key_input.strip()
                            st.session_state.authenticated = True
                            st.session_state.employees_df = df
                            st.session_state.company_name = company_name or ""
                            st.session_state.facility_id = facility_id
                            st.session_state.facility_name = facility_name
                            st.rerun()
                        else:
                            st.error("No employee data returned.")