import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/transactions', label: 'Transactions' },
  { to: '/devices', label: 'Devices' },
  { to: '/sessions', label: 'Sessions' },
  { to: '/audit', label: 'Audit log' },
]

export function Layout() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-paper text-ink flex">
      <aside className="w-60 shrink-0 bg-ink text-paper flex flex-col justify-between">
        <div>
          <div className="px-6 py-6">
            <span className="font-display text-lg font-semibold tracking-tight">
              SecureBank
            </span>
          </div>
          <nav className="px-3 flex flex-col gap-0.5">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `rounded-md px-3 py-2 text-sm transition-colors ${
                    isActive
                      ? 'bg-ink-soft text-paper font-medium'
                      : 'text-paper/60 hover:text-paper hover:bg-ink-soft/60'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="px-6 py-5 border-t border-ink-line">
          {user && (
            <div className="mb-3">
              <div className="text-sm font-medium text-paper">{user.full_name}</div>
              <div className="text-xs text-paper/50">{user.email}</div>
            </div>
          )}
          <button
            onClick={() => logout()}
            className="text-sm text-paper/60 hover:text-paper transition-colors"
          >
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  )
}