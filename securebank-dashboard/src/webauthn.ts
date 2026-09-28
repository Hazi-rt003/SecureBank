export function bufferToBase64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer)
  let str = ''
  for (const b of bytes) str += String.fromCharCode(b)
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

export function base64urlToBuffer(base64url: string): ArrayBuffer {
  const padding = '='.repeat((4 - (base64url.length % 4)) % 4)
  const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/')
  const str = atob(base64)
  const bytes = new Uint8Array(str.length)
  for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i)
  return bytes.buffer
}

// Converts server-issued registration options (base64url strings) into the
// ArrayBuffer form navigator.credentials.create() requires.
export function prepareCreationOptions(
  options: Record<string, any>,
): PublicKeyCredentialCreationOptions {
  const prepared = { ...options }
  prepared.challenge = base64urlToBuffer(options.challenge)
  prepared.user = { ...options.user, id: base64urlToBuffer(options.user.id) }
  if (options.excludeCredentials) {
    prepared.excludeCredentials = options.excludeCredentials.map((c: any) => ({
      ...c,
      id: base64urlToBuffer(c.id),
    }))
  }
  return prepared as PublicKeyCredentialCreationOptions
}

// Converts server-issued authentication options into the form
// navigator.credentials.get() requires.
export function prepareRequestOptions(
  options: Record<string, any>,
): PublicKeyCredentialRequestOptions {
  const prepared = { ...options }
  prepared.challenge = base64urlToBuffer(options.challenge)
  if (options.allowCredentials) {
    prepared.allowCredentials = options.allowCredentials.map((c: any) => ({
      ...c,
      id: base64urlToBuffer(c.id),
    }))
  }
  return prepared as PublicKeyCredentialRequestOptions
}

// Converts a fresh registration credential into the JSON shape the
// backend's verify_registration_response expects.
export function registrationCredentialToJSON(credential: PublicKeyCredential) {
  const response = credential.response as AuthenticatorAttestationResponse
  return {
    id: credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64url(response.clientDataJSON),
      attestationObject: bufferToBase64url(response.attestationObject),
    },
    clientExtensionResults: credential.getClientExtensionResults?.() ?? {},
  }
}

// Converts a fresh authentication assertion into the JSON shape the
// backend's verify_authentication_response expects.
export function authenticationCredentialToJSON(credential: PublicKeyCredential) {
  const response = credential.response as AuthenticatorAssertionResponse
  return {
    id: credential.id,
    rawId: bufferToBase64url(credential.rawId),
    type: credential.type,
    response: {
      clientDataJSON: bufferToBase64url(response.clientDataJSON),
      authenticatorData: bufferToBase64url(response.authenticatorData),
      signature: bufferToBase64url(response.signature),
      userHandle: response.userHandle ? bufferToBase64url(response.userHandle) : null,
    },
    clientExtensionResults: credential.getClientExtensionResults?.() ?? {},
  }
}