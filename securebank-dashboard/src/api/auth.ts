import { api } from './client'
import type { LoginResult, Token, User } from '../types'
import { getBrowserDeviceMeta } from '../deviceIdentity'

// HTTP header values must be Latin-1 (chars <= 255) or fetch() throws.
// Strip anything outside printable ASCII so a stray character in a
// browser-reported string (platform, user agent, etc.) can never break a request.
function toHeaderSafe(value: string): string {
  return value.replace(/[^\x20-\x7E]/g, '-')
}

function deviceHeaders(): Record<string, string> {
  const meta = getBrowserDeviceMeta()
  return {
    'X-Device-Fingerprint': toHeaderSafe(meta.device_fingerprint),
    'X-Device-Id': toHeaderSafe(meta.device_id),
    'X-Device-Name': toHeaderSafe(meta.device_name),
    'X-Device-Type': toHeaderSafe(meta.device_type),
    'X-Platform': toHeaderSafe(meta.platform),
  }
}

export function register(input: {
  full_name: string
  email: string
  phone_number: string
  password: string
}) {
  return api.post<User>('/users/register', input)
}

export function login(email: string, password: string) {
  return api.postForm<LoginResult>(
    '/users/login',
    { username: email, password },
    deviceHeaders(),
  )
}

export function verifyLoginPasskey(credential: Record<string, unknown>) {
  return api.post<Token>('/users/login/passkey/verify', { credential })
}

export function getMe() {
  return api.get<User>('/users/me')
}

export function logout() {
  return api.post<{ detail: string }>('/users/logout')
}

export { deviceHeaders }