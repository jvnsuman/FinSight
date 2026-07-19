import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { Card } from '../common/Card'
import { Link } from 'react-router-dom'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function RecentTransactions({ transactions }) {
  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-lg font-semibold text-ink">Recent transactions</h2>
        <Link to="/transactions" className="text-sm text-teal hover:underline font-medium">View all</Link>
      </div>

      {transactions.length === 0 ? (
        <p className="text-sm text-ink-light">No transactions yet. Add your first one to get started.</p>
      ) : (
        <div className="divide-y divide-slate-100">
          {transactions.map((t) => {
            const isIncome = t.transaction_type === 'income'
            return (
              <div key={t.transaction_id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${isIncome ? 'bg-mint-light' : 'bg-coral-light'}`}>
                    {isIncome ? (
                      <ArrowUpRight size={16} className="text-mint" strokeWidth={2.5} />
                    ) : (
                      <ArrowDownRight size={16} className="text-coral" strokeWidth={2.5} />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-ink">{t.description || t.category_name || 'Transaction'}</p>
                    <p className="text-xs text-ink-light">
                      {t.category_name || 'Uncategorized'} · {new Date(t.transaction_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </p>
                  </div>
                </div>
                <span className={`text-sm font-semibold tabular-nums ${isIncome ? 'text-mint' : 'text-coral'}`}>
                  {isIncome ? '+' : '-'}{formatCurrency(t.amount)}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
