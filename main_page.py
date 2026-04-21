# --- main_page.py ---
# The authenticated page shown after a successful login.
# Contains: frozen top bar, Opportunities section, New Opportunity form,
# and the Products section (cart + library + per-line variable editors).

import streamlit as st

from api_helpers import (
    create_opportunity,
    fetch_products,
    fetch_variable_sets,
    fetch_variables,
    BID_TYPE_MAP,
)
from login_page import get_logo_base64, get_dev_api_key
from styles import inject_main_page_styles


# --- HELPER: READ DEV SKIP-OPP FLAG FROM SECRETS ---
def get_dev_skip_opp_default():
    try:
        return bool(st.secrets.get("DEV_SKIP_OPP", False))
    except Exception:
        return False


# --- HELPER: ARE WE IN DEV MODE? ---
def is_dev_mode():
    return bool(get_dev_api_key())


# --- HELPER: DOES AN OPPORTUNITY EXIST FOR THIS SESSION? ---
def has_opportunity():
    if st.session_state.opp_id:
        return True
    if st.session_state.dev_skip_opp:
        return True
    return False


# --- HELPER: WHAT NAME TO DISPLAY FOR THE ACTIVE OPPORTUNITY? ---
def active_opp_display_name():
    if st.session_state.opp_name_created:
        return st.session_state.opp_name_created
    if st.session_state.dev_skip_opp:
        return "TEST OPP (dev mode)"
    return ""


# --- MAIN AUTHENTICATED PAGE RENDERER ---
def render_main_page():
    inject_main_page_styles()

    if st.session_state.dev_skip_opp is None:
        st.session_state.dev_skip_opp = get_dev_skip_opp_default()

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

    # --- DEV MODE TOGGLE (only shown when DEV_API_KEY is in secrets) ---
    if is_dev_mode():
        with st.expander("🛠️ Developer Tools", expanded=False):
            st.caption("This section only appears when a DEV_API_KEY is set in secrets.toml.")
            new_val = st.toggle(
                "Skip requiring an opportunity (show Products immediately)",
                value=st.session_state.dev_skip_opp,
                help="When ON, you don't need to create an opportunity before seeing the products UI."
            )
            if new_val != st.session_state.dev_skip_opp:
                st.session_state.dev_skip_opp = new_val
                st.rerun()

    # --- SUCCESS / ERROR MESSAGES ---
    if st.session_state.opp_success:
        st.success(f"✅ Opportunity created successfully: **{st.session_state.opp_name_created}**")
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

    if not has_opportunity():
        if st.button("＋ Create Opportunity", type="primary"):
            st.session_state.show_opp_form = not st.session_state.show_opp_form

        if st.session_state.show_opp_form:
            _render_create_opportunity_form()
    else:
        st.info(f"📋 Active opportunity: **{active_opp_display_name()}**")
        _render_products_section()

    st.markdown('</div>', unsafe_allow_html=True)


