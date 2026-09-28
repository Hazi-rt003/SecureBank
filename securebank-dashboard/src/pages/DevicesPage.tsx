import { useEffect, useState } from 'react'
import * as api from '../api/resources'
import type { Device } from '../types'
import { PageHeader } from '../components/PageHeader'
import { TrustBadge } from '../components/Badges'
import { ApiError } from '../api/client'
import { prepareCreationOptions, registrationCredentialToJSON } from '../webauthn'
import { getDeviceIdentity } from '../deviceIdentity'

export function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<number | 'register' | null>(null)
  const [error, setError] = useState<string | null>(null)

  const currentFingerprint = getDeviceIdentity().fingerprint

  function refresh() {
    setLoading(true)
    api
      .listDevices()
      .then(setDevices)
      .finally(() => setLoading(false))
  }

  useEffect(refresh, [])

  async function handleRegisterThisDevice() {
    setError(null)
    setBusyId('register')
    try {
      await api.registerCurrentDevice()
      refresh()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not register this device.')
    } finally {
      setBusyId(null)
    }
  }

  async function handleTrustWithPasskey(device: Device) {
    setError(null)
    setBusyId(device.id)
    try {
      const options = await api.getPasskeyRegistrationOptions(device.id)
      const creationOptions = prepareCreationOptions(options)
      const credential = (await navigator.credentials.create({
        publicKey: creationOptions,
      })) as PublicKeyCredential | null

      if (!credential) throw new Error('Passkey creation was cancelled')

      const credentialJSON = registrationCredentialToJSON(credential)
      await api.verifyPasskeyRegistration(device.id, credentialJSON)
      refresh()
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : 'Passkey setup failed.',
      )
    } finally {
      setBusyId(null)
    }
  }

  async function handleRevoke(device: Device) {
    setError(null)
    setBusyId(device.id)
    try {
      await api.revokeDeviceTrust(device.id)
      refresh()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not revoke this device.')
    } finally {
      setBusyId(null)
    }
  }

  const thisDeviceRegistered = devices.some((d) => d.device_fingerprint === currentFingerprint)

  return (
    <div>
      <PageHeader
        title="Devices"
        subtitle="Devices you've used to sign in, and their trust status"
        action={
          !thisDeviceRegistered && (
            <button
              onClick={handleRegisterThisDevice}
              disabled={busyId === 'register'}
              className="rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-60"
            >
              {busyId === 'register' ? 'Registering…' : 'Register this browser'}
            </button>
          )
        }
      />

      <div className="px-10 py-8">
        {error && (
          <div className="mb-4 rounded-md bg-risk-high-soft px-3 py-2 text-sm text-risk-high">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-sm text-ink/50">Loading…</p>
        ) : devices.length === 0 ? (
          <p className="text-sm text-ink/50 border border-dashed border-paper-line rounded-md px-4 py-6 text-center">
            No devices yet. Register this browser to get started.
          </p>
        ) : (
          <div className="border border-paper-line rounded-md divide-y divide-paper-line">
            {devices.map((device) => (
              <div key={device.id} className="px-4 py-4 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium flex items-center gap-2">
                    {device.device_name}
                    {device.device_fingerprint === currentFingerprint && (
                      <span className="text-xs text-signal font-normal">This browser</span>
                    )}
                  </div>
                  <div className="text-xs text-ink/50 mt-0.5 font-mono">
                    {device.platform} · {device.device_type}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <TrustBadge trusted={device.trusted} />
                  {!device.trusted ? (
                    <button
                      onClick={() => handleTrustWithPasskey(device)}
                      disabled={busyId === device.id}
                      className="rounded-md bg-signal px-3 py-1.5 text-sm font-medium text-white hover:bg-signal/90 transition-colors disabled:opacity-50"
                    >
                      {busyId === device.id ? 'Waiting…' : 'Set up passkey'}
                    </button>
                  ) : (
                    <button
                      onClick={() => handleRevoke(device)}
                      disabled={busyId === device.id}
                      className="rounded-md border border-paper-line px-3 py-1.5 text-sm font-medium text-ink/70 hover:bg-paper-line/40 transition-colors disabled:opacity-50"
                    >
                      Revoke trust
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}