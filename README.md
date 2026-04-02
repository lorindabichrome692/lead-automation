# Lead Capture & Follow-Up Automation System

An end-to-end lead automation system that captures leads from a web form and WhatsApp, qualifies them using Claude AI (scoring 1-100), stores them in Airtable CRM, triggers automated follow-up emails, and displays everything on a real-time Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29-red)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange)
![Airtable](https://img.shields.io/badge/Airtable-CRM-blue)
![Resend](https://img.shields.io/badge/Resend-Email-purple)

---

## Architecture

```
Web Form / WhatsApp
        │
        ▼
  FastAPI Backend
        │
        ├──► Claude API (Lead Scoring 1-100)
        │
        ├──► Airtable CRM (Store lead + score)
        │
        └──► Resend Email (hot: immediate, warm: 24h, cold: 7d)
                    │
                    ▼
        Streamlit Dashboard (real-time KPIs + table + detail)
```

---

## Features

- **Lead Capture** — Web form (HTML/Tailwind) + WhatsApp webhook simulation
- **AI Qualification** — Claude Sonnet scores leads 1-100 and labels hot/warm/cold
- **CRM Integration** — All leads stored in Airtable with full metadata
- **Smart Follow-ups** — Automated emails via Resend (hot: instant, warm: 24h, cold: 7 days)
- **Live Dashboard** — Streamlit dashboard with KPIs, charts, filters, and lead detail view
- **APScheduler** — Background job scheduler for delayed email delivery

---

## Cost Breakdown

| Service | Plan | Cost | Limits |
|---------|------|------|--------|
| Claude API | Pay-as-you-go | ~$0.003-0.01/lead | Usage-based |
| Airtable | Free | $0 | 1,000 records/base |
| Resend | Free | $0 | 3,000 emails/month |
| Render | Free | $0 | 750 hours/month |
| **Total** | | **~$0/month** | |

---

## Project Structure

```
lead-automation/
├── app/
│   ├── main.py              # FastAPI app, CORS, APScheduler lifespan
│   ├── config.py            # pydantic-settings (.env loader)
│   ├── routers/
│   │   ├── leads.py         # POST /api/lead, POST /api/whatsapp-webhook
│   │   └── health.py        # GET /health
│   ├── services/
│   │   ├── qualification.py # Claude API lead scoring
│   │   ├── crm.py           # Airtable CRUD operations
│   │   ├── email_service.py # Resend email sending + Jinja2 templates
│   │   └── followup.py      # Follow-up logic & APScheduler jobs
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── templates/
│       ├── hot_lead.html
│       ├── warm_lead.html
│       └── cold_lead.html
├── frontend/
│   └── index.html           # Lead capture form (Tailwind CSS)
├── dashboard/
│   └── app.py               # Streamlit dashboard
├── tests/
│   ├── test_api.py
│   ├── test_qualification.py
│   ├── test_crm.py
│   └── test_whatsapp.py
├── .streamlit/
│   └── config.toml          # Dark theme
├── .env.example
├── requirements.txt
├── render.yaml
├── Procfile
└── README.md
```

---

## Local Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd lead-automation
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs
```

### 4. Run the dashboard

```bash
streamlit run dashboard/app.py
# Dashboard at http://localhost:8501
```

### 5. Open the web form

Open `frontend/index.html` in your browser.

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | `sk-ant-...` |
| `AIRTABLE_API_KEY` | Airtable Personal Access Token | `pat...` |
| `AIRTABLE_BASE_ID` | Airtable Base ID | `appXXXXXXXX` |
| `AIRTABLE_TABLE_NAME` | Table name | `Leads` |
| `RESEND_API_KEY` | Resend API key | `re_...` |
| `RESEND_FROM_EMAIL` | Sender email | `onboarding@resend.dev` |
| `APP_ENV` | Environment | `development` |

---

## API Endpoints

### `POST /api/lead`
Submit a lead from the web form.

```json
{
  "name": "Jane Smith",
  "email": "jane@company.com",
  "phone": "+1 555 123 4567",
  "company": "Acme Corp",
  "sector": "Technology",
  "message": "We need a CRM solution for our 50-person team.",
  "source": "web_form"
}
```

**Response:**
```json
{
  "id": "recXXXXXXXXXXXXXX",
  "status": "received",
  "score": {
    "score": 85,
    "label": "hot",
    "reason": "...",
    "suggested_response": "..."
  }
}
```

### `POST /api/whatsapp-webhook`
Simulate an incoming WhatsApp message.

```json
{
  "from": "+905551234567",
  "name": "John Doe",
  "message": "Hi, I'm interested in your automation services.",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### `GET /health`
```json
{"status": "ok", "version": "1.0.0"}
```

---

## Lead Scoring

Claude AI scores leads 1-100 based on:

| Criteria | Points |
|----------|--------|
| Budget mentioned or implied | +20 |
| Urgent need expressed | +20 |
| Decision maker indicators | +15 |
| Clear/specific request | +15 |
| Company name provided | +10 |
| Relevant sector | +10 |
| Professional tone | +10 |

**Labels:** hot (≥70) · warm (40-69) · cold (<40)

**Follow-up timing:** hot → immediate · warm → 24 hours · cold → 7 days

---

## Airtable Setup

Create a base called `Lead Automation` with a table `Leads` and these fields:

| Field | Type |
|-------|------|
| Name | Single line text |
| Email | Email |
| Phone | Phone number |
| Company | Single line text |
| Sector | Single select |
| Message | Long text |
| Score | Number |
| Label | Single select: hot, warm, cold |
| Reason | Long text |
| SuggestedResponse | Long text |
| Source | Single select: web_form, whatsapp, email |
| Status | Single select: new, contacted, follow_up_scheduled, converted, lost |
| FollowUpCount | Number |
| LastContactedAt | Date |

---

## Deploy to Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

### 2. Deploy on Render

1. Go to [render.com](https://render.com) → New → Blueprint
2. Connect your GitHub repo
3. Render will detect `render.yaml` and create both services automatically
4. Set environment variables in Render dashboard for each service

### 3. Update frontend API URL

After deployment, update `API_URL` in `frontend/index.html` to your Render backend URL:
```js
const API_URL = 'https://lead-automation-api.onrender.com/api/lead';
```

---

## Running Tests

```bash
# Phase 1: API tests (requires server running)
python -m tests.test_api

# Phase 2: Claude qualification tests
python -m tests.test_qualification

# Phase 3: Airtable CRM tests
python -m tests.test_crm

# Phase 5: WhatsApp webhook tests (requires server running)
python -m tests.test_whatsapp
```

---

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) — Backend API framework
- [Anthropic Claude](https://www.anthropic.com/) — AI lead qualification
- [Airtable](https://airtable.com/) — CRM and data storage
- [Resend](https://resend.com/) — Transactional email
- [APScheduler](https://apscheduler.readthedocs.io/) — Background job scheduling
- [Streamlit](https://streamlit.io/) — Dashboard UI
- [Render](https://render.com/) — Cloud deployment
