# SecureBank

A security-focused digital banking backend and dashboard, built to explore what real banking-grade authentication, fraud protection, and session security look like in practice — not just a CRUD app with a login screen bolted on.

**Live demo:** _deployment in progress — link coming soon_
**Repo:** https://github.com/Hazi-rt003/SecureBank

---

## Project status

| Phase | Scope | Status |
|---|---|---|
| 1 | Project structure — FastAPI, PostgreSQL, SQLAlchemy, Alembic | ✅ Done |
| 2 | Registration, login, password hashing, JWT auth | ✅ Done |
| 3 | Trusted devices, passkey (WebAuthn) verification, push approval for transactions, login notifications, device fingerprinting | ✅ Done |
| 4 | Audit logs, transaction risk scoring, rate limiting, session management | ✅ Done |
| 5 | React web dashboard | ✅ Done |
| 6 | Docker, HTTPS, cloud deployment | 🔨 In progress |

This is an actively developed learning project. Some design choices below are explicitly flagged as placeholders rather than production-grade decisions — see [Known limitations](#known-limitations).

---

## Why this project exists

Most "banking app" tutorials stop at JWT auth. SecureBank goes further into the parts that actually matter for protecting an account:

- **A device being logged in isn't the same as a device being trusted.** Trust is earned by registering a passkey — a real WebAuthn credential bound to that device's hardware — not just by having a valid session token.
- **Moving money requires more than being logged in.** Every transaction starts `pending_approval` and only completes once it's explicitly approved from a *trusted* device, regardless of which device initiated it.
- **A stolen JWT shouldn't be forever.** Sessions are tracked server-side and can be revoked individually or all-at-once ("log out everywhere"), even though the token itself hasn't expired yet.
- **Risk is scored, not assumed.** Every transaction gets a rule-based risk score (amount vs. balance, new recipient, untrusted device) that's visible in the audit trail, even though — by design — every transaction already requires trusted-device approval regardless of its score.

---

## Architecture

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────┐
│  React Dashboard     │  HTTPS  │  FastAPI Backend      │  SQL    │  PostgreSQL │
│  (Vite + TS +        │ ──────▶ │  (Python)              │ ──────▶ │             │
│   Tailwind v4)        │         │                        │         │             │
└─────────────────────┘         └──────────┬─────────────┘         └─────────────┘
                                             │
                                             │ SMTP            Browser WebAuthn API
                                             ▼                 (passkeys, no server
                                    Login notification emails   round-trip for biometrics)
```

**Backend:** FastAPI, SQLAlchemy 2.0, Alembic migrations, PostgreSQL, JWT (python-jose), passlib/bcrypt for password hashing, the `webauthn` library for passkey registration/authentication ceremonies, `slowapi` for rate limiting.

**Frontend:** React 19 + TypeScript, Vite, React Router, Tailwind CSS v4. Talks to the backend purely over the REST API defined below — no server-side rendering, no shared backend code.

---

## Core security features

### Passkeys instead of OTP
Rather than SMS/email one-time codes, device trust and login step-up are both backed by real WebAuthn passkeys — platform authenticators (Face ID, Windows Hello, Google Password Manager) or hardware security keys. A device only becomes "trusted" once it successfully completes a passkey registration ceremony; a manual trust toggle exists for development but should not be exposed in production (see [Known limitations](#known-limitations)).

### Push approval for transactions
Initiating a transaction never moves money immediately. It creates a `pending_approval` record, and only a call to `/transactions/{id}/approve` **from a trusted device** (verified via the device's fingerprint) can complete it. There is currently no mobile app to deliver a real push notification for this — see [Known limitations](#known-limitations).

### Session revocation
Every login creates a server-side session row tied to a unique `jti` claim embedded in the JWT. Logging out, revoking a specific session, or "log out other devices" all work by marking that row revoked — the next request bearing that token is rejected even though the token itself hasn't expired.

### Transaction risk scoring
A simple rule-based scorer (0–100) weighs: amount as a percentage of balance, absolute amount, whether the recipient has ever successfully received a completed transaction before, and whether the initiating device is trusted. The resulting `risk_level` (LOW/MEDIUM/HIGH) is stored and surfaced in the dashboard and audit log — it labels risk for visibility rather than gating approval differently, since every transaction already requires trusted-device approval regardless of score.

### Audit trail
Registration, login success/failure, device trust/revoke, and every transaction state change are logged with a timestamp, action type, and (where available) the device fingerprint involved. Viewable per-user at `GET /audit-logs/`.

### Rate limiting
Login (5/min), registration (3/hour), and transaction initiate/approve/reject (20/min and 10/min respectively) are all rate-limited per IP, counting failed attempts — not just successful ones — to resist brute-force attempts.

---

## Getting started

### Backend

```bash
git clone https://github.com/Hazi-rt003/SecureBank.git
cd SecureBank
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the values below
alembic upgrade head
uvicorn app.main:app --reload
```

API docs (Swagger UI) are then available at `http://localhost:8000/docs`.

### Frontend

```bash
cd securebank-dashboard
npm install
cp .env.example .env   # defaults to http://localhost:8000
npm run dev
```

### Environment variables (backend)

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/securebank` |
| `SECRET_KEY` | JWT signing secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` | |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT/session lifetime | `30` |
| `WEBAUTHN_RP_ID` | Must exactly match your domain (`localhost` for local dev) | `localhost` |
| `WEBAUTHN_RP_NAME` | Display name shown in passkey prompts | `SecureBank` |
| `WEBAUTHN_ORIGIN` | Full origin the browser is served from | `http://localhost:8000` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` | Login notification emails. Omit to disable — login still works, emails just don't send | |
| `STARTING_ACCOUNT_BALANCE` | Demo balance seeded on registration (placeholder — see limitations) | `1000.00` |
| `DEFAULT_CURRENCY` | | `KES` |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:5173` |

### Environment variables (frontend)

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend URL the dashboard talks to |

---

## API overview

Full interactive documentation is auto-generated at `/docs`. Key endpoint groups:

- `POST /users/register`, `POST /users/login`, `POST /users/login/passkey/verify` — auth, including step-up
- `GET /users/sessions`, `POST /users/sessions/{id}/revoke`, `POST /users/sessions/revoke-others`, `POST /users/logout` — session management
- `GET /devices/`, `POST /devices/register`, `GET/POST /devices/{id}/trust/passkey/*` — device trust via passkeys
- `GET /accounts/me` — account balance
- `POST /transactions/`, `GET /transactions/pending`, `POST /transactions/{id}/approve`, `POST /transactions/{id}/reject` — transactions
- `GET /audit-logs/` — security event history

---

## Known limitations

These are deliberate, documented scope decisions for a learning project — not oversights:

- **The manual device-trust endpoint (`POST /devices/{id}/trust`) bypasses passkey verification.** It exists for local testing and development convenience. It should be removed or locked down before any public deployment, since it lets a device become "trusted" without ever proving possession of a passkey.
- **Push notifications for transaction approval are stubbed to a log line**, not real FCM/APNs delivery — there's no mobile app yet to receive a real push.
- **The demo starting balance (`STARTING_ACCOUNT_BALANCE`) is seeded automatically on registration.** There's no real deposit/funding flow yet; this exists purely so the transaction flow is testable end-to-end.
- **Real device fingerprinting is deferred to the mobile app build.** The current fingerprint is a persisted random browser ID, not a derived hardware/browser characteristic fingerprint.
- **Rate limiting uses in-memory storage**, which only works correctly behind a single server process — fine for the current deployment target, but would need Redis-backed storage before scaling horizontally.

---

## Roadmap

- [ ] Flutter mobile app, with real device fingerprinting and real push notifications
- [ ] Complete Phase 6 deployment (Docker, HTTPS via Let's Encrypt, cloud hosting)
- [ ] Remove/lock down the manual device-trust bypass before any public-facing deployment