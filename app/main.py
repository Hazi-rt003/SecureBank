import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.limiter import limiter

from app.api.devices import router as devices_router
from app.api.users import router as users_router
from app.api.passkeys import router as passkeys_router
from app.api.webauthn_test_page import router as webauthn_test_router
from app.api.transactions import router as transactions_router
from app.api.accounts import router as accounts_router
from app.api.audit import router as audit_router

from app.database.database import engine


app = FastAPI(
    title="SecureBank API",
    version="1.0.0",
)

# Comma-separated list in .env, e.g. CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
# Defaults cover Vite's dev server on both hostnames it might report.
_default_origins = "http://localhost:5173,http://127.0.0.1:8000"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # auth is a Bearer token, not cookies -- no credentials needed
    allow_methods=["*"],
    allow_headers=["*"],  # must include our custom X-Device-Fingerprint etc. headers
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(users_router)
app.include_router(devices_router)
app.include_router(passkeys_router)
app.include_router(webauthn_test_router)
app.include_router(transactions_router)
app.include_router(accounts_router)
app.include_router(audit_router)


@app.get("/")
def home():
    return {"message": "SecureBank API is running!"}


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))#confirm if PostgreSQL is working.
        return {
            "database": "Connected",
            "api": "Running"
        }
    except Exception as e:
        return {
            "database": "Disconnected",
            "error": str(e)
        }