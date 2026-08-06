import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '../common/Card'

const SLICE_COLORS = ['#028090', '#02C39A', '#E0574B', '#F4A259', '#7C9885', '#5B7B9A']

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

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="bg-navy text-white text-xs rounded-lg px-3 py-2 shadow-soft">
      <p className="text-slate-300 font-medium mb-1">{ASSET_TYPE_LABELS[data.asset_type] || data.asset_type}</p>
      <p style={{ color: payload[0].color }}>
        {formatCurrency(data.value)} ({data.percentage.toFixed(1)}%)
      </p>
    </div>
  )
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

      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={allocation}
            dataKey="value"
            nameKey="asset_type"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
          >
            {allocation.map((slice, i) => (
              <Cell key={slice.asset_type} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="space-y-3 mt-2">
        {allocation.map((slice, i) => (
          <div key={slice.asset_type} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: SLICE_COLORS[i % SLICE_COLORS.length] }}
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
