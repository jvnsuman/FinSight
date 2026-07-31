import { useNavigate } from 'react-router-dom'
import { X, Wallet, TrendingUp, Target, ShieldCheck, Settings, ArrowRight } from 'lucide-react'
import Button from './Button'

const TYPE_META = {
  budget: { icon: Wallet, label: 'Budget', color: 'text-coral' },
  investment: { icon: TrendingUp, label: 'Investment', color: 'text-teal' },
  goal: { icon: Target, label: 'Goal', color: 'text-mint' },
  security: { icon: ShieldCheck, label: 'Security', color: 'text-navy' },
  system: { icon: Settings, label: 'System', color: 'text-slate-400' },
}

// Human-readable label for each action_url's destination, so the button
// says "Go to Budgets" instead of exposing the raw route.
const ACTION_LABELS = {
  '/budgets': 'Go to Budgets',
  '/goals': 'Go to Goals',
  '/investments': 'Go to Investments',
  '/portfolio': 'Go to Portfolio',
  '/profile': 'Go to Profile',
  '/dashboard': 'Go to Dashboard',
}

function formatFullDate(dateString) {
  return new Date(dateString).toLocaleString('en-IN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/**
 * Shows the full details of a single notification and, if it has an
 * action_url, a button to jump to the relevant page. Used from both the
 * bell dropdown and the full Notifications page so "click a notification"
 * behaves the same everywhere: see full details first, then act.
 */
export default function NotificationDetailModal({ notification, onClose }) {
  const navigate = useNavigate()
  if (!notification) return null

  const meta = TYPE_META[notification.type] || TYPE_META.system
  const Icon = meta.icon
  const actionLabel = notification.action_url
    ? ACTION_LABELS[notification.action_url] || 'View'
    : null

  const handleAction = () => {
    onClose()
    navigate(notification.action_url)
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-[200]">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <Icon size={20} className={meta.color} />
            <span className="text-xs font-semibold text-ink-light bg-surface px-2.5 py-1 rounded-full">
              {meta.label}
            </span>
          </div>
          <button onClick={onClose} className="text-ink-light hover:text-ink">
            <X size={20} />
          </button>
        </div>

        <h2 className="font-display text-lg font-semibold text-ink mb-2">{notification.title}</h2>
        <p className="text-sm text-ink-light leading-relaxed mb-4">{notification.message}</p>
        <p className="text-xs text-slate-400 mb-6">{formatFullDate(notification.created_at)}</p>

        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Close
          </Button>
          {actionLabel && (
            <Button variant="primary" onClick={handleAction} className="flex-1">
              {actionLabel}
              <ArrowRight size={16} />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
