## Session — April 23, 2026

### Wins
- **Cracked Global variable dropdowns** 🎉 The endpoint is `/api/v2-unstable/libraries/variables/variable-set-values` — the trick was passing `variableSetId` as a lowercase query parameter (not as a filter array). My earlier filter attempts kept returning 0 items. Dan figured it out via Power Query M code.
- Global variable dropdowns in the cart now show the full list of options for each variable set (e.g. 301 Laminate shows all 10 PL options).
- Labels formatted as "Reference - DisplayName" (e.g. "001 - PL 01: As Spec'd") to match Innergy's UI convention.
- Per-session caching of instance lists so we don't re-fetch the same variable set twice.

### UI polish
- Product library rows: name + description now render on the same line, with tighter row spacing.
- Categories stay expanded after clicking Add (no more re-expanding).
- Replaced `st.toast` with an inline green "✓ Added" flag next to each product's button — fades out after 3 seconds via CSS animation.
- Globals dropdowns are no longer grayed out.

### Dead ends (for future reference — do NOT re-try these)
- Tried `/query/run` POST with `VariableSetValueListQuery` → 403 Forbidden (API key auth not accepted on internal query endpoint).
- Tried `/query/run` GET with URL-encoded JSON → HTTP 500.
- Tried `/api/v2-unstable/libraries/parts/base-variable-sets/{id}/elements` → HTTP 500 (wrong ID type; `additionId` is not a variable set ID).
- Earlier attempt with `filter=["VariableSetId","=","<guid>"]` on variable-set-values endpoint → 0 items. The correct approach was a direct `variableSetId` query param.

### Still not built
- Posting products with filled variables back to Innergy.
- "Start new opportunity" button (multi-opportunity sessions).
- Nicely formatted product dimensions (X × Y × Z) in the library.
- Fetching and displaying an existing opportunities list.

## Features Completed

### Authentication & Layout
- Login card with Innergy logo, blocked browser autofill, password-masked API key input
- On connect: fetches company name, facility (id + name), validates via employees endpoint
- Frozen top bar on authenticated page (logo left, welcome-company-name center, disconnect right)
- Disconnect button clears session via query param
- Developer auto-fill: DEV_API_KEY in secrets.toml pre-fills the login field
- Developer skip-opp toggle: DEV_SKIP_OPP in secrets.toml lets us skip creating an opportunity while testing UI; also togglable live in the UI

### Opportunities
- Create Opportunity form (simplified to only two visible fields):
  - Opportunity Name * (free text)
  - First Delivery Date * (required)
  - All other required API fields are set to hidden defaults:
    - Bid Name = "First Bid"
    - Bid Type = Actual
    - Projected Revenue = 0
    - Win Probability = 0
    - Target Margin = 0
    - Last Delivery Date = First Delivery Date
    - Substantial Completion Date = First Delivery Date
    - Facility Id = captured at login
- Posts to `/api/opportunities/create` with payload wrapped in `[payload]` as raw bytes
- After success: stores the new opportunity's Id and Name in session state; hides the Create button for the rest of the session (one-opportunity-per-session model)
- Debug expander shows the payload if the POST fails

### Products UI
- After an opportunity exists (or dev skip is on), the page shows the Products section
- Product library fetched once per session from `/api/products`, filtered to Status = Active
- Grouped by CategoryName, each category in its own expander (collapsed by default)
- Each product row: Name (bold) + Description + "Add to Opportunity" button
- Duplicates allowed: clicking Add creates a new cart line each time
- Toast notification "✓ Added [name] to opportunity" on each add

### Cart
- Above the library
- One st.expander per line
- Collapsed summary: "[editable name] — Qty N"
- Expanded body:
  - Top row: Name (editable text) | Library Name (read-only) | Qty (editable number) | Remove (✕)
  - Global Variables section (3-column layout, disabled dropdowns showing PrimaryInstance default — pending Round 2)
  - Local Variables section (3-column layout, working dropdowns from PredefinedValues, free-text input when no PredefinedValues)
  - All edits persist across reruns via `cart[line_id]["globals"]` and `cart[line_id]["locals"]` dicts

### Variable Catalogs
- Fetched once per session via two V2-unstable endpoints:
  - `/api/v2-unstable/libraries/variable-sets?skip=0&take=500` — globals catalog (20 groups)
  - `/api/v2-unstable/libraries/variables?skip=0&take=500` — locals catalog with TypeName, PredefinedValues, DefaultValue
- A third endpoint, `/api/v2-unstable/libraries/variables/variable-set-values`, returned 0 items — still a mystery (see Open Items)
- Matched to per-product Globals/Locals arrays by DisplayName

## Confirmed API Details

### Auth
- Base URL: `https://app.innergy.com`
- Header: `Api-Key: <key>` (not Authorization: Bearer)

### V1 Endpoints Used
- `GET /api/ourCompanyInfo/settings` — company name
- `GET /api/employees` — used to validate the API key on login
- `GET /api/opportunities` — used to discover a FacilityId at login
- `POST /api/opportunities/create` — payload wrapped in `[payload]` array, sent as raw bytes via `json.dumps(...).encode("utf-8")`
- `GET /api/products` — product library; response wrapped in `Items`

### V2-unstable Endpoints Used
- `GET /api/v2-unstable/libraries/variable-sets` — global variable groups; response wrapped in `data`; supports `skip` + `take` (max 500)
- `GET /api/v2-unstable/libraries/variables` — local variables catalog; same pagination

### Field-name Gotchas (POST vs GET on Opportunities)
- GET returns `FirstDelivery`, `LastDelivery`, `SubstantialCompletion`
- POST requires `FirstDeliveryDate`, `LastDeliveryDate`, `SubstantialCompletionDate`
- GET returns `CurrentBid`; POST requires `CurrentBidName`
- `WinProbabilityPercentage` / `TargetMarginPercentage` on POST are decimals (0.75 = 75%)
- `BidTypeId` on POST requires a GUID (see below)
- `FacilityId` is required on POST

### BidType GUIDs (account-specific)
- Actual: `7bb84c4f-8751-4241-9e16-ca07eb0ef0fc`
- Budget: `89e93736-3f6e-4630-89b6-3e9ac64eb841`

## Open Items / Next Sessions

### Round 2 — Global Variable Dropdowns
We have the default (`PrimaryInstance`) for every global but not the full list of instance names. The `variable-set-values` endpoint returned 0 items with no filter — probably needs a specific `variable-set-id` parameter. Next steps:
- Test `variable-set-values` with a query param like `variable-set-id=<GUID>` or similar
- Or hunt via Chrome DevTools for a per-group-instances endpoint the Innergy UI itself calls
- Once found, turn the globals dropdowns from disabled to working

### Future Work
- Post products (with filled variables) back to Innergy
- Start-new-opportunity button / multi-opportunity flow within a single session
- Nicely formatted product dimensions (X × Y × Z) in the library

## Dan's Shortcuts
- "Let's publish" — push to GitHub and update the live Streamlit app
- "Let's test this out" — run locally via `streamlit run app.py`
- "Revert back" — discard uncommitted changes (`git checkout -- app.py`) or soft-reset last commit (`git reset --soft HEAD~1`)