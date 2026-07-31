import { useState, useEffect, useCallback } from 'react'
import { Bell, CheckCheck, Wallet, TrendingUp, Target, Settings } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '../api/notificationsApi'
import NotificationDetailModal from '../components/common/NotificationDetailModal'

const FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'budget', label: 'Budget', icon: Wallet },
  { value: 'investment', label: 'Investment', icon: TrendingUp },
  { value: 'goal', label: 'Goal', icon: Target },
  { value: 'system', label: 'System', icon: Settings },
]

const TYPE_STYLE = {
  budget: { dot: 'bg-coral', label: 'Budget' },
  investment: { dot: 'bg-teal', label: 'Investment' },
  goal: { dot: 'bg-mint', label: 'Goal' },
  security: { dot: 'bg-navy', label: 'Security' },
  system: { dot: 'bg-slate-400', label: 'System' },
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  })
}

// How many to request from the backend at once. There's no server-side
// pagination cursor yet (list_notifications just takes a limit), so "Load
// more" re-requests with a larger limit rather than an offset - simple and
// good enough for this milestone's volume of alerts.
const PAGE_SIZE = 30

export default function Notifications() {
  const [notifications, setNotifications] = useState([])
  const [filter, setFilter] = useState('all')
  const [limit, setLimit] = useState(PAGE_SIZE)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [hasMore, setHasMore] = useState(true)
  const [selectedNotification, setSelectedNotification] = useState(null)

  const load = useCallback(async (currentLimit) => {
    setIsLoading(true)
    setError('')
    try {
      const { data } = await getNotifications(false, currentLimit)
      setNotifications(data.notifications)
      setHasMore(data.notifications.length >= currentLimit)
    } catch {
      setError('Could not load your notifications.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    load(limit)
  }, [limit, load])

  const handleOpenNotification = (notification) => {
    setSelectedNotification(notification)
    if (!notification.is_read) {
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === notification.notification_id ? { ...n, is_read: true } : n))
      )
      markNotificationRead(notification.notification_id).catch(() => load(limit))
    }
  }

  const handleMarkAllRead = async () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    try {
      await markAllNotificationsRead()
    } catch {
      load(limit)
    }
  }

  const filtered = filter === 'all' ? notifications : notifications.filter((n) => n.type === filter)
  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2.5">
          <Bell size={22} className="text-teal" />
          <h1 className="font-display text-2xl font-semibold text-ink">Notifications</h1>
        </div>
        {unreadCount > 0 && (
          <Button variant="secondary" onClick={handleMarkAllRead}>
            <CheckCheck size={16} />
            Mark all read ({unreadCount})
          </Button>
        )}
      </div>

      <div className="flex gap-2 mb-5 flex-wrap">
        {FILTERS.map(({ value, label, icon: Icon }) => (
          <button
            key={value}
            onClick={() => setFilter(value)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === value
                ? 'bg-teal text-white'
                : 'bg-white text-ink-light border border-slate-200 hover:bg-surface'
            }`}
          >
            {Icon && <Icon size={14} />}
            {label}
          </button>
        ))}
      </div>

      <ErrorBanner message={error} />

      <Card className="p-0 overflow-hidden">
        {isLoading && notifications.length === 0 && (
          <p className="text-sm text-ink-light text-center py-12">Loading notifications...</p>
        )}

        {!isLoading && filtered.length === 0 && (
          <p className="text-sm text-ink-light text-center py-12">
            {filter === 'all' ? "You're all caught up." : `No ${filter} notifications yet.`}
          </p>
        )}

        {filtered.map((n) => {
          const style = TYPE_STYLE[n.type] || { dot: 'bg-teal', label: n.type }
          return (
            <button
              key={n.notification_id}
              onClick={() => handleOpenNotification(n)}
              className={`w-full text-left px-5 py-4 border-b border-slate-100 last:border-0 hover:bg-surface transition-colors flex items-start gap-3 ${
                n.is_read ? 'opacity-60' : ''
              }`}
            >
              <span className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${n.is_read ? 'bg-slate-300' : style.dot}`} />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-semibold text-ink">{n.title}</p>
                  <span className="text-[11px] font-medium text-ink-light bg-surface px-2 py-0.5 rounded-full">
                    {style.label}
                  </span>
                  {!n.is_read && <span className="w-1.5 h-1.5 rounded-full bg-coral" />}
                </div>
                <p className="text-sm text-ink-light mt-1">{n.message}</p>
                <p className="text-xs text-slate-400 mt-1.5">{formatDate(n.created_at)}</p>
              </div>
            </button>
          )
        })}
      </Card>

      {!isLoading && hasMore && filter === 'all' && (
        <div className="flex justify-center mt-5">
          <Button variant="secondary" onClick={() => setLimit((prev) => prev + PAGE_SIZE)}>
            Load more
          </Button>
        </div>
      )}

      <NotificationDetailModal
        notification={selectedNotification}
        onClose={() => setSelectedNotification(null)}
      />
    </AppShell>
  )
}
