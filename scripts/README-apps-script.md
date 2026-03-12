# Pipeline Tools — Google Apps Script Setup Guide

Automated workflow for your CRM/sales pipeline spreadsheet. Adds a **"Pipeline Tools"** menu to Google Sheets with filtering, sorting, cleanup, dashboard, and cross-sheet operations.

## Setup

### Step 1: Import your Excel file

1. Open [Google Sheets](https://sheets.google.com)
2. Go to **File > Import > Upload** and select your Excel file
3. Choose **"Replace spreadsheet"** or **"Create new spreadsheet"**

### Step 2: Rename the data sheet

1. Right-click the sheet tab at the bottom
2. Rename it to **`Pipeline`** (case-sensitive)

Your sheet should have these columns in order:
| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| Date | Brand Name | Type of Scope | Handled by | POC Name | Phone | Email | Stage | Costs | Proposal Date/Follow up | Status |

### Step 3: Add the script

1. In your Google Sheet, go to **Extensions > Apps Script**
2. Delete the default code in `Code.gs`
3. Copy the entire contents of `Code.gs` from this repository and paste it in
4. Click **Save** (Ctrl+S)
5. Close the Apps Script tab
6. **Reload** the Google Sheet (F5 or Ctrl+R)

### Step 4: Authorize

1. After reload, you'll see the **"Pipeline Tools"** menu in the menu bar
2. The first time you click any menu item, Google will ask you to authorize the script
3. Click **"Advanced" > "Go to Pipeline Tools (unsafe)"** > **"Allow"**
4. This is normal for custom scripts — the script only accesses your spreadsheet

## Features

### Filter & Sort

| Menu Item | What it does |
|-----------|-------------|
| Filter by Stage | Shows only rows matching a stage (First Call, Pitch, Commercials, Closed, Didnt work out) |
| Filter by Handled by | Shows only rows for Tan or Ally |
| Filter by Type of Scope | Shows only rows matching a scope type (partial match, e.g. "Web" matches "Branding, Web") |
| Sort by Cost | Sorts numerically; TBD/empty values go to the bottom |
| Sort by Date | Sorts chronologically; handles messy date formats like "14th Jan", "2nd March" |
| Sort by Stage | Sorts in pipeline progression order: First Call > Pitch > Commercials > Closed > Lost |
| Clear All Filters | Unhides all hidden rows |

### Dashboard

| Menu Item | What it does |
|-----------|-------------|
| Generate / Refresh Dashboard | Creates a "Dashboard" sheet with pipeline summary, revenue metrics, team performance, and scope breakdown |
| Go to Dashboard | Navigates to the Dashboard sheet |

Dashboard sections:
- **Pipeline Summary by Stage** — count, total value, average deal size per stage
- **Revenue Metrics** — closed revenue, active pipeline value, TBD count
- **Team Performance** — deals, closed count, closing rate %, and revenue per handler
- **Scope Type Breakdown** — count and value per scope type

### Cleanup

| Menu Item | What it does |
|-----------|-------------|
| Find Duplicate Brands | Highlights duplicate brand names in orange and lists them |
| Standardize Phone Numbers | Formats Indian mobile numbers as +91 XXXXX XXXXX |
| Clean Cost Values | Converts ₹ strings to sortable numbers; flags TBD values in yellow |
| Highlight Incomplete Rows | Marks empty Brand/Phone/Email/Stage cells in red |
| Run All Cleanup | Runs all four cleanup operations |

### Stage Sheets

| Menu Item | What it does |
|-----------|-------------|
| Generate All Stage Sheets | Creates/refreshes all three sheets below |
| Refresh Closed Deals | Green tab — all rows with Stage = "Closed" |
| Refresh Active Pipeline | Blue tab — First Call + Pitch + Commercials |
| Refresh Lost Deals | Red tab — "Didnt work out" |

Each generated sheet:
- Copies headers with formatting
- Has alternating row colors
- Is protected with a warning (edits are discouraged since the sheet auto-regenerates)
- Includes a note on cell A1 with last-updated timestamp

## Customization

Edit the `CONFIG` object at the top of `Code.gs`:

```javascript
// Change sheet name if yours is different
MAIN_SHEET: 'Pipeline',

// Add new stages
STAGES: ['First Call', 'Pitch', 'Commercials', 'Closed', 'Didnt work out'],

// Add new team members
HANDLERS: ['Tan', 'Ally'],

// Adjust column positions (1-based) if your layout differs
COL: { DATE: 1, BRAND: 2, SCOPE: 3, ... }
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Menu doesn't appear | Reload the sheet. If still missing, open Apps Script and re-save |
| "Sheet Pipeline not found" | Rename your data sheet tab to exactly `Pipeline` |
| Authorization error | Follow the authorization steps above; click "Advanced" to proceed |
| Dates not sorting correctly | The script handles "14th Jan" style dates. If your dates use a different format, they'll sort to the bottom |
| Costs showing as TBD | Run Cleanup > Clean Cost Values first to convert ₹ strings to numbers |
