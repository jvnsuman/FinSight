import { useState, useEffect, useRef, useCallback } from 'react'
import { Bell } from 'lucide-react'
import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
} from '../../api/notificationsApi'

const POLL_INTERVAL_MS = 30000

function timeAgo(dateString) {
  const seconds = Math.floor((Date.now() - new Date(dateString)) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

// Loosely maps notification `type` to a dot color. Any unrecognized type
// (a teammate's new category) safely falls back to teal rather than erroring.
const TYPE_DOT_COLOR = {
  budget: 'bg-coral',
  investment: 'bg-teal',
  goal: 'bg-mint',
  security: 'bg-navy',
  system: 'bg-slate-400',
}

export default function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const dropdownRef = useRef(null)

  const refreshUnreadCount = useCallback(async () => {
    try {
      const { data } = await getUnreadCount()
      setUnreadCount(data.unread_count)
    } catch {
      // Silently ignore - a failed poll shouldn't disrupt the rest of the UI.
    }
  }, [])

  const loadNotifications = useCallback(async () => {
    setIsLoading(true)
    try {
      const { data } = await getNotifications()
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch {
      // Leave whatever was already loaded in place.
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUnreadCount()
    const interval = setInterval(refreshUnreadCount, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [refreshUnreadCount])

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggle = () => {
    const next = !isOpen
    setIsOpen(next)
    if (next) loadNotifications()
  }

  const handleMarkRead = async (notificationId) => {
    setNotifications((prev) =>
      prev.map((n) => (n.notification_id === notificationId ? { ...n, is_read: true } : n))
    )
    setUnreadCount((prev) => Math.max(prev - 1, 0))
    try {
      await markNotificationRead(notificationId)
    } catch {
      loadNotifications() // resync on failure
    }
  }

  const handleMarkAllRead = async () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
    setUnreadCount(0)
    try {
      await markAllNotificationsRead()
    } catch {
      loadNotifications()
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={handleToggle}
        className="relative flex items-center justify-center w-9 h-9 rounded-lg text-slate-300 hover:bg-white/5 hover:text-white transition-colors"
        aria-label="Notifications"
      >
        <Bell size={18} strokeWidth={2} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[16px] h-4 px-1 rounded-full bg-coral text-white text-[10px] font-semibold leading-none">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute left-0 top-full mt-2 w-80 bg-white rounded-xl shadow-soft border border-slate-100 overflow-hidden z-[100]">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
            <h3 className="font-display text-sm font-semibold text-ink">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="text-xs font-medium text-teal hover:text-teal-light transition-colors"
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {isLoading && (
              <div className="px-4 py-8 text-center text-sm text-ink-light">Loading...</div>
            )}

            {!isLoading && notifications.length === 0 && (
              <div className="px-4 py-8 text-center text-sm text-ink-light">
                You're all caught up.
              </div>
            )}

            {!isLoading &&
              notifications.map((n) => (
                <button
                  key={n.notification_id}
                  onClick={() => !n.is_read && handleMarkRead(n.notification_id)}
                  className={`w-full text-left px-4 py-3 border-b border-slate-50 last:border-0 hover:bg-surface transition-colors ${
                    n.is_read ? 'opacity-60' : ''
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    <span
                      className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${
                        n.is_read ? 'bg-slate-300' : TYPE_DOT_COLOR[n.type] || 'bg-teal'
                      }`}
                    />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-ink truncate">{n.title}</p>
                      <p className="text-xs text-ink-light mt-0.5 line-clamp-2">{n.message}</p>
                      <p className="text-[11px] text-slate-400 mt-1">{timeAgo(n.created_at)}</p>
                    </div>
                  </div>
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
