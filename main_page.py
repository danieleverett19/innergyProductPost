# --- main_page.py ---
# The authenticated page shown after a successful login.
# Contains the frozen top bar, the Opportunities section, and the New Opportunity form.

import streamlit as st

from api_helpers import create_opportunity, BID_TYPE_MAP
from login_page import get_logo_base64
from styles import inject_main_page_styles


# --- MAIN AUTHENTICATED PAGE RENDERER ---
def render_main_page():
    # --- SCOPED STYLE: tighten top padding only on this page ---
    inject_main_page_styles()

    logo_src = get_logo_base64()
    company = st.session_state.company_name
    welcome_text = f"Welcome, {company}" if company else "Welcome"

    # --- TOP BAR (fixed header with logo, welcome message, disconnect button) ---
    if logo_src:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-inner">
                    <div class="innergy-title">
                        <img src="{logo_src}" />
                        <span>Product Posting Tool</span>
                    </div>
                    <div class="welcome-text">{welcome_text}</div>
                    <form action="" method="get">
                        <button class="disconnect-btn" name="disconnect" value="1">Disconnect</button>
                    </form>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-inner">
                    <div class="innergy-title"><span>Product Posting Tool</span></div>
                    <div class="welcome-text">{welcome_text}</div>
                    <form action="" method="get">
                        <button class="disconnect-btn" name="disconnect" value="1">Disconnect</button>
                    </form>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- HANDLE DISCONNECT ---
    if st.query_params.get("disconnect") == "1":
        st.query_params.clear()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # --- SUCCESS / ERROR MESSAGES ---
    if st.session_state.opp_success:
        st.success("✅ Opportunity created successfully!")
        st.session_state.opp_success = False

    if st.session_state.opp_error:
        st.error(f"❌ Failed to create opportunity: {st.session_state.opp_error}")
        st.session_state.opp_error = None
        if st.session_state.debug_payload:
            with st.expander("🔍 Debug — payload that was sent", expanded=True):
                st.json(st.session_state.debug_payload)
            st.session_state.debug_payload = None

    # --- OPPORTUNITIES SECTION ---
    st.markdown("### Opportunities")

    if st.button("＋ Create Opportunity", type="primary"):
        st.session_state.show_opp_form = not st.session_state.show_opp_form

    # --- CREATE OPPORTUNITY FORM ---
    if st.session_state.show_opp_form:
        _render_create_opportunity_form()

    st.markdown('</div>', unsafe_allow_html=True)


# --- CREATE OPPORTUNITY FORM ---
def _render_create_opportunity_form():
    st.markdown("---")
    st.markdown("#### New Opportunity")
    st.caption("All fields marked * are required.")

    fname = st.session_state.facility_name or "Unknown"
    st.info(f"🏢 Facility: **{fname}**")

    with st.form("opp_form", clear_on_submit=False):

        # --- OPPORTUNITY NAME ---
        st.markdown("**Opportunity Details**")
        opp_name = st.text_input("Opportunity Name *", placeholder="e.g. 107 Norfolk")

        # --- FIRST DELIVERY DATE (only visible date field) ---
        first_delivery = st.date_input("First Delivery Date *", value=None)

        # --- FORM BUTTONS ---
        st.markdown("")
        col_cancel, col_spacer, col_submit = st.columns([2, 5, 2])
        with col_cancel:
            cancel = st.form_submit_button("Cancel", type="secondary")
        with col_submit:
            submit = st.form_submit_button("Create Opportunity", type="primary")

    # --- CANCEL FORM ---
    if cancel:
        st.session_state.show_opp_form = False
        st.rerun()

    # --- SUBMIT FORM ---
    if submit:
        errors = []
        if not opp_name.strip():
            errors.append("Opportunity Name is required.")
        if not first_delivery:
            errors.append("First Delivery Date is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            # --- HIDDEN DEFAULTS (applied automatically) ---
            bid_name = "First Bid"
            bid_type_selection = "Actual"
            proj_revenue = 0.0
            win_prob = 0
            target_margin = 0
            last_delivery = first_delivery
            substantial_completion = first_delivery

            # --- BUILD PAYLOAD ---
            payload = {
                "Name": opp_name.strip(),
                "CurrentBidName": bid_name,
                "BidTypeId": BID_TYPE_MAP[bid_type_selection],
                "WinProbabilityPercentage": round(win_prob / 100, 4),
                "TargetMarginPercentage": round(target_margin / 100, 4),
                "ProjectedRevenue": proj_revenue,
                "FirstDeliveryDate": first_delivery.isoformat(),
                "LastDeliveryDate": last_delivery.isoformat(),
                "SubstantialCompletionDate": substantial_completion.isoformat(),
                "FacilityId": st.session_state.facility_id,
            }

            # --- POST TO INNERGY API ---
            with st.spinner("Creating opportunity..."):
                success, result = create_opportunity(st.session_state.api_key, payload)

            if success:
                st.session_state.show_opp_form = False
                st.session_state.opp_success = True
                st.session_state.debug_payload = None
            else:
                st.session_state.opp_error = result
                st.session_state.debug_payload = payload
            st.rerun()