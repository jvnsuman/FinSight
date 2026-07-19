import { Card } from '../common/Card'

const STRIP_COLORS = ['#028090', '#02C39A', '#E0574B', '#F4A259', '#7C9885', '#5B7B9A']

const ASSET_TYPE_LABELS = {
  stock: 'Stocks',
  mutual_fund: 'Mutual Funds',
  etf: 'ETFs',
  bond: 'Bonds',
  gold: 'Gold',
  cash: 'Cash',
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function AllocationStrip({ allocation }) {
  if (!allocation || allocation.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Asset allocation</h2>
        <p className="text-sm text-ink-light">Add a holding to see how your portfolio is split.</p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Asset allocation</h2>

      <div className="flex h-3 rounded-full overflow-hidden mb-5">
        {allocation.map((slice, i) => (
          <div
            key={slice.asset_type}
            style={{
              width: `${slice.percentage}%`,
              backgroundColor: STRIP_COLORS[i % STRIP_COLORS.length],
            }}
            title={`${ASSET_TYPE_LABELS[slice.asset_type] || slice.asset_type}: ${slice.percentage.toFixed(1)}%`}
          />
        ))}
      </div>

      <div className="space-y-3">
        {allocation.map((slice, i) => (
          <div key={slice.asset_type} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: STRIP_COLORS[i % STRIP_COLORS.length] }}
              />
              <span className="text-ink font-medium">{ASSET_TYPE_LABELS[slice.asset_type] || slice.asset_type}</span>
            </div>
            <div className="flex items-center gap-3 tabular-nums">
              <span className="text-ink-light">{slice.percentage.toFixed(1)}%</span>
              <span className="text-ink font-semibold w-24 text-right">{formatCurrency(slice.value)}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
