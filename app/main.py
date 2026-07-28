from fastapi import FastAPI
from sqlalchemy import text

from app.api.devices import router as devices_router
from app.api.users import router as users_router

from app.database.database import engine


app = FastAPI(
    title="SecureBank API",
    version="1.0.0",
)

app.include_router(users_router)
app.include_router(devices_router)


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