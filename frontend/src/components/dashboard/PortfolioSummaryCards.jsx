import { TrendingUp, TrendingDown, Wallet, PieChart } from 'lucide-react'
import { Card } from '../common/Card'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function SummaryCard({ label, value, icon: Icon, accent, sub }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-ink-light uppercase tracking-wide">{label}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent.bg}`}>
          <Icon size={16} className={accent.text} strokeWidth={2.25} />
        </div>
      </div>
      <p className="font-display text-2xl font-semibold text-ink tabular-nums">{value}</p>
      {sub && <p className="text-xs text-ink-light mt-1">{sub}</p>}
    </Card>
  )
}

export default function PortfolioSummaryCards({ summary, holdingsCount }) {
  const isPositive = summary.total_return_amount >= 0

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <SummaryCard
        label="Total Invested"
        value={formatCurrency(summary.total_invested)}
        icon={Wallet}
        accent={{ bg: 'bg-teal/10', text: 'text-teal' }}
      />
      <SummaryCard
        label="Current Value"
        value={formatCurrency(summary.total_current_value)}
        icon={PieChart}
        accent={{ bg: 'bg-navy/10', text: 'text-navy' }}
      />
      <SummaryCard
        label="Overall Return"
        value={formatCurrency(summary.total_return_amount)}
        icon={isPositive ? TrendingUp : TrendingDown}
        accent={
          isPositive
            ? { bg: 'bg-mint-light', text: 'text-mint' }
            : { bg: 'bg-coral-light', text: 'text-coral' }
        }
        sub={`${isPositive ? '+' : ''}${summary.total_return_pct.toFixed(2)}%`}
      />
      <SummaryCard
        label="Holdings"
        value={holdingsCount ?? '—'}
        icon={PieChart}
        accent={{ bg: 'bg-teal/10', text: 'text-teal' }}
      />
    </div>
  )
}
