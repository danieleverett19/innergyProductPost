import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Innergy Product Posting Tool", layout="wide")

# ── Constants ──────────────────────────────────────────────────────────────────
BASE_URL = "https://app.innergy.com/api"

EMPLOYEE_ENDPOINTS = [
    "/v1/employees",
    "/v2/employees",
    "/employees",
    "/v1/users",
    "/users",
    "/v1/hr/employees",
    "/hr/employees",
]

# ── Session state defaults ─────────────────────────────────────────────────────
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "employees_df" not in st.session_state:
    st.session_state.employees_df = None
if "working_endpoint" not in st.session_state:
    st.session_state.working_endpoint = None


def try_get(endpoint: str, api_key: str):
    """Try a GET request using the most common Innergy auth header patterns."""
    url = BASE_URL + endpoint
    header_variants = [
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": f"Token {api_key}"},
        {"X-API-Key": api_key},
        {"ApiKey": api_key},
        {"api-key": api_key},
    ]
    for headers in header_variants:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                return r, headers, url
            if r.status_code in (401, 403):
                # Auth failed for this header variant — try next
                continue
        except requests.exceptions.RequestException:
            continue
    # Return last response for debugging
    try:
        r = requests.get(url, headers=header_variants[0], timeout=10)
        return r, header_variants[0], url
    except Exception as e:
        return None, None, url


def validate_and_fetch_employees(api_key: str):
    """Try all employee endpoints and return a DataFrame if any succeed."""
    for endpoint in EMPLOYEE_ENDPOINTS:
        response, headers, url = try_get(endpoint, api_key)
        if response is None:
            continue
        if response.status_code == 200:
            try:
                data = response.json()
                # Handle both list and dict responses
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    # Common wrappers: data, employees, results, items
                    for key in ("data", "employees", "results", "items", "records"):
                        if key in data and isinstance(data[key], list):
                            records = data[key]
                            break
                    else:
                        records = [data]  # single object
                else:
                    continue

                if records:
                    df = pd.json_normalize(records)
                    return df, endpoint, url, headers, None
            except Exception as e:
                continue
        elif response.status_code in (401, 403):
            return None, None, None, None, f"❌ API key rejected (HTTP {response.status_code}). Please check your key."
        elif response.status_code == 404:
            continue  # try next endpoint

    return None, None, None, None, "⚠️ Could not find an employees endpoint. The API may use a different path."


def pick_display_columns(df: pd.DataFrame):
    """Pick the most useful columns for display — prefer name/id/status/email etc."""
    priority_keywords = [
        "id", "name", "first", "last", "email", "phone",
        "status", "active", "role", "title", "department",
        "hire", "start", "position", "location"
    ]
    cols = df.columns.tolist()
    ordered = []
    for kw in priority_keywords:
        for col in cols:
            if kw in col.lower() and col not in ordered:
                ordered.append(col)
    # Add any remaining columns not yet included (up to 20 total)
    for col in cols:
        if col not in ordered:
            ordered.append(col)
    return ordered[:20]


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🪵 Innergy Product Posting Tool")
st.markdown("---")

# ── Step 1: API Key Entry ──────────────────────────────────────────────────────
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
                df, endpoint, url, headers, error = validate_and_fetch_employees(api_key_input.strip())

            if error:
                st.error(error)
                st.info("Double-check your API key and try again. If the problem persists, the API endpoint structure may have changed.")
            elif df is not None:
                st.session_state.api_key = api_key_input.strip()
                st.session_state.authenticated = True
                st.session_state.employees_df = df
                st.session_state.working_endpoint = endpoint
                st.success(f"✅ Connected! Found **{len(df)}** employees via `{endpoint}`")
                st.rerun()
            else:
                st.error("Could not retrieve employee data. The API key may be valid but the endpoint is unknown.")
                st.caption(f"Tried: {', '.join(EMPLOYEE_ENDPOINTS)}")

# ── Step 2: Show employee table ────────────────────────────────────────────────
else:
    col1, col2 = st.columns([6, 1])
    with col1:
        st.subheader("👷 Employees")
    with col2:
        if st.button("🔓 Disconnect"):
            for key in ["api_key", "authenticated", "employees_df", "working_endpoint"]:
                st.session_state[key] = "" if key == "api_key" else (False if key == "authenticated" else None)
            st.rerun()

    df = st.session_state.employees_df

    if df is not None and not df.empty:
        display_cols = pick_display_columns(df)
        display_df = df[display_cols].copy()

        # Clean up column names for display
        display_df.columns = [
            c.replace("_", " ").replace(".", " ").title() for c in display_df.columns
        ]

        st.caption(f"Showing {len(display_df)} employees · {len(display_cols)} columns · endpoint: `{st.session_state.working_endpoint}`")

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        # Download button
        csv = display_df.to_csv(index=False).encode("utf-8")
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
