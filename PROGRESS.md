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
- **Auth header:** `Api-Key: <your_key>` (NOT Authorization: Bearer)
- **Employees endpoint:** `GET /api/employees` ✅ confirmed working
- **Company info endpoint:** `GET /api/ourCompanyInfo/settings` ✅ confirmed working
- **Response format:** JSON array (employees) or JSON object (company info)
- **Known employee columns:** CreatedBy, CreatedDate, DateOfHire, Department, EmploymentStatus, ExternalIdentifier, Facility, FirstName, HasPin, Id, LastClockInDate, LastClockInIp, LastClockOutDate, LastClockOutIp, LastLoginDate, LastName, LoginEmail, OfficePhone, Roles, ShiftSchedule, Status, TimeZone
- **How to discover new endpoints:** Ask Dan for his Power Query M code — it reveals the exact endpoint and header format

## Current App Features (All Working ✅)
- Innergy logo inline next to title text (logo at Images/InnergyLogo.jpeg)
- Innergy color scheme — white background, navy headings, orange (#E8500A) accents
- API key authentication screen (password masked, session only)
- On connect: fetches company name from `/api/ourCompanyInfo/settings` and displays "Welcome, [Company Name]"
- Fetches and displays employee table with key columns
- Download employees as CSV
- Disconnect button clears session

## What's Not Built Yet
- Opportunities: fetch, create
- Products: add to opportunities, fill variables, post back

## Terminal Instructions for Dan
Every time code is updated, do this in the VS Code terminal:

**Step 1 — Make sure you're in the right folder:**
```
cd C:\Users\dan.everett\projects\postProducts
```

**Step 2 — Stage, commit, push (one at a time, hit Enter after each):**
```
git add app.py
```
```
git commit -m "your message here"
```
```
git push
```

**If push is rejected:**
```
git pull --rebase
```
```
git push
```

**To also push images or other files:**
```
git add Images/
```
```
git commit -m "Add images"
```
```
git push
```

**Common mistakes to avoid:**
- Only copy the command AFTER the `>` — never copy the `PS C:\...>` part itself
- If terminal is closed, reopen in VS Code: Terminal → New Terminal

**Step 3 — Check the live app:**
- Go to https://innergy-posting-tool.streamlit.app
- Wait 30–60 seconds for Streamlit to redeploy
- Refresh the page

## Next Steps
- Fetch and display Opportunities (ask Dan for Power Query M code for opportunities first)
- Create new opportunities via API
- Add products to opportunities, fill variables, post back

## Session Log

### Session 1 — April 15, 2026
- Set up project instructions in Claude
- Created PROGRESS.md
- Built API key auth screen
- Discovered correct auth header (`Api-Key`) and endpoint (`/api/employees`) from Power Query M code
- Got employee table working and displaying in Streamlit ✅
- Applied Innergy color scheme (white, navy, orange #E8500A) ✅
- Added Innergy logo inline next to title text ✅
- Added Welcome + company name banner using `/api/ourCompanyInfo/settings` ✅
- Learned git push/pull workflow including how to fix rejected pushes
- Tried browser local storage for persistent login — did not work reliably, removed it
