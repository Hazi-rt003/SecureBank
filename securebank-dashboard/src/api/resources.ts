import { api } from './client'
import type { Account, Device, Transaction, Session, AuditLogEntry } from '../types'
import { deviceHeaders } from './auth'
import { getBrowserDeviceMeta } from '../deviceIdentity'

// --- Accounts ---
export function getMyAccount() {
  return api.get<Account>('/accounts/me')
}

// --- Devices ---
export function listDevices() {
  return api.get<Device[]>('/devices/')
}

export function registerCurrentDevice() {
  const meta = getBrowserDeviceMeta()
  return api.post<Device>('/devices/register', meta)
}

export function trustDeviceManually(deviceId: number) {
  return api.post<Device>(`/devices/${deviceId}/trust`)
}

export function revokeDeviceTrust(deviceId: number) {
  return api.post<Device>(`/devices/${deviceId}/revoke`)
}

// --- Passkeys (device-trust registration ceremony) ---
export function getPasskeyRegistrationOptions(deviceId: number) {
  return api.get<Record<string, unknown>>(`/devices/${deviceId}/trust/passkey/options`)
}

export function verifyPasskeyRegistration(deviceId: number, credential: Record<string, unknown>) {
  return api.post<Device>(`/devices/${deviceId}/trust/passkey/verify`, credential)
}

// --- Transactions ---
export function initiateTransaction(recipient_account_number: string, amount: string) {
  return api.post<Transaction>(
    '/transactions/',
    { recipient_account_number, amount },
    { 'X-Device-Fingerprint': deviceHeaders()['X-Device-Fingerprint'] },
  )
}

export function listPendingTransactions() {
  return api.get<Transaction[]>('/transactions/pending')
}

export function approveTransaction(transactionId: number) {
  return api.post<Transaction>(
    `/transactions/${transactionId}/approve`,
    undefined,
    { 'X-Device-Fingerprint': deviceHeaders()['X-Device-Fingerprint'] },
  )
}

export function rejectTransaction(transactionId: number) {
  return api.post<Transaction>(
    `/transactions/${transactionId}/reject`,
    undefined,
    { 'X-Device-Fingerprint': deviceHeaders()['X-Device-Fingerprint'] },
  )
}

// --- Sessions ---
export function listSessions() {
  return api.get<Session[]>('/users/sessions')
}

export function revokeSession(sessionId: number) {
  return api.post<Session>(`/users/sessions/${sessionId}/revoke`)
}

export function revokeOtherSessions() {
  return api.post<{ revoked_count: number }>('/users/sessions/revoke-others')
}

// --- Audit log ---
export function listAuditLogs() {
  return api.get<AuditLogEntry[]>('/audit-logs/')
}