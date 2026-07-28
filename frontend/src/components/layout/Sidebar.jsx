import { NavLink } from 'react-router-dom'
import { LayoutGrid, Receipt, Wallet, PiggyBank, TrendingUp, Target, LineChart, User, LogOut } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import NotificationBell from './NotificationBell'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutGrid },
  { to: '/transactions', label: 'Transactions', icon: Receipt },
  { to: '/accounts', label: 'Accounts', icon: Wallet },
  { to: '/budgets', label: 'Budgets', icon: PiggyBank },
  { to: '/investments', label: 'Investments', icon: TrendingUp },
  { to: '/goals', label: 'Goals', icon: Target },
  { to: '/portfolio', label: 'Portfolio', icon: LineChart },
]

export default function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside className="relative z-20 w-64 shrink-0 bg-navy min-h-screen flex flex-col">
      <div className="px-6 py-7 flex items-center justify-between">
        <span className="font-display text-2xl font-semibold text-white">
          Fin<span className="text-mint">Sight</span>
        </span>
        <NotificationBell />
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-teal text-white'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            <Icon size={18} strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 pb-6 pt-4 border-t border-white/10 mx-3">
        <div className="px-3.5 py-2 mb-1">
          <p className="text-sm font-medium text-white truncate">{user?.name}</p>
          <p className="text-xs text-slate-400 truncate">{user?.email}</p>
        </div>
        <NavLink
          to="/profile"
          className={({ isActive }) =>
            `w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              isActive
                ? 'bg-teal text-white'
                : 'text-slate-300 hover:bg-white/5 hover:text-white'
            }`
          }
        >
          <User size={18} strokeWidth={2} />
          Profile
        </NavLink>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-white/5 hover:text-white transition-colors"
        >
          <LogOut size={18} strokeWidth={2} />
          Log out
        </button>
      </div>
    </aside>
  )
}
