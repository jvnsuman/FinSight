import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { Card } from '../common/Card'

const SLICE_COLORS = ['#028090', '#02C39A', '#E0574B', '#F4A259', '#7C9885', '#5B7B9A', '#B8A9C9', '#D4A574']

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
      <p className="text-slate-300 font-medium mb-1">{data.category_name}</p>
      <p style={{ color: payload[0].color }}>
        {formatCurrency(data.amount)} ({data.percent_of_total}%)
      </p>
    </div>
  )
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

      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={breakdown}
            dataKey="amount"
            nameKey="category_name"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={80}
            paddingAngle={3}
          >
            {breakdown.map((item, i) => (
              <Cell key={item.category_id ?? 'uncategorized'} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      <div className="space-y-3 mt-2">
        {breakdown.map((item, i) => (
          <div key={item.category_id ?? 'uncategorized'} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2.5">
              <span
                className="w-2.5 h-2.5 rounded-full shrink-0"
                style={{ backgroundColor: SLICE_COLORS[i % SLICE_COLORS.length] }}
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
