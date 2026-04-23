# --- api_helpers.py ---
# All Innergy API calls and related constants live here.
# No Streamlit UI code — just pure API logic.
#
# API version choices:
#   - V1 STABLE: used wherever possible (employees, company info, opportunities, products)
#   - V2-UNSTABLE: variable-sets and variables catalogs (no V1 equivalent exists yet)

import requests
import pandas as pd
import json


# --- CONSTANTS ---
BASE_URL = "https://app.innergy.com"

BID_TYPE_MAP = {
    "Actual": "7bb84c4f-8751-4241-9e16-ca07eb0ef0fc",
    "Budget": "89e93736-3f6e-4630-89b6-3e9ac64eb841"
}

EMPLOYEE_COLUMNS = [
    "FirstName", "LastName", "LoginEmail", "Status", "EmploymentStatus",
    "Department", "Facility", "DateOfHire", "Roles", "OfficePhone",
    "TimeZone", "ExternalIdentifier", "Id", "CreatedDate", "LastLoginDate"
]


# --- HELPER: FETCH COMPANY NAME (V1 stable) ---
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


# --- HELPER: FETCH FACILITY (V1 stable) ---
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


# --- HELPER: FETCH EMPLOYEES (V1 stable — used to validate API key on login) ---
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


# --- HELPER: CREATE OPPORTUNITY (V1 stable) ---
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


# --- HELPER: FETCH PRODUCTS (V1 stable) ---
def fetch_products(api_key: str):
    url = BASE_URL + "/api/products"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = []
            if isinstance(data, dict):
                items = data.get("Items") or data.get("items") or data.get("data") or []
            elif isinstance(data, list):
                items = data
            return items, None
        elif r.status_code in (401, 403):
            return None, f"❌ API key rejected (HTTP {r.status_code})."
        else:
            return None, f"❌ Unexpected response: HTTP {r.status_code} — {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Could not reach Innergy."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# --- HELPER: FETCH VARIABLE SETS (V2-unstable — master catalog of global variable groups) ---
def fetch_variable_sets(api_key: str):
    url = BASE_URL + "/api/v2-unstable/libraries/variable-sets?skip=0&take=500"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = []
            if isinstance(data, dict):
                items = data.get("data") or data.get("Data") or []
            elif isinstance(data, list):
                items = data
            return items, None
        elif r.status_code in (401, 403):
            return None, f"❌ API key rejected (HTTP {r.status_code})."
        else:
            return None, f"❌ Unexpected response: HTTP {r.status_code} — {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Could not reach Innergy."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# --- HELPER: FETCH VARIABLES (V2-unstable — local variables catalog) ---
def fetch_variables(api_key: str):
    url = BASE_URL + "/api/v2-unstable/libraries/variables?skip=0&take=500"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = []
            if isinstance(data, dict):
                items = data.get("data") or data.get("Data") or []
            elif isinstance(data, list):
                items = data
            return items, None
        elif r.status_code in (401, 403):
            return None, f"❌ API key rejected (HTTP {r.status_code})."
        else:
            return None, f"❌ Unexpected response: HTTP {r.status_code} — {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Could not reach Innergy."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# --- HELPER: FETCH VARIABLE SET VALUES (V2-unstable — instances inside a variable set) ---
# Returns the dropdown options for a given global variable group.
# e.g. for "301 Laminate" (variableSetId=e300cad4...), returns 10 rows:
# PL 01, PL 02, PL 03, etc.
# Key: variableSetId must be a lowercase query parameter (not a filter).
def fetch_variable_set_values(api_key: str, variable_set_id: str):
    url = BASE_URL + "/api/v2-unstable/libraries/variables/variable-set-values"
    headers = {"Accept": "application/json", "Api-Key": api_key}
    params = {
        "skip": 0,
        "take": 500,
        "variableSetId": variable_set_id,
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            items = []
            if isinstance(data, dict):
                items = data.get("data") or data.get("Data") or []
            elif isinstance(data, list):
                items = data
            return items, None
        elif r.status_code in (401, 403):
            return None, f"❌ API key rejected (HTTP {r.status_code})."
        else:
            return None, f"❌ Unexpected response: HTTP {r.status_code} — {r.text[:200]}"
    except requests.exceptions.ConnectionError:
        return None, "❌ Could not reach Innergy."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"