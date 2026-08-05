import { useEffect, useState } from 'react'
import { Landmark, X, Target, Wallet, TrendingUp, CalendarClock } from 'lucide-react'
import { Card, ErrorBanner } from '../common/Card'
import { getSavingsBreakdown } from '../../api/savingsApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function monthLabel(dateStr) {
  if (!dateStr) return null
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
}

function BreakdownRow({ icon: Icon, label, value, accent }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-100 last:border-0">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent.bg}`}>
          <Icon size={14} className={accent.text} />
        </div>
        <span className="text-sm text-ink">{label}</span>
      </div>
      <span className="text-sm font-medium text-ink tabular-nums">{formatCurrency(value)}</span>
    </div>
  )
}

function SavingsBreakdownModal({ onClose }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    getSavingsBreakdown()
      .then((res) => { if (!cancelled) setData(res.data) })
      .catch(() => { if (!cancelled) setError('Could not load your savings breakdown.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-lg p-6 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Savings Pool breakdown</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-12 rounded-lg bg-slate-100 animate-pulse" />)}
          </div>
        ) : error ? (
          <ErrorBanner message={error} />
        ) : (
          <>
            <div className="bg-surface rounded-lg p-4 mb-5 text-center">
              <p className="text-xs font-medium text-ink-light uppercase tracking-wide mb-1">Total in pool</p>
              <p className="font-display text-3xl font-semibold text-ink tabular-nums">
                {formatCurrency(data.savings_pool)}
              </p>
              {data.last_refill_triggered_month && (
                <p className="text-xs text-ink-light mt-1">Last topped up {monthLabel(data.last_refill_triggered_month)}</p>
              )}
            </div>

            <h3 className="text-sm font-semibold text-ink mb-1">How it's building up</h3>
            <div className="mb-5">
              {data.last_refill_month && (
                <BreakdownRow
                  icon={CalendarClock}
                  label={`Added from ${monthLabel(data.last_refill_month)}`}
                  value={data.last_refill_amount}
                  accent={{ bg: 'bg-navy/10', text: 'text-navy' }}
                />
              )}
              <BreakdownRow
                icon={TrendingUp}
                label="This month's contribution"
                value={data.this_month_contribution}
                accent={{ bg: 'bg-mint-light', text: 'text-mint' }}
              />
              <BreakdownRow
                icon={Wallet}
                label="Wallet cash pending next sweep"
                value={data.wallet_cash_pending_sweep}
                accent={{ bg: 'bg-teal/10', text: 'text-teal' }}
              />
            </div>

            <h3 className="text-sm font-semibold text-ink mb-1">
              Already allocated to goals ({formatCurrency(data.total_allocated_to_goals)})
            </h3>
            {data.goal_allocations.length === 0 ? (
              <p className="text-sm text-ink-light py-3">Nothing allocated to goals yet.</p>
            ) : (
              <div>
                {data.goal_allocations.map((g) => (
                  <BreakdownRow
                    key={g.goal_id}
                    icon={Target}
                    label={g.goal_name}
                    value={g.current_amount}
                    accent={{ bg: 'bg-navy/10', text: 'text-navy' }}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function SavingsPoolCard({ savingsPool }) {
  const [showBreakdown, setShowBreakdown] = useState(false)

  return (
    <>
      <Card
        className="p-5 cursor-pointer hover:shadow-soft transition-shadow"
        onClick={() => setShowBreakdown(true)}
      >
        <div className="flex items-start justify-between mb-3">
          <span className="text-xs font-medium text-ink-light uppercase tracking-wide">Savings Pool</span>
          <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-mint-light">
            <Landmark size={16} className="text-mint" strokeWidth={2.25} />
          </div>
        </div>
        <p className="font-display text-2xl font-semibold text-ink tabular-nums">{formatCurrency(savingsPool)}</p>
        <p className="text-xs text-ink-light mt-1">Your overall savings · tap for details</p>
      </Card>

      {showBreakdown && <SavingsBreakdownModal onClose={() => setShowBreakdown(false)} />}
    </>
  )
}
