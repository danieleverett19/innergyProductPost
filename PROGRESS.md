# Innergy Product Posting Tool — Progress Log

## Session 1 — Initial Build
- Built login screen with API key input
- Connected to Innergy API using Api-Key header
- Fetches company name from /api/ourCompanyInfo/settings
- Fetches and displays employee table with key columns
- Download as CSV button
- Disconnect button
- Innergy branding (logo, orange/navy color scheme)
- Frozen top bar with welcome message

## Session 2 — Create Opportunity (In Progress)
### What we built
- Create Opportunity button above employee table
- Form with fields: Opportunity Name, Bid Name, Win Probability, Target Margin, Projected Revenue, First/Last Delivery Date, Substantial Completion Date
- Facility auto-fetched from /api/opportunities at login
- Debug payload expander that persists after failed attempts

### What we learned about the API
- Base URL: https://app.innergy.com
- Create endpoint: POST /api/opportunities/create (plural, array payload)
- OR singular: POST /api/opportunity/create (single object)
- FacilityId must be sent — fetched from existing opportunities at login
- Field names for POST differ from GET responses:
  - POST uses: FirstDeliveryDate, LastDeliveryDate, SubstantialCompletionDate
  - GET returns: FirstDelivery, LastDelivery, SubstantialCompletion
  - POST uses: CurrentBidName (not CurrentBid)
  - POST uses: WinProbabilityPercentage (stored as decimal 0-1)
  - POST uses: TargetMarginPercentage (stored as decimal 0-1)
- BidType on GET is plain text "Actual" or "Budget"
- BidTypeId on POST requires a GUID — source unknown
- BidTypeId is NOT in the dictionary endpoint
- BidTypeId is NOT returned on existing opportunities via GET
- Sending BidType as plain text is rejected
- Sending BidTypeId as generated UUID is rejected
- Sending without BidTypeId gives "Bid Type can't be empty"

### Blocking issue
- BidTypeId GUID is required but source is unknown
- Not in /api/dictionary
- Not returned by GET /api/opportunities
- Need to find where Innergy exposes these GUIDs
- Recommended next step: Contact Innergy support and ask:
  "What endpoint or dictionary type returns BidType GUIDs for use in POST /api/opportunities/create?"

## What's Not Built Yet
- Opportunity creation (blocked on BidTypeId)
- Fetch and display existing opportunities list
- Products: add to opportunities, fill variables, post back
