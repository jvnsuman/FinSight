import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'
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
      <p className="text-slate-300 font-medium mb-1">{label}</p>
      <p style={{ color: payload[0].color || '#02C39A' }}>
        Total Spent: ₹{payload[0].value.toLocaleString('en-IN')}
      </p>
    </div>
  )
}

export default function DayOfWeekChart({ breakdown }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Weekly patterns</h2>
        <p className="text-sm text-ink-light">No expenses recorded for this month yet.</p>
      </Card>
    )
  }

  // Find max value to color the highest bar differently if desired, or just use a nice solid color.
  const maxAmount = Math.max(...breakdown.map(b => b.amount))

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Weekly patterns</h2>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={breakdown} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis 
            dataKey="day_name" 
            tickFormatter={(d) => d.substring(0, 3)} 
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
          <Tooltip content={<CustomTooltip />} cursor={{ fill: '#F1F5F9' }} />
          <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
            {breakdown.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.amount === maxAmount && entry.amount > 0 ? '#E0574B' : '#028090'} 
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
