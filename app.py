import streamlit as st
import requests
import pandas as pd
import base64
import json
from pathlib import Path

st.set_page_config(page_title="Innergy Product Posting Tool", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        header[data-testid="stHeader"] {
            background-color: #ffffff;
            border-bottom: 3px solid #E8500A;
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
            padding: 6px 2rem; border-bottom: 3px solid #E8500A;
        }
        .top-bar-inner {
            display: flex; align-items: center; justify-content: space-between;
        }
        .innergy-title { display: flex; align-items: center; gap: 8px; }
        .innergy-title img { height: 28px; width: auto; }
        .innergy-title span { font-size: 1.1rem; font-weight: 700; color: #1a2433; }
        .welcome-text { font-size: 0.85rem; font-weight: 600; color: #E8500A; }
        .main-content { margin-top: 80px; }
    </style>
""", unsafe_allow_html=True)

BASE_URL = "https://app.innergy.com"

# BidType GUIDs fetched from Innergy network inspector
BID_TYPE_MAP = {
    "Actual": "7bb84c4f-8751-4241-9e16-ca07eb0ef0fc",
    "Budget": "89e93736-3f6e-4630-89b6-3e9ac64eb841"
}

EMPLOYEE_COLUMNS = [
    "FirstName", "LastName", "LoginEmail", "Status", "EmploymentStatus",
    "Department", "Facility", "DateOfHire", "Roles", "OfficePhone",
    "TimeZone", "ExternalIdentifier", "Id", "CreatedDate", "LastLoginDate"
]

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
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def get_logo_base64():
    logo_path = Path("Images/InnergyLogo.jpeg")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/jpeg;base64,{data}"
    return None


def fetch_company_name(api_key: str):
    url = BASE_URL + "/api/ourCompanyInfo/settings"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for field in ("CompanyName", "Name", "companyName", "name", "Company", "company"):
                if field in data and data[field]:
                    return data[field]
        return None
    except Exception:
        return None


def fetch_facility(api_key: str):
    url = BASE_URL + "/api/opportunities"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            items = []
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("Items") or data.get("items") or data.get("data") or []
            for item in items:
                fid = item.get("FacilityId") or item.get("facilityId")
                fname = item.get("FacilityName") or item.get("facilityName") or ""
                if fid:
                    return fid, fname
        return None, ""
    except Exception:
        return None, ""


def fetch_employees(api_key: str):
    url = BASE_URL + "/api/employees"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                for key in ("data", "employees", "results", "items"):
                    if key in data and isinstance(data[key], list):
                        df = pd.DataFrame(data[key])
                        break
                else:
                    df = pd.DataFrame([data])
            cols = [c for c in EMPLOYEE_COLUMNS if c in df.columns]
            return df[cols], None
        elif r.status_code in (401, 403):
            return None, f"❌ API key rejected (HTTP {r.status_code}). Please check your key."
        else:
            return None, f"❌ Unexpected response: HTTP {r.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Could not reach Innergy. Check your internet connection."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def create_opportunity(api_key: str, payload: dict):
    url = BASE_URL + "/api/opportunities/create"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Api-Key": api_key
    }
    try:
        body = json.dumps([payload]).encode("utf-8")
        r = requests.post(url, headers=headers, data=body, timeout=15)
        if r.status_code in (200, 201):
            return True, r.json()
        else:
            return False, f"HTTP {r.status_code}: {r.text}"
    except Exception as e:
        return False, str(e)


logo_src = get_logo_base64()

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    if logo_src:
        st.markdown(f"""
            <div class="innergy-title" style="margin-bottom:0.5rem;">
                <img src="{logo_src}" />
                <span>Product Posting Tool</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### Innergy Product Posting Tool")

    st.markdown("---")
    st.subheader("Connect to Innergy")
    st.markdown("Paste your Innergy API key below to get started.")

    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your Innergy API key here...",
        help="Your API key is stored only for this session and never saved.",
        label_visibility="collapsed"
    )

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

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
else:
    company = st.session_state.company_name
    welcome_text = f"Welcome, {company}" if company else "Welcome"

    if logo_src:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-inner">
                    <div class="innergy-title">
                        <img src="{logo_src}" />
                        <span>Product Posting Tool</span>
                    </div>
                    <div class="welcome-text">{welcome_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="top-bar">
                <div class="top-bar-inner">
                    <div class="innergy-title"><span>Product Posting Tool</span></div>
                    <div class="welcome-text">{welcome_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([10, 1])
    with top_col2:
        if st.button("Disconnect", type="secondary", key="disconnect_btn"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

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

    # ══════════════════════════════════════════════════════════════════════════
    # OPPORTUNITIES
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("### Opportunities")

    if st.button("＋ Create Opportunity", type="primary"):
        st.session_state.show_opp_form = not st.session_state.show_opp_form

    if st.session_state.show_opp_form:
        st.markdown("---")
        st.markdown("#### New Opportunity")
        st.caption("All fields marked * are required.")

        fname = st.session_state.facility_name or "Unknown"
        st.info(f"🏢 Facility: **{fname}**")

        with st.form("opp_form", clear_on_submit=False):

            st.markdown("**Opportunity Details**")
            opp_name = st.text_input("Opportunity Name *",
                                     placeholder="e.g. 107 Norfolk")

            st.markdown("---")
            st.markdown("**Bid Details**")
            bid_name = st.text_input("Bid Name *", value="First Bid")

            col1, col2 = st.columns(2)
            with col1:
                bid_type_selection = st.selectbox(
                    "Bid Type *", ["", "Actual", "Budget"]
                )
            with col2:
                proj_revenue = st.number_input(
                    "Projected Revenue ($) *",
                    min_value=0.0, value=0.0, step=500.0
                )

            col3, col4 = st.columns(2)
            with col3:
                win_prob = st.number_input(
                    "Win Probability (%) *",
                    min_value=0, max_value=100, value=0, step=1,
                    help="Enter as whole number e.g. 75 for 75%"
                )
            with col4:
                target_margin = st.number_input(
                    "Target Margin (%) *",
                    min_value=0, max_value=100, value=0, step=1,
                    help="Enter as whole number e.g. 40 for 40%"
                )

            st.markdown("---")
            st.markdown("**Dates**")
            first_delivery = st.date_input("First Delivery Date *", value=None)

            col5, col6 = st.columns(2)
            with col5:
                last_delivery = st.date_input(
                    "Last Delivery Date *",
                    value=first_delivery if first_delivery else None
                )
            with col6:
                substantial_completion = st.date_input(
                    "Substantial Completion Date *",
                    value=first_delivery if first_delivery else None
                )

            st.markdown("")
            col_cancel, col_spacer, col_submit = st.columns([2, 5, 2])
            with col_cancel:
                cancel = st.form_submit_button("Cancel", type="secondary")
            with col_submit:
                submit = st.form_submit_button("Create Opportunity",
                                               type="primary")

        if cancel:
            st.session_state.show_opp_form = False
            st.rerun()

        if submit:
            errors = []
            if not opp_name.strip():
                errors.append("Opportunity Name is required.")
            if not bid_name.strip():
                errors.append("Bid Name is required.")
            if not bid_type_selection:
                errors.append("Bid Type is required.")
            if not first_delivery:
                errors.append("First Delivery Date is required.")
            if not last_delivery:
                errors.append("Last Delivery Date is required.")
            if not substantial_completion:
                errors.append("Substantial Completion Date is required.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                payload = {
                    "Name": opp_name.strip(),
                    "CurrentBidName": bid_name.strip(),
                    "BidTypeId": BID_TYPE_MAP[bid_type_selection],
                    "WinProbabilityPercentage": round(win_prob / 100, 4),
                    "TargetMarginPercentage": round(target_margin / 100, 4),
                    "ProjectedRevenue": proj_revenue,
                    "FirstDeliveryDate": first_delivery.isoformat(),
                    "LastDeliveryDate": last_delivery.isoformat(),
                    "SubstantialCompletionDate": substantial_completion.isoformat(),
                    "FacilityId": st.session_state.facility_id,
                }

                with st.spinner("Creating opportunity..."):
                    success, result = create_opportunity(
                        st.session_state.api_key, payload
                    )

                if success:
                    st.session_state.show_opp_form = False
                    st.session_state.opp_success = True
                    st.session_state.debug_payload = None
                else:
                    st.session_state.opp_error = result
                    st.session_state.debug_payload = payload
                st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # EMPLOYEES
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("Employees")
    df = st.session_state.employees_df
    if df is not None and not df.empty:
        st.caption(f"{len(df)} employees · {len(df.columns)} columns")
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="innergy_employees.csv",
            mime="text/csv",
        )
    else:
        st.warning("No employee data to display.")

    st.markdown('</div>', unsafe_allow_html=True)