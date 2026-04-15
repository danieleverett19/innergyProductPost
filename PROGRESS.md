# Innergy Product Posting Tool — Progress Log

## Project Overview
A web-based tool that connects to the Innergy API. Users authenticate with their own API key, then fetch data, create opportunities, add products with variables, and post everything back to Innergy. Shareable with anyone via a public URL.

## Tech Stack
- Python
- Streamlit
- GitHub
- VS Code

## Key Links
- Local folder: C:\Users\dan.everett\projects\postProducts
- GitHub repo: https://github.com/danieleverett19/innergyProductPost
- Live app: https://innergy-posting-tool.streamlit.app
- Innergy API docs: https://app.innergy.com/api/index.html

## Innergy API — Confirmed Working Details
- **Base URL:** `https://app.innergy.com`
- **Auth header:** `Api-Key: <your_key>` (NOT Authorization: Bearer — this was wrong at first)
- **Employees endpoint:** `GET /api/employees` (no version number like /v1/)
- **Response format:** JSON array of employee objects
- **Known employee columns:** CreatedBy, CreatedDate, DateOfHire, Department, EmploymentStatus, ExternalIdentifier, Facility, FirstName, HasPin, Id, LastClockInDate, LastClockInIp, LastClockOutDate, LastClockOutIp, LastLoginDate, LastName, LoginEmail, OfficePhone, Roles, ShiftSchedule, Status, TimeZone
- **How we figured this out:** Dan shared working Power Query M code which revealed the correct header name (`Api-Key`) and endpoint path (`/api/employees`)

## Terminal Instructions for Dan
Every time code is updated, do this in the VS Code terminal:

**Step 1 — Make sure you're in the right folder:**
```
cd C:\Users\dan.everett\projects\postProducts
```

**Step 2 — Stage, commit, and push (one at a time):**
```
git add app.py
```
```
git commit -m "your message here"
```
```
git push
```

**Step 3 — Check the live app:**
- Go to https://innergy-posting-tool.streamlit.app
- Wait 30–60 seconds for Streamlit to redeploy
- Refresh the page

**Common mistakes to avoid:**
- Don't copy the `PS C:\...>` prompt — only copy the command after the `>`
- If push is rejected, run `git pull --rebase` then `git push` again
- If terminal is closed, reopen it in VS Code: Terminal → New Terminal

## Current App Features
- ✅ API key authentication screen (password masked)
- ✅ Connects to Innergy using correct `Api-Key` header
- ✅ Fetches and displays employee table with key columns
- ✅ Download employees as CSV
- ✅ Disconnect button to reset session

## Current Status
- Basic scaffold live ✅
- Full pipeline working (VS Code → GitHub → Streamlit) ✅
- API authentication working ✅
- Employee table working ✅
- Opportunities: not started
- Products/posting: not started

## Next Steps
- Fetch and display Opportunities
- Figure out the opportunities endpoint (use Power Query M code as reference like we did for employees)
- Eventually: create opportunities, add products, fill variables, post back

## Session Log

### Session 1 — April 15, 2026
- Set up project instructions in Claude
- Created PROGRESS.md
- Built API key authentication screen
- Discovered correct auth header (`Api-Key`) and endpoint (`/api/employees`) from Power Query M code
- Got employee table working and displaying in Streamlit ✅
- Learned git push/pull workflow including how to fix rejected pushes with `git pull --rebase`
