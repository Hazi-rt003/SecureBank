const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

let authToken: string | null = null

export function setAuthToken(token: string | null) {
  authToken = token
  if (token) localStorage.setItem('securebank_token', token)
  else localStorage.removeItem('securebank_token')
}

export function loadStoredToken(): string | null {
  authToken = localStorage.getItem('securebank_token')
  return authToken
}

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  /** application/x-www-form-urlencoded body instead of JSON */
  form?: Record<string, string>
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { ...opts.headers }
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`

  let body: BodyInit | undefined
  if (opts.form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    body = new URLSearchParams(opts.form).toString()
  } else if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(opts.body)
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: opts.method || (opts.body || opts.form ? 'POST' : 'GET'),
    headers,
    body,
  })

  if (res.status === 204) return undefined as T

  let data: any = null
  try {
    data = await res.json()
  } catch {
    // non-JSON response (rare, e.g. a raw 500 from an unhandled error)
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || data.message)) || `Request failed with status ${res.status}`
    throw new ApiError(res.status, typeof message === 'string' ? message : JSON.stringify(message))
  }

  return data as T
}

export const api = {
  get: <T>(path: string, headers?: Record<string, string>) =>
    request<T>(path, { method: 'GET', headers }),
  post: <T>(path: string, body?: unknown, headers?: Record<string, string>) =>
    request<T>(path, { method: 'POST', body, headers }),
  postForm: <T>(path: string, form: Record<string, string>, headers?: Record<string, string>) =>
    request<T>(path, { method: 'POST', form, headers }),
}