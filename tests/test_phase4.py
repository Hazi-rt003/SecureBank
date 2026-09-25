"""
Run this against your OWN running server to confirm Phase 4 (fraud
protection) works end-to-end on your real Postgres DB.

Requires: pip install requests pyjwt (pyjwt only used here to peek at the
token payload for verification -- your app itself doesn't need it, jose
is used there instead).

IMPORTANT: run this against a server you just applied the Phase 4
migration to. Old tokens from before this update will already be dead --
that's expected, not a bug (see the jti explanation from earlier).

Usage: python test_phase4.py
"""
import time
import requests
import jwt as pyjwt

BASE = "http://localhost:8000"

DAVE = {"full_name": "Dave Phase4", "email": "dave.phase4@example.com",
        "phone_number": "+254700666666", "password": "pass1234"}
EVE = {"full_name": "Eve Phase4", "email": "eve.phase4@example.com",
       "phone_number": "+254700777777", "password": "pass1234"}


def register(user):
    r = requests.post(f"{BASE}/users/register", json=user)
    print(f"register {user['email']}: {r.status_code}")


def login(email, password):
    r = requests.post(f"{BASE}/users/login", data={"username": email, "password": password})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


print("=== SETUP ===")
register(DAVE)
register(EVE)
dave_token = login(DAVE["email"], DAVE["password"])
eve_token = login(EVE["email"], EVE["password"])
h_dave = {"Authorization": f"Bearer {dave_token}"}
h_eve = {"Authorization": f"Bearer {eve_token}"}

dave_acct = requests.get(f"{BASE}/accounts/me", headers=h_dave).json()
eve_acct = requests.get(f"{BASE}/accounts/me", headers=h_eve).json()
print("dave account:", dave_acct)


print("\n=== SESSION MANAGEMENT ===")
payload = pyjwt.decode(dave_token, options={"verify_signature": False})
assert "jti" in payload, "FAIL: jti missing from token"
print("PASS: token has a jti claim ->", payload["jti"][:12], "...")

sessions = requests.get(f"{BASE}/users/sessions", headers=h_dave).json()
current = [s for s in sessions if s["is_current"]]
assert len(current) == 1, "FAIL: expected exactly one is_current=True session"
print(f"PASS: {len(sessions)} session(s) listed, current one correctly flagged")

# Second login -> second session
dave_token2 = login(DAVE["email"], DAVE["password"])
h_dave2 = {"Authorization": f"Bearer {dave_token2}"}

check_before = requests.get(f"{BASE}/users/me", headers=h_dave)
assert check_before.status_code == 200

revoke = requests.post(f"{BASE}/users/sessions/revoke-others", headers=h_dave2)
print("revoke-others response:", revoke.json())

check_old = requests.get(f"{BASE}/users/me", headers=h_dave)
check_new = requests.get(f"{BASE}/users/me", headers=h_dave2)
assert check_old.status_code == 401, f"FAIL: old session should be dead, got {check_old.status_code}"
assert check_new.status_code == 200, f"FAIL: calling session should survive, got {check_new.status_code}"
print("PASS: old session killed (401), calling session survives (200)")

logout = requests.post(f"{BASE}/users/logout", headers=h_dave2)
after_logout = requests.get(f"{BASE}/users/me", headers=h_dave2)
assert after_logout.status_code == 401, "FAIL: token should be dead after logout"
print("PASS: logout kills the session, token now rejected")

# Get a fresh token for the rest of the script
dave_token = login(DAVE["email"], DAVE["password"])
h_dave = {"Authorization": f"Bearer {dave_token}"}


print("\n=== AUDIT LOGS ===")
logs = requests.get(f"{BASE}/audit-logs/", headers=h_dave).json()
actions = [entry["action"] for entry in logs]
print(f"{len(logs)} audit entries, actions seen:", set(actions))
assert "register" in actions or "login_success" in actions, "FAIL: expected register/login events in audit log"
print("PASS: audit log contains expected event types")


print("\n=== RISK SCORING ===")
tx_small = requests.post(f"{BASE}/transactions/", headers=h_dave, json={
    "recipient_account_number": eve_acct["account_number"], "amount": "50.00"
}).json()
print(f"small tx: risk_score={tx_small['risk_score']} risk_level={tx_small['risk_level']}")

tx_large = requests.post(f"{BASE}/transactions/", headers=h_dave, json={
    "recipient_account_number": eve_acct["account_number"], "amount": str(dave_acct["balance"])
}).json()
print(f"large tx (full balance): risk_score={tx_large['risk_score']} risk_level={tx_large['risk_level']}")
assert tx_large["risk_score"] > tx_small["risk_score"], "FAIL: larger transaction should score higher risk"
print("PASS: larger transaction correctly scores higher risk")
assert tx_large["status"] == "pending_approval", "FAIL: high-risk tx should still be pending, not auto-completed"
print("PASS: high-risk transaction is pending_approval, not completed")


print("\n=== RATE LIMITING ===")
print("Hitting /users/login 7 times rapidly with a wrong password...")
statuses = []
for i in range(7):
    r = requests.post(f"{BASE}/users/login", data={
        "username": DAVE["email"], "password": "definitely-wrong"
    })
    statuses.append(r.status_code)
print("statuses:", statuses)
assert 429 in statuses, "FAIL: expected a 429 somewhere in there -- rate limiting may not be active"
print(f"PASS: rate limit triggered (429 appeared after {statuses.index(429)} requests)")

print("\n=== ALL CHECKS PASSED ===")