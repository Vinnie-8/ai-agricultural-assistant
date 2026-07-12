# Flask Frontend Setup

## 1. Create the project

This is a brand new, separate project from `backend` and `ai-service` —
give it its own folder and venv:

```bash
mkdir -p ~/Desktop/2026-AI-PROJECT/ai-agricultural-assistant/frontend
cd ~/Desktop/2026-AI-PROJECT/ai-agricultural-assistant/frontend
uv venv
source .venv/bin/activate
```

Copy all files from this scaffold into that folder, preserving structure:
```
frontend/
├── app.py
├── requirements.txt
├── .env.example
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── diagnosis.html
└── static/
    └── css/
        └── style.css
```

## 2. Install dependencies

```bash
uv pip install -r requirements.txt
```

## 3. Set up your .env

```bash
cp .env.example .env
```

Generate a real secret key (same technique as your backend's `SECRET_KEY`):
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Paste that into `FLASK_SECRET_KEY` in `.env`.

`BACKEND_URL` should already be correct (`http://127.0.0.1:8000`) if your
backend runs on the default port.

## 4. Run all three services

You now have three separate processes to run, each in its own terminal:

**Terminal 1 — AI service:**
```bash
cd ai-service && uvicorn app.main:app --reload --port 8001
```

**Terminal 2 — Backend:**
```bash
cd backend && uvicorn app.main:app --reload --port 8000
```

**Terminal 3 — Frontend:**
```bash
cd frontend && python app.py
```

## 5. Use it

Open **http://127.0.0.1:5000** in your browser.

Flow:
1. Register a new account (or log in if you already have one from earlier
   testing — e.g. `vinnie2@example.com`)
2. You'll land on the upload page — choose a leaf photo and click Diagnose
3. See the crop/disease/confidence/recommendation result
4. Ask the chat assistant follow-up questions right below it — each
   response is grounded in your knowledge base and this specific diagnosis

## How auth works here

- On login, the backend's `access_token` and `refresh_token` are stored in
  the Flask **session** (a signed cookie) — not a database, so this is
  simple and fine for a project, but sessions reset if you clear cookies
  or restart with a different `FLASK_SECRET_KEY`.
- Every backend call from Flask attaches `Authorization: Bearer <token>`
  automatically via the `auth_headers()` helper.
- There's no refresh-token flow wired in yet — if the access token expires
  (default 30 minutes per your backend config) mid-session, you'll start
  getting 401s and need to log in again. Fine for a demo; a production
  version would silently refresh using the refresh token instead.

## Known simplifications (fine for a project, not production)

- Chat history is only kept in the Flask session (in memory via cookie),
  not fetched from the backend's `chat_history` table — so refreshing
  after closing the browser loses the visible conversation, even though
  it's still safely stored in Postgres.
- Only one diagnosis is "active" at a time per browser session — there's
  no page to browse past diagnoses yet.
- No client-side JS/AJAX — every action is a full page reload (form
  POST → redirect). Simple and reliable, just not as snappy as a JS-driven
  UI would be.
