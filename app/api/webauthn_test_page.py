from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>SecureBank — Passkey Test</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; }
  section { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
  h2 { margin-top: 0; font-size: 16px; }
  input { display: block; width: 100%; margin: 6px 0; padding: 6px; box-sizing: border-box; }
  button { padding: 8px 14px; cursor: pointer; }
  pre { background: #f5f5f5; padding: 10px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
</style>
</head>
<body>

<h1>SecureBank Passkey Test</h1>
<p>Run this over <code>http://localhost:8000</code> (must match WEBAUTHN_RP_ID / WEBAUTHN_ORIGIN in your .env).</p>

<section>
  <h2>1. Log in</h2>
  <input id="email" placeholder="email">
  <input id="password" type="password" placeholder="password">
  <button onclick="login()">Log in</button>
  <pre id="loginOut"></pre>
</section>

<section>
  <h2>2. Register a device</h2>
  <input id="deviceName" placeholder="device_name" value="Test Laptop">
  <input id="deviceIdField" placeholder="device_id" value="test-device-001">
  <input id="deviceType" placeholder="device_type" value="desktop">
  <input id="platform" placeholder="platform" value="web">
  <button onclick="registerDevice()">Register device</button>
  <pre id="deviceOut"></pre>
</section>

<section>
  <h2>3. Create passkey & trust device</h2>
  <input id="trustDeviceId" placeholder="numeric device id (from step 2)">
  <button onclick="trustWithPasskey()">Create passkey & trust</button>
  <pre id="trustOut"></pre>
</section>

<script>
let authToken = null;
let currentDeviceId = null;

function bufferToBase64url(buffer) {
  const bytes = new Uint8Array(buffer);
  let str = '';
  for (const b of bytes) str += String.fromCharCode(b);
  return btoa(str).replace(/\\+/g, '-').replace(/\\//g, '_').replace(/=+$/, '');
}

function base64urlToBuffer(base64url) {
  const padding = '='.repeat((4 - base64url.length % 4) % 4);
  const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/');
  const str = atob(base64);
  const bytes = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i);
  return bytes.buffer;
}

async function login() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const res = await fetch('/users/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
  });
  const data = await res.json();
  document.getElementById('loginOut').textContent = JSON.stringify(data, null, 2);
  if (data.access_token) authToken = data.access_token;
}

async function registerDevice() {
  const body = {
    device_name: document.getElementById('deviceName').value,
    device_id: document.getElementById('deviceIdField').value,
    device_type: document.getElementById('deviceType').value,
    device_fingerprint: 'fp-' + Math.random().toString(36).slice(2),
    platform: document.getElementById('platform').value,
  };
  const res = await fetch('/devices/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  document.getElementById('deviceOut').textContent = JSON.stringify(data, null, 2);
  if (data.id) {
    currentDeviceId = data.id;
    document.getElementById('trustDeviceId').value = data.id;
  }
}

async function trustWithPasskey() {
  const out = document.getElementById('trustOut');
  const deviceId = document.getElementById('trustDeviceId').value;

  try {
    // Step 1: get creation options from the server
    const optRes = await fetch(`/devices/${deviceId}/trust/passkey/options`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    const options = await optRes.json();
    if (!optRes.ok) { out.textContent = 'Options error: ' + JSON.stringify(options); return; }

    // Step 2: convert base64url fields to ArrayBuffers for the browser API
    options.challenge = base64urlToBuffer(options.challenge);
    options.user.id = base64urlToBuffer(options.user.id);
    if (options.excludeCredentials) {
      options.excludeCredentials = options.excludeCredentials.map(c => ({
        ...c,
        id: base64urlToBuffer(c.id),
      }));
    }

    // Step 3: prompt the platform authenticator (Face ID / Windows Hello / security key)
    const credential = await navigator.credentials.create({ publicKey: options });

    // Step 4: convert the credential back to base64url JSON for the server
    const credentialJSON = {
      id: credential.id,
      rawId: bufferToBase64url(credential.rawId),
      type: credential.type,
      response: {
        clientDataJSON: bufferToBase64url(credential.response.clientDataJSON),
        attestationObject: bufferToBase64url(credential.response.attestationObject),
      },
      clientExtensionResults: credential.getClientExtensionResults ? credential.getClientExtensionResults() : {},
    };

    // Step 5: send it to the server for verification
    const verifyRes = await fetch(`/devices/${deviceId}/trust/passkey/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(credentialJSON),
    });
    const result = await verifyRes.json();
    out.textContent = JSON.stringify(result, null, 2);
  } catch (err) {
    out.textContent = 'Error: ' + err;
  }
}
</script>

</body>
</html>
"""


@router.get("/webauthn-test", response_class=HTMLResponse)
def webauthn_test_page():
    return PAGE