import { Link } from 'react-router-dom'
import { Target } from 'lucide-react'
import { Card } from '../common/Card'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

const STATUS_BAR = {
  on_track: 'bg-teal',
  at_risk: 'bg-coral',
  completed: 'bg-mint',
}

export default function GoalsOverviewStrip({ goals }) {
  const topGoals = [...goals]
    .filter((g) => g.status !== 'completed')
    .slice(0, 4)

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-lg font-semibold text-ink">Financial goals</h2>
        <Link to="/goals" className="text-xs font-medium text-teal hover:underline">
          View all goals
        </Link>
      </div>

      {topGoals.length === 0 ? (
        <p className="text-sm text-ink-light">No active goals right now.</p>
      ) : (
        <div className="space-y-4">
          {topGoals.map((goal) => (
            <div key={goal.goal_id}>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-sm font-medium text-ink flex items-center gap-2">
                  <Target size={13} className="text-ink-light" />
                  {goal.goal_name}
                </span>
                <span className="text-xs text-ink-light tabular-nums">
                  {formatCurrency(goal.current_amount)} / {formatCurrency(goal.target_amount)}
                </span>
              </div>
              <div className="w-full h-1.5 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${STATUS_BAR[goal.status] || STATUS_BAR.on_track}`}
                  style={{ width: `${goal.progress_pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
