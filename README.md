# WhatsApp Booking Assistant

A conversational AI appointment booking assistant powered by Claude that operates through WhatsApp Business messaging. It uses Google Sheets as a persistent memory database and Gmail for email confirmations.

## Architecture

```
WhatsApp Message
       │
       ▼
  Express Webhook (/webhook)
       │
       ▼
  Step 1: Lead Memory (Google Sheets)
  ├── Existing lead → retrieve history
  └── New lead → create record
       │
       ▼
  Step 2: Knowledge Base Retrieval
  (services, hours, pricing, FAQs, policies)
       │
       ▼
  Step 3: Claude AI Conversation
  (tool-use for availability checks & bookings)
       │
       ▼
  Step 4: Appointment Scheduling
  (slot generation, availability, booking)
       │
       ▼
  Step 5: WhatsApp Confirmation
  (send response via WhatsApp Business API)
       │
       ▼
  Step 6: Email Confirmation (Gmail)
  (send booking details to lead's email)
```

## Project Structure

```
src/
├── app.js                    # Express server entry point
├── config/
│   ├── index.js              # Environment configuration
│   └── knowledge-base.js     # Company services, hours, FAQs, policies
├── modules/
│   ├── conversation.js       # Claude AI engine with tool use
│   ├── email.js              # Gmail confirmation sender
│   ├── scheduler.js          # Time slot generation & availability
│   ├── sheets.js             # Google Sheets CRUD (leads, messages, bookings)
│   └── whatsapp.js           # WhatsApp Business API client
├── routes/
│   └── webhook.js            # Webhook verification & message handler
tests/
├── knowledge-base.test.js
├── scheduler.test.js
└── whatsapp.test.js
```

## Setup

### Prerequisites

- Node.js >= 20
- A WhatsApp Business API account with a phone number
- A Google Cloud service account with Sheets API access
- An Anthropic API key
- A Gmail account with an app password (or OAuth)

### Google Sheets Setup

Create a spreadsheet with three sheets:

1. **Leads** — columns: `phone | name | email | status | createdAt | updatedAt`
2. **Messages** — columns: `phone | role | content | timestamp`
3. **Bookings** — columns: `phone | service | date | time | status | createdAt`

Add header rows and share the spreadsheet with your service account email.

### Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### Install & Run

```bash
npm install
npm start
```

For development with auto-reload:

```bash
npm run dev
```

### Expose the Webhook

Use a tunnel (e.g., ngrok) to expose your local server:

```bash
ngrok http 3000
```

Set the webhook URL in your WhatsApp Business API configuration to:
`https://your-ngrok-url/webhook`

## Testing

```bash
npm test
```

## How It Works

1. **Incoming message** arrives at the `/webhook` POST endpoint
2. The system looks up or creates a **lead** in Google Sheets by phone number
3. **Message history** is loaded from the Messages sheet for conversation context
4. Claude generates a response using the **knowledge base** and **tool use** (availability checks, booking creation, lead updates)
5. The response is sent back via **WhatsApp Business API**
6. If a booking was created, a **confirmation email** is sent via Gmail

### Returning vs New Leads

- **New leads** are warmly welcomed; the assistant tries to learn their name
- **Returning leads** are greeted by name with awareness of their booking history

### Claude Tool Use

The assistant has access to four tools:

| Tool | Purpose |
|------|---------|
| `check_availability` | Query open slots for a given date |
| `book_appointment` | Create a confirmed booking |
| `update_lead_name` | Save the lead's name to Sheets |
| `update_lead_email` | Save the lead's email to Sheets |

## Customization

Edit `src/config/knowledge-base.js` to configure:

- Services offered (name, duration, price)
- Working hours per day of week
- Booking policies
- FAQs
- Company contact information
