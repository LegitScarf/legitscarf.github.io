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
```

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

## Railway Deployment

Railway is the better fit for the current app because this project is a stateful FastAPI server that serves both HTML and API routes and currently stores data in SQLite by default.

This repo includes [railway.toml](c:/Users/KIIT/Desktop/NexAlpha/railway.toml) so Railway can start the app with:

```text
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

### Deploy Steps

1. Push the repo to GitHub.
2. In Railway, create a new project from the GitHub repo.
3. Add a `Volume` and mount it at:

```text
/app/backend/data
```

4. Set these environment variables in Railway:

```env
APP_NAME=NexAlpha FastAPI
APP_BASE_URL=https://your-railway-domain.up.railway.app
API_BASE_URL=https://your-railway-domain.up.railway.app/api
SECRET_KEY=replace-this-with-a-long-random-secret
SESSION_COOKIE_NAME=nexalpha_session
SESSION_TTL_MINUTES=10080
SESSION_COOKIE_SECURE=true
VERIFICATION_TOKEN_TTL_HOURS=48
CORS_ORIGINS=https://your-railway-domain.up.railway.app
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD=change-me-now
BOOTSTRAP_ADMIN_NAME=NexAlpha Admin
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your-brevo-login
SMTP_PASSWORD=your-brevo-smtp-key
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-verified-sender@example.com
SMTP_FROM_NAME=NexAlpha
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
RAZORPAY_PLAN_ID=
RAZORPAY_WEBHOOK_SECRET=
```

5. Redeploy the service.
6. Open the generated Railway domain and test:
   - `/`
   - `/register.html`
   - `/login.html`
   - `/api/health`

### Notes

- If `DATABASE_URL` is not set, the app now automatically uses `RAILWAY_VOLUME_MOUNT_PATH/nexalpha.db` when Railway provides a mounted volume path.
- For a more production-grade setup later, move from SQLite to Postgres.

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
