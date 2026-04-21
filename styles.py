# --- styles.py ---
# All CSS styles for the Innergy Product Posting Tool live here.
# Each function returns a string of CSS wrapped in <style> tags.

import streamlit as st


# --- GLOBAL STYLES (used on every page) ---
def inject_global_styles():
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; }
            header[data-testid="stHeader"] {
                background-color: #ffffff;
                border-bottom: 1px solid #e5e7eb;
                padding-top: 0px !important;
                padding-bottom: 0px !important;
                min-height: 0px !important;
            }
            .stButton > button[kind="primary"] {
                background-color: #E8500A; color: white;
                border: none; border-radius: 4px; font-weight: 600;
            }
            .stButton > button[kind="primary"]:hover { background-color: #c94208; color: white; }
            .stButton > button[kind="secondary"] {
                border: 1px solid #E8500A; color: #E8500A;
                border-radius: 4px; font-weight: 600; background-color: white;
            }
            .stButton > button[kind="secondary"]:hover { background-color: #fff3ee; }
            h2, h3 { color: #1a2433; font-weight: 700; }
            hr { border-color: #e5e7eb; }
            .top-bar {
                position: fixed; top: 50px; left: 0; right: 0;
                z-index: 999; background-color: #ffffff;
                height: 65px; border-bottom: 1px solid #e5e7eb;
                padding: 0 2rem;
            }
            .top-bar-inner {
                display: flex; align-items: center; justify-content: space-between;
                height: 100%;
            }
            .innergy-title { display: flex; align-items: center; gap: 8px; }
            .innergy-title img { height: 28px; width: auto; }
            .innergy-title span { font-size: 1.1rem; font-weight: 700; color: #1a2433; }
            .welcome-text { font-size: 1.4rem; font-weight: 700; color: #1a2433; position: absolute; left: 50%; transform: translateX(-50%); }
            .disconnect-btn {
                background-color: white; border: 1px solid #E8500A;
                color: #E8500A; border-radius: 4px; font-weight: 600;
                padding: 4px 12px; cursor: pointer; font-size: 0.9rem;
            }
            .disconnect-btn:hover { background-color: #fff3ee; }
            .main-content { margin-top: 80px; }
        </style>
    """, unsafe_allow_html=True)


# --- LOGIN-PAGE-ONLY STYLES ---
def inject_login_styles():
    # Block browser autocomplete/password save on the API key field
    st.markdown("""
        <style>
            input[type="password"] { autocomplete: off !important; }
        </style>
        <input type="text" name="prevent_autofill" style="display:none;" autocomplete="off" />
        <input type="password" name="prevent_autofill2" style="display:none;" autocomplete="off" />
    """, unsafe_allow_html=True)


# --- MAIN-PAGE-ONLY STYLES ---
def inject_main_page_styles():
    # Tighten top padding only on the authenticated page
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)