"""
Run this against your OWN running server (uvicorn app.main:app --reload)
to confirm push approval for transactions works end-to-end on your real
Postgres DB. Requires: pip install requests (if not already installed).

Usage: python test_push_approval.py
"""
import requests

BASE = "http://localhost:8000"

# --- adjust these to two real users in your DB, or let this register fresh ones ---
ALICE = {"full_name": "Alice Test", "email": "alice.pushtest@example.com",
         "phone_number": "+254700111111", "password": "pass1234"}
BOB = {"full_name": "Bob Test", "email": "bob.pushtest@example.com",
       "phone_number": "+254700222222", "password": "pass1234"}


def register(user):
    r = requests.post(f"{BASE}/users/register", json=user)
    print("register:", r.status_code, r.json())


def login(email, password):
    r = requests.post(f"{BASE}/users/login", data={"username": email, "password": password})
    print("login:", r.status_code, r.json())
    return r.json()["access_token"]


register(ALICE)
register(BOB)

alice_token = login(ALICE["email"], ALICE["password"])
bob_token = login(BOB["email"], BOB["password"])
h_alice = {"Authorization": f"Bearer {alice_token}"}
h_bob = {"Authorization": f"Bearer {bob_token}"}

alice_acct = requests.get(f"{BASE}/accounts/me", headers=h_alice).json()
bob_acct = requests.get(f"{BASE}/accounts/me", headers=h_bob).json()
print("alice account:", alice_acct)
print("bob account:", bob_acct)

# 1. Initiate a transaction
tx = requests.post(f"{BASE}/transactions/", headers=h_alice, json={
    "recipient_account_number": bob_acct["account_number"], "amount": "200.00"
}).json()
print("initiated tx:", tx)
tx_id = tx["id"]

# 2. Try approving with no device fingerprint -> should be 400
r = requests.post(f"{BASE}/transactions/{tx_id}/approve", headers=h_alice)
print("approve, no fingerprint:", r.status_code, r.json())

# 3. Register a device (untrusted by default)
dev = requests.post(f"{BASE}/devices/register", headers=h_alice, json={
    "device_name": "Test Phone", "device_id": "push-test-device-1",
    "device_type": "mobile", "device_fingerprint": "fp-push-test-1", "platform": "android"
}).json()
print("registered device:", dev)

# 4. Try approving with the UNTRUSTED device -> should be 403
r = requests.post(f"{BASE}/transactions/{tx_id}/approve", headers={
    **h_alice, "X-Device-Fingerprint": "fp-push-test-1"
})
print("approve, untrusted device:", r.status_code, r.json())

# 5. Manually trust it (stand-in for the passkey ceremony)
r = requests.post(f"{BASE}/devices/{dev['id']}/trust", headers=h_alice)
print("trust device:", r.status_code, r.json())

# 6. Approve for real
r = requests.post(f"{BASE}/transactions/{tx_id}/approve", headers={
    **h_alice, "X-Device-Fingerprint": "fp-push-test-1"
})
print("approve, trusted device:", r.status_code, r.json())

# 7. Confirm balances moved
print("alice balance after:", requests.get(f"{BASE}/accounts/me", headers=h_alice).json())
print("bob balance after:", requests.get(f"{BASE}/accounts/me", headers=h_bob).json())