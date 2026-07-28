import { useState, useEffect } from 'react'
import { Monitor, ShieldCheck, LogOut } from 'lucide-react'
import { Card, ErrorBanner } from '../common/Card'
import Button from '../common/Button'
import { getSessions, revokeSession } from '../../api/authApi'

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

export default function SessionsCard() {
  const [sessions, setSessions] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [revokingId, setRevokingId] = useState(null)

  const loadSessions = async () => {
    setIsLoading(true)
    setError('')
    try {
      const { data } = await getSessions()
      setSessions(data.sessions)
    } catch {
      setError('Could not load your active sessions.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadSessions()
  }, [])

  const handleRevoke = async (sessionId) => {
    setRevokingId(sessionId)
    setError('')
    try {
      await revokeSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId))
    } catch {
      setError('Could not log out that device. Please try again.')
    } finally {
      setRevokingId(null)
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-1">
        <ShieldCheck size={18} className="text-teal" />
        <h2 className="font-display text-base font-semibold text-ink">Active sessions</h2>
      </div>
      <p className="text-sm text-ink-light mb-4">
        Devices currently logged into your account. Don't recognize one? Log it out below.
      </p>

      <ErrorBanner message={error} />

      {isLoading && <p className="text-sm text-ink-light py-4">Loading sessions...</p>}

      {!isLoading && sessions.length === 0 && (
        <p className="text-sm text-ink-light py-4">No active sessions found.</p>
      )}

      {!isLoading && sessions.length > 0 && (
        <div className="space-y-2 mt-2">
          {sessions.map((s) => (
            <div
              key={s.session_id}
              className="flex items-center justify-between px-4 py-3 rounded-lg border border-slate-100 bg-surface"
            >
              <div className="flex items-start gap-3 min-w-0">
                <Monitor size={18} className="text-ink-light mt-0.5 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink truncate">
                    {s.device_info || 'Unknown device'}
                    {s.is_current && (
                      <span className="ml-2 text-xs font-semibold text-mint bg-mint-light px-2 py-0.5 rounded-full">
                        This device
                      </span>
                    )}
                  </p>
                  <p className="text-xs text-ink-light mt-0.5">
                    {s.ip_address ? `${s.ip_address} · ` : ''}Last active {timeAgo(s.last_active_at)}
                  </p>
                </div>
              </div>

              {!s.is_current && (
                <Button
                  variant="danger"
                  onClick={() => handleRevoke(s.session_id)}
                  disabled={revokingId === s.session_id}
                  className="shrink-0"
                >
                  <LogOut size={14} />
                  {revokingId === s.session_id ? 'Logging out...' : 'Log out'}
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
