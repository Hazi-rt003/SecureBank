// A lightweight, persistent per-browser device identity. This is NOT a
// sophisticated fingerprinting technique (canvas/audio fingerprinting etc.)
// -- it's a random ID generated once and stored, which is enough for the
// backend's trust/revocation model. Real fingerprinting (deriving an ID
// from hardware/browser characteristics without storage) is a separate,
// deliberately deferred piece of work.

const STORAGE_KEY = 'securebank_device'

interface StoredDevice {
  fingerprint: string
  deviceId: string
}

function randomId(): string {
  return crypto.randomUUID().replace(/-/g, '')
}

export function getDeviceIdentity(): StoredDevice {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (raw) {
    try {
      return JSON.parse(raw) as StoredDevice
    } catch {
      // fall through and regenerate if corrupted
    }
  }
  const fresh: StoredDevice = {
    fingerprint: `fp-${randomId()}`,
    deviceId: `web-${randomId()}`,
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh))
  return fresh
}

export function getBrowserDeviceMeta() {
  const { fingerprint, deviceId } = getDeviceIdentity()
  const ua = navigator.userAgent
  let platform = 'web'
  if (/Mac/i.test(ua)) platform = 'macos'
  else if (/Win/i.test(ua)) platform = 'windows'
  else if (/Linux/i.test(ua)) platform = 'linux'
  else if (/Android/i.test(ua)) platform = 'android'
  else if (/iPhone|iPad/i.test(ua)) platform = 'ios'

  return {
    device_fingerprint: fingerprint,
    device_id: deviceId,
    device_name: `${navigator.platform || 'Browser'} — ${navigator.userAgent.includes('Chrome') ? 'Chrome' : navigator.userAgent.includes('Firefox') ? 'Firefox' : 'Browser'}`,
    device_type: 'desktop',
    platform,
  }
}