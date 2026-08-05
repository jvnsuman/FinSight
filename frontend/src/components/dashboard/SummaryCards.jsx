import { TrendingUp, TrendingDown, PiggyBank, Gauge } from 'lucide-react'
import { Card } from '../common/Card'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function SummaryCard({ label, value, icon: Icon, accent }) {
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-ink-light uppercase tracking-wide">{label}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${accent.bg}`}>
          <Icon size={16} className={accent.text} strokeWidth={2.25} />
        </div>
      </div>
      <p className="font-display text-2xl font-semibold text-ink tabular-nums">{value}</p>
    </Card>
  )
}

export default function SummaryCards({ summary }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <SummaryCard
        label="Total Income"
        value={formatCurrency(summary.total_income)}
        icon={TrendingUp}
        accent={{ bg: 'bg-mint-light', text: 'text-mint' }}
      />
      <SummaryCard
        label="Total Expenses"
        value={formatCurrency(summary.total_expenses)}
        icon={TrendingDown}
        accent={{ bg: 'bg-coral-light', text: 'text-coral' }}
      />
      <SummaryCard
        label="Monthly Savings"
        value={formatCurrency(summary.total_savings)}
        icon={PiggyBank}
        accent={{ bg: 'bg-teal/10', text: 'text-teal' }}
      />
      <SummaryCard
        label="Budget Utilization"
        value={`${summary.budget_utilization_percent}%`}
        icon={Gauge}
        accent={{ bg: 'bg-navy/10', text: 'text-navy' }}
      />
    </div>
  )
}
