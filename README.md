# NexAlpha

NexAlpha is a gated-access product site for OptiTrade and BharatAlpha. The project now runs on a FastAPI backend that serves the static frontend, handles authentication, tracks approval state, and syncs billing state from Razorpay.

## Current Stack

- Frontend: HTML, CSS, vanilla JavaScript
- Backend: FastAPI
- Database: SQLAlchemy with SQLite by default
- Auth: FastAPI cookie session + hashed passwords
- Billing: Razorpay subscriptions
- Product apps: Streamlit

## User Flow

1. User registers on `register.html`
2. User verifies email with the FastAPI verification link
3. Admin approves the account
4. Approved user starts the Razorpay subscription
5. Razorpay webhook updates subscription/payment state
6. Active users launch either app through `access.html`

## Repository Layout

```text
nexalpha/
├── index.html
├── login.html
├── register.html
├── account.html
├── access.html
├── admin.html
├── assets/
│   ├── css/
│   └── js/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── config.py
│       ├── database.py
│       ├── dependencies.py
│       ├── main.py
│       ├── models.py
│       ├── routers/
│       ├── schemas.py
│       ├── security.py
│       └── services/
└── supabase/
```

`supabase/` is kept as legacy reference material from the previous implementation. The active runtime now lives in `backend/`.

## Local Development

Install Python 3.11+ first, then:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
uvicorn backend.app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

FastAPI serves the frontend pages and the `/api/*` routes from the same origin by default.

## Configuration

Frontend runtime configuration lives in `assets/js/config.js`.

```js
window.NEXALPHA_CONFIG = Object.freeze({
  appBaseUrl: "",
  apiBaseUrl: "",
  billing: {
    amountInr: 500,
    interval: "month"
  },
  products: {
    optitrade: {
      name: "OptiTrade",
      appUrl: "https://optitrade-nexalpha.streamlit.app/"
    },
    bharatalpha: {
      name: "BharatAlpha",
      appUrl: "https://bharatalpha-nexalpha.streamlit.app/"
    }
  }
});
```

Leave `appBaseUrl` and `apiBaseUrl` blank when FastAPI serves everything from the same origin. Set them only if the frontend and backend are deployed separately.

Backend environment variables live in `backend/.env.example`. Important ones:

- `SECRET_KEY`
- `DATABASE_URL`
- `BOOTSTRAP_ADMIN_EMAIL`
- `BOOTSTRAP_ADMIN_PASSWORD`
- `ENABLE_DEV_TOOLS`
- `DEV_ADMIN_TOKEN`
- `SMTP_*`
- `RAZORPAY_KEY_ID`
- `RAZORPAY_KEY_SECRET`
- `RAZORPAY_PLAN_ID`
- `RAZORPAY_WEBHOOK_SECRET`

If SMTP is not configured, registration returns a verification preview link so the flow still works locally.

## FastAPI Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/session`
- `GET /verify-email`
- `GET /api/account/status`
- `POST /api/billing/create-subscription`
- `GET /api/admin/users`
- `POST /api/admin/approve-user`
- `POST /api/dev/promote-admin`
- `POST /api/webhooks/razorpay`
- `GET /api/health`

## Local Admin Promotion

If you need to promote an existing local account to admin without resetting the database:

1. Set these in `backend/.env`:

```env
ENABLE_DEV_TOOLS=true
DEV_ADMIN_TOKEN=pick-a-long-random-string
```

2. Restart FastAPI.

3. Run this from PowerShell:

```powershell
$headers = @{ "Content-Type" = "application/json"; "X-Dev-Admin-Token" = "pick-a-long-random-string" }
$body = '{ "email": "your-user@example.com" }'
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/dev/promote-admin" -Headers $headers -Body $body
```

That marks the user as `admin`, sets approval to `approved`, and allows access to `admin.html`.

## Notes

- One `Rs 500/month` subscription unlocks both apps.
- The admin approval rule still requires verified email before approval.
- Direct Streamlit app URLs are not fully protected unless those apps also validate NexAlpha entitlement server-side.

## Disclaimer

This project is for informational purposes only and does not constitute financial advice. Trading in Futures and Options involves significant risk of loss.
