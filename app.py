import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Innergy Product Posting Tool", layout="wide")

BASE_URL = "https://app.innergy.com"

EMPLOYEE_COLUMNS = [
    "FirstName", "LastName", "LoginEmail", "Status", "EmploymentStatus",
    "Department", "Facility", "DateOfHire", "Roles", "OfficePhone",
    "TimeZone", "ExternalIdentifier", "Id", "CreatedDate", "LastLoginDate"
]

if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "employees_df" not in st.session_state:
    st.session_state.employees_df = None


def fetch_employees(api_key: str):
    url = BASE_URL + "/api/employees"
    headers = {
        "Accept": "application/json",
        "Api-Key": api_key
    }
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
            # Keep only known columns that exist in the response
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


# ── UI ─────────────────────────────────────────────────────────────────────────

st.title("🪵 Innergy Product Posting Tool")
st.markdown("---")

if not st.session_state.authenticated:
    st.subheader("🔑 Connect to Innergy")
    st.markdown("Paste your Innergy API key below to get started.")

    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your Innergy API key here...",
        help="Your API key is stored only for this session and never saved.",
    )

    if st.button("Connect", type="primary"):
        if not api_key_input.strip():
            st.error("Please enter an API key.")
        else:
            with st.spinner("Connecting to Innergy..."):
                df, error = fetch_employees(api_key_input.strip())

            if error:
                st.error(error)
            elif df is not None:
                st.session_state.api_key = api_key_input.strip()
                st.session_state.authenticated = True
                st.session_state.employees_df = df
                st.rerun()
            else:
                st.error("No employee data returned.")

else:
    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader("👷 Employees")
    with col2:
        if st.button("🔓 Disconnect"):
            st.session_state.api_key = ""
            st.session_state.authenticated = False
            st.session_state.employees_df = None
            st.rerun()

    df = st.session_state.employees_df

    if df is not None and not df.empty:
        st.caption(f"{len(df)} employees · {len(df.columns)} columns")
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download as CSV",
            data=csv,
            file_name="innergy_employees.csv",
            mime="text/csv",
        )
    else:
        st.warning("No employee data to display.")

    st.markdown("---")
    st.caption("More features coming soon: Opportunities, Products, Posting.")
