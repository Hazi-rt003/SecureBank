export interface User {
  id: number
  full_name: string
  email: string
  phone_number: string
  is_verified: boolean
}

export interface Token {
  access_token: string
  token_type: string
  device_trusted: boolean | null
  new_device: boolean | null
}

export interface LoginStepUp {
  step_up_required: true
  device_id: number
  options: Record<string, unknown>
}

export type LoginResult = Token | LoginStepUp

export interface Account {
  id: number
  account_number: string
  balance: string
  currency: string
}

export interface Device {
  id: number
  device_name: string
  device_id: string
  device_type: string | null
  device_fingerprint: string
  platform: string
  trusted: boolean
}

export interface Transaction {
  id: number
  sender_account_id: number
  recipient_account_id: number
  amount: string
  currency: string
  status: 'pending_approval' | 'completed' | 'rejected' | 'failed'
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  created_at: string | null
  decided_at: string | null
  completed_at: string | null
}

export interface Session {
  id: number
  device_id: number | null
  created_at: string | null
  expires_at: string
  revoked_at: string | null
  is_current: boolean
}

export interface AuditLogEntry {
  id: number
  action: string
  details: string | null
  ip_address: string | null
  device_fingerprint: string | null
  created_at: string | null
}