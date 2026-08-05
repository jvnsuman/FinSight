import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Card } from '../common/Card'

const COLORS = ['#028090', '#02C39A', '#E0574B', '#F4A259', '#7C9885', '#5B7B9A', '#B8A9C9']

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
      <p className="text-slate-300 font-medium mb-1">{data.payment_mode}</p>
      <p style={{ color: payload[0].color }}>
        {formatCurrency(data.amount)} ({data.percent_of_total}%)
      </p>
    </div>
  )
}

export default function PaymentModePieChart({ breakdown }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="font-display text-lg font-semibold text-ink mb-1">Payment modes</h2>
        <p className="text-sm text-ink-light">No expenses recorded for this month yet.</p>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-lg font-semibold text-ink mb-4">Payment modes</h2>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={breakdown}
            dataKey="amount"
            nameKey="payment_mode"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
          >
            {breakdown.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            iconType="circle"
            wrapperStyle={{ fontSize: '12px', color: '#64748B' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
