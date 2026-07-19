import { Card } from '../common/Card'

const STRIP_COLORS = ['#028090', '#02C39A', '#E0574B', '#F4A259', '#7C9885', '#5B7B9A', '#B8A9C9', '#D4A574']

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function ExpenseBreakdownStrip({ breakdown }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Where it went</h2>
        <p className="text-sm text-ink-light">No expenses recorded for this month yet.</p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Where it went</h2>

      {/* The signature strip - proportional segments, one per category */}
      <div className="flex h-3 rounded-full overflow-hidden mb-5">
        {breakdown.map((item, i) => (
          <div
            key={item.category_id ?? 'uncategorized'}
            style={{
              width: `${item.percent_of_total}%`,
              backgroundColor: STRIP_COLORS[i % STRIP_COLORS.length],
            }}
            title={`${item.category_name}: ${item.percent_of_total}%`}
          />
        ))}
      </div>

      <div className="space-y-3">
        {breakdown.map((item, i) => (
          <div key={item.category_id ?? 'uncategorized'} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: STRIP_COLORS[i % STRIP_COLORS.length] }}
              />
              <span className="text-ink font-medium">{item.category_name}</span>
            </div>
            <div className="flex items-center gap-3 tabular-nums">
              <span className="text-ink-light">{item.percent_of_total}%</span>
              <span className="text-ink font-semibold w-24 text-right">{formatCurrency(item.amount)}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
