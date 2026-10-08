"""
One-off: create every table straight from your SQLAlchemy models.

Run from the project root with .env pointing at the database you want to
set up (Neon, in this case):

    python init_schema.py

It prints the host it connected to BEFORE doing anything, so you can see
whether it is Neon (host contains "neon.tech") or your local Postgres.
"""
import app.models  # noqa: F401  -- importing registers all tables on Base.metadata
from app.database.database import Base, engine

print("Target database:", engine.url.render_as_string(hide_password=True))

Base.metadata.create_all(bind=engine)

print("Tables defined by the models:")
for name in sorted(Base.metadata.tables):
    print("  -", name)
print("Done. Now check the tables in the Neon console before stamping.")