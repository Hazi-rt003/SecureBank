import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User } from '../types'
import * as authApi from '../api/auth'
import { setAuthToken, loadStoredToken, ApiError } from '../api/client'
import {
  prepareRequestOptions,
  authenticationCredentialToJSON,
} from '../webauthn'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = loadStoredToken()
    if (!token) {
      setLoading(false)
      return
    }
    authApi
      .getMe()
      .then(setUser)
      .catch(() => setAuthToken(null))
      .finally(() => setLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const result = await authApi.login(email, password)

    if ('step_up_required' in result) {
      // This device has a registered passkey — password alone isn't enough.
      // Complete the WebAuthn authentication ceremony transparently.
      const requestOptions = prepareRequestOptions(result.options)
      const assertion = (await navigator.credentials.get({
        publicKey: requestOptions,
      })) as PublicKeyCredential | null

      if (!assertion) {
        throw new Error('Passkey authentication was cancelled')
      }

      const credentialJSON = authenticationCredentialToJSON(assertion)
      const token = await authApi.verifyLoginPasskey(credentialJSON)
      setAuthToken(token.access_token)
    } else {
      setAuthToken(result.access_token)
    }

    const me = await authApi.getMe()
    setUser(me)
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch {
      // even if the server call fails, clear local state so the user isn't
      // stuck appearing logged in
    }
    setAuthToken(null)
    setUser(null)
  }

  async function refreshUser() {
    const me = await authApi.getMe()
    setUser(me)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export { ApiError }