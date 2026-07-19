import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { Card } from '../common/Card'

function formatCurrencyShort(value) {
  if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L`
  if (value >= 1000) return `₹${(value / 1000).toFixed(0)}K`
  return `₹${value}`
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-navy text-white text-xs rounded-lg px-3 py-2 shadow-soft">
      <p className="text-slate-300 mb-1">{new Date(label).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.name}: ₹{p.value.toLocaleString('en-IN')}
        </p>
      ))}
    </div>
  )
}

export default function MonthlyTrendChart({ trend }) {
  if (!trend || trend.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Monthly trend</h2>
        <p className="text-sm text-ink-light">No transactions recorded for this month yet.</p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Monthly trend</h2>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={trend} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={(d) => new Date(d).getDate()}
            tick={{ fontSize: 12, fill: '#64748B' }}
            axisLine={{ stroke: '#E2E8F0' }}
            tickLine={false}
          />
          <YAxis
            tickFormatter={formatCurrencyShort}
            tick={{ fontSize: 12, fill: '#64748B' }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line type="monotone" dataKey="income" name="Income" stroke="#02C39A" strokeWidth={2.5} dot={false} />
          <Line type="monotone" dataKey="expenses" name="Expenses" stroke="#E0574B" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-5 mt-2 text-xs text-ink-light">
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-mint" />Income</span>
        <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-coral" />Expenses</span>
      </div>
    </Card>
  )
}
