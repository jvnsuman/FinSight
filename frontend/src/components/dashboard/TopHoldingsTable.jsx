import { Card } from '../common/Card'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatPercent(pct) {
  if (pct === null || pct === undefined) return '—'
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

export default function TopHoldingsTable({ investments }) {
  const topHoldings = [...investments]
    .filter((inv) => inv.current_value != null)
    .sort((a, b) => b.current_value - a.current_value)
    .slice(0, 5)

  if (topHoldings.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Top holdings</h2>
        <p className="text-sm text-ink-light">No priced holdings yet.</p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Top holdings</h2>
      <div className="space-y-3">
        {topHoldings.map((inv) => (
          <div key={inv.investment_id} className="flex items-center justify-between text-sm">
            <div className="min-w-0">
              <p className="text-ink font-medium truncate">{inv.asset_name}</p>
              {inv.symbol && <p className="text-xs text-ink-light">{inv.symbol}</p>}
            </div>
            <div className="flex items-center gap-3 tabular-nums shrink-0">
              <span className={inv.return_pct >= 0 ? 'text-mint' : 'text-coral'}>
                {formatPercent(inv.return_pct)}
              </span>
              <span className="text-ink font-semibold w-24 text-right">
                {formatCurrency(inv.current_value)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
