from slowapi import Limiter
from slowapi.util import get_remote_address

# storage_uri="memory://" is explicit on purpose: in-memory works for a
# single process now. Swapping to Redis later (per-request rate limits
# shared across multiple server processes) is a one-line change here —
# storage_uri="redis://localhost:6379" — nothing else in the app changes.
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")