# --- CREATE OPPORTUNITY FORM ---
def _render_create_opportunity_form():
    st.markdown("---")
    st.markdown("#### New Opportunity")
    st.caption("All fields marked * are required.")

    fname = st.session_state.facility_name or "Unknown"
    st.info(f"🏢 Facility: **{fname}**")

    with st.form("opp_form", clear_on_submit=False):
        st.markdown("**Opportunity Details**")
        opp_name = st.text_input("Opportunity Name *", placeholder="e.g. 107 Norfolk")
        first_delivery = st.date_input("First Delivery Date *", value=None)

        st.markdown("")
        col_cancel, col_spacer, col_submit = st.columns([2, 5, 2])
        with col_cancel:
            cancel = st.form_submit_button("Cancel", type="secondary")
        with col_submit:
            submit = st.form_submit_button("Create Opportunity", type="primary")

    if cancel:
        st.session_state.show_opp_form = False
        st.rerun()

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
            bid_name = "First Bid"
            bid_type_selection = "Actual"
            proj_revenue = 0.0
            win_prob = 0
            target_margin = 0
            last_delivery = first_delivery
            substantial_completion = first_delivery

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

            with st.spinner("Creating opportunity..."):
                success, result = create_opportunity(st.session_state.api_key, payload)

            if success:
                new_opp_id = None
                new_opp_name = opp_name.strip()
                try:
                    if isinstance(result, list) and result:
                        first = result[0]
                        new_opp_id = first.get("Id") or first.get("id")
                        new_opp_name = first.get("Name") or first.get("name") or new_opp_name
                    elif isinstance(result, dict):
                        new_opp_id = result.get("Id") or result.get("id")
                        new_opp_name = result.get("Name") or result.get("name") or new_opp_name
                except Exception:
                    pass

                st.session_state.opp_id = new_opp_id
                st.session_state.opp_name_created = new_opp_name
                st.session_state.show_opp_form = False
                st.session_state.opp_success = True
                st.session_state.debug_payload = None
            else:
                st.session_state.opp_error = result
                st.session_state.debug_payload = payload
            st.rerun()


# --- PRODUCTS SECTION (cart + library) ---
def _render_products_section():
    st.markdown("---")
    st.markdown("### Products")

    # --- FETCH PRODUCTS ONCE PER SESSION ---
    if st.session_state.products_cache is None:
        with st.spinner("Loading products..."):
            items, error = fetch_products(st.session_state.api_key)
        if error:
            st.error(error)
            return
        active_items = [p for p in (items or []) if p.get("Status") == "Active"]
        st.session_state.products_cache = active_items

    # --- FETCH VARIABLE CATALOGS ONCE PER SESSION (used by all cart line editors) ---
    _ensure_variable_catalogs_loaded()

    products = st.session_state.products_cache or []

    if not products:
        st.warning("No active products found.")
        return

    # --- CART (ON TOP) ---
    _render_cart()

    # --- LIBRARY (BELOW) ---
    _render_library(products)


# --- HELPER: LOAD BOTH VARIABLE CATALOGS ONCE PER SESSION ---
def _ensure_variable_catalogs_loaded():
    if st.session_state.variable_sets_cache is None:
        with st.spinner("Loading global variable catalog..."):
            items, error = fetch_variable_sets(st.session_state.api_key)
        if error:
            st.warning(f"Could not load global variable catalog: {error}")
            st.session_state.variable_sets_cache = []
        else:
            st.session_state.variable_sets_cache = items or []

    if st.session_state.variables_cache is None:
        with st.spinner("Loading local variable catalog..."):
            items, error = fetch_variables(st.session_state.api_key)
        if error:
            st.warning(f"Could not load local variable catalog: {error}")
            st.session_state.variables_cache = []
        else:
            st.session_state.variables_cache = items or []


# --- HELPER: LOOK UP A GLOBAL VARIABLE SET BY ITS DISPLAY NAME ---
def _find_global_by_display_name(display_name: str):
    # The /api/products response lists globals by their display name (e.g. "301 Laminate").
    # We look that name up in the /variable-sets catalog to get the PrimaryInstance (default) etc.
    if not display_name:
        return None
    for vs in st.session_state.variable_sets_cache or []:
        name_field = vs.get("Name")
        dn = name_field.get("DisplayName") if isinstance(name_field, dict) else name_field
        if dn == display_name:
            return vs
    return None


# --- HELPER: LOOK UP A LOCAL VARIABLE BY ITS DISPLAY NAME ---
def _find_local_by_display_name(display_name: str):
    if not display_name:
        return None
    for v in st.session_state.variables_cache or []:
        dn_field = v.get("DisplayName")
        dn = dn_field.get("DisplayName") if isinstance(dn_field, dict) else dn_field
        if dn == display_name:
            return v
    return None


# --- HELPER: PARSE PREDEFINED VALUES STRING INTO A LIST ---
def _parse_predefined_values(predefined: str):
    # API returns something like "finished, raw" or "0, 2, 4, 6"
    if not predefined:
        return []
    return [v.strip() for v in predefined.split(",") if v.strip()]


# --- CART RENDERER ---
def _render_cart():
    st.markdown("#### 🛒 Your Cart")

    cart = st.session_state.cart
    if not cart:
        st.caption("No products added yet. Pick some from the library below.")
        return

    st.caption(f"{len(cart)} line{'s' if len(cart) != 1 else ''} in cart.")

    # Reduce vertical padding between streamlit expanders in the cart
    st.markdown("""
        <style>
            div[data-testid="stExpander"] { margin-bottom: 0.25rem; }
            div[data-testid="stExpander"] details summary { padding: 0.35rem 0.75rem; }
            div.var-row { padding: 0.1rem 0; }
        </style>
    """, unsafe_allow_html=True)

    # Render each cart line as its own expander
    for line_id, entry in list(cart.items()):
        _render_cart_line(line_id, entry)

    st.markdown("---")


# --- SINGLE CART LINE (expander: header = summary row, body = variable editors) ---
def _render_cart_line(line_id, entry):
    summary_label = f"{entry.get('name') or entry.get('library_name')}  —  Qty {entry.get('qty', 1)}"
    with st.expander(summary_label, expanded=False):
        # --- TOP ROW: editable name | library name (read-only) | qty | remove ---
        h1, h2, h3, h4 = st.columns([4, 4, 2, 1])
        with h1:
            st.markdown("**Name**")
            new_name = st.text_input(
                "name",
                value=entry["name"],
                key=f"cart_name_{line_id}",
                label_visibility="collapsed",
            )
            if new_name != entry["name"]:
                st.session_state.cart[line_id]["name"] = new_name
        with h2:
            st.markdown("**Library Name**")
            st.write(entry["library_name"])
        with h3:
            st.markdown("**Qty**")
            new_qty = st.number_input(
                "qty",
                min_value=1,
                value=int(entry["qty"]),
                step=1,
                key=f"cart_qty_{line_id}",
                label_visibility="collapsed",
            )
            if new_qty != entry["qty"]:
                st.session_state.cart[line_id]["qty"] = int(new_qty)
        with h4:
            st.markdown("**Remove**")
            if st.button("✕", key=f"cart_remove_{line_id}", help="Remove from cart"):
                del st.session_state.cart[line_id]
                st.rerun()

        # --- VARIABLE EDITORS (GLOBAL + LOCAL) ---
        _render_line_variables(line_id, entry)


# --- VARIABLE EDITORS FOR A SINGLE CART LINE ---
def _render_line_variables(line_id, entry):
    # Find the full product record so we know its Globals/Locals lists
    product_id = entry.get("product_id")
    product = None
    for p in st.session_state.products_cache or []:
        if p.get("Id") == product_id:
            product = p
            break

    if not product:
        st.caption("_(Could not find product details — variables unavailable.)_")
        return

    globals_list = product.get("Globals") or []
    locals_list = product.get("Locals") or []

    # --- GLOBAL VARIABLES SECTION ---
    st.markdown("---")
    st.markdown("**Global Variables**")
    if not globals_list:
        st.caption("_(No global variables for this product.)_")
    else:
        _render_globals_section(line_id, globals_list)

    # --- LOCAL VARIABLES SECTION ---
    st.markdown("**Local Variables**")
    if not locals_list:
        st.caption("_(No local variables for this product.)_")
    else:
        _render_locals_section(line_id, locals_list)


# --- RENDER THE GLOBAL VARIABLES (for now: read-only default only) ---
def _render_globals_section(line_id, globals_list):
    # Layout in 3 columns to save vertical space
    cols = st.columns(3)
    for i, g_name in enumerate(globals_list):
        col = cols[i % 3]
        with col:
            catalog_entry = _find_global_by_display_name(g_name)
            default_value = (catalog_entry or {}).get("PrimaryInstance") or "(unknown)"

            # Read current override (if any) so the widget keeps its value after rerun
            overrides = st.session_state.cart[line_id].setdefault("globals", {})
            current = overrides.get(g_name, default_value)

            # For now we only know the default, so the dropdown has just one option.
            # Full dropdown options will come in Round 2.
            st.selectbox(
                g_name,
                options=[current],
                index=0,
                key=f"glob_{line_id}_{g_name}",
                disabled=True,
                help="Full dropdown options coming soon — shown value is the system default.",
            )
            overrides[g_name] = current


# --- RENDER THE LOCAL VARIABLES (working dropdowns based on PredefinedValues) ---
def _render_locals_section(line_id, locals_list):
    cols = st.columns(3)
    for i, l_name in enumerate(locals_list):
        col = cols[i % 3]
        with col:
            catalog_entry = _find_local_by_display_name(l_name)

            if not catalog_entry:
                # Variable listed on the product but not in the catalog — display name only
                st.text_input(l_name, value="(not in catalog)", key=f"loc_{line_id}_{l_name}", disabled=True)
                continue

            predefined = _parse_predefined_values(catalog_entry.get("PredefinedValues", ""))
            default_value = catalog_entry.get("DefaultValue")
            type_name = catalog_entry.get("TypeName", "Text")

            overrides = st.session_state.cart[line_id].setdefault("locals", {})
            current = overrides.get(l_name, default_value if default_value is not None else "")

            # Choose widget type based on whether there are predefined values
            if predefined:
                # Ensure the current value exists in the options list (fallback to first)
                if current not in predefined:
                    current = default_value if default_value in predefined else predefined[0]
                new_val = st.selectbox(
                    l_name,
                    options=predefined,
                    index=predefined.index(current),
                    key=f"loc_{line_id}_{l_name}",
                )
            else:
                # Free-entry when no predefined values
                new_val = st.text_input(
                    l_name,
                    value=str(current) if current is not None else "",
                    key=f"loc_{line_id}_{l_name}",
                    help=f"Type: {type_name}",
                )

            overrides[l_name] = new_val


# --- LIBRARY RENDERER ---
def _render_library(products):
    st.markdown("#### 📚 Product Library")
    st.caption(f"{len(products)} active products across {len({p.get('CategoryName', '') for p in products})} categories.")

    grouped = {}
    for p in products:
        cat = p.get("CategoryName") or "Uncategorized"
        grouped.setdefault(cat, []).append(p)

    for cat in sorted(grouped.keys(), key=lambda s: s.lower()):
        cat_products = sorted(grouped[cat], key=lambda p: (p.get("Name") or "").lower())
        with st.expander(f"{cat} ({len(cat_products)})", expanded=False):
            for p in cat_products:
                _render_library_product(p)


# --- SINGLE PRODUCT ROW IN LIBRARY ---
def _render_library_product(product):
    pid = product.get("Id")
    name = product.get("Name") or "(no name)"
    desc = product.get("Description") or "—"
    category = product.get("CategoryName") or ""

    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"**{name}**")
        st.caption(desc)
    with c2:
        if st.button("Add to Opportunity", key=f"lib_add_{pid}", type="primary"):
            line_id = f"{pid}__{st.session_state.cart_line_counter}"
            st.session_state.cart_line_counter += 1

            st.session_state.cart[line_id] = {
                "product_id": pid,
                "library_name": name,
                "name": name,
                "qty": 1,
                "category": category,
                "globals": {},  # Populated as user interacts with the expander
                "locals": {},   # Populated as user interacts with the expander
            }
            st.toast(f"✓ Added {name} to opportunity", icon="🛒")
            st.rerun()

    st.markdown("<hr style='margin:0.5rem 0; border-color:#f0f0f0;' />", unsafe_allow_html=True)