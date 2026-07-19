import { useEffect, useState, useCallback } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { getDashboardSummary } from '../api/dashboardApi'
import AppShell from '../components/layout/AppShell'
import SummaryCards from '../components/dashboard/SummaryCards'
import ExpenseBreakdownStrip from '../components/dashboard/ExpenseBreakdownStrip'
import MonthlyTrendChart from '../components/dashboard/MonthlyTrendChart'
import RecentTransactions from '../components/dashboard/RecentTransactions'
import { useAuth } from '../context/AuthContext'

function monthLabel(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
}

function shiftMonth(dateStr, delta) {
  const d = new Date(dateStr + 'T00:00:00')
  d.setMonth(d.getMonth() + delta)
  return d.toISOString().slice(0, 10)
}

export default function Dashboard() {
  const { user } = useAuth()
  const [month, setMonth] = useState(() => {
    const now = new Date()
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
  })
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async (targetMonth) => {
    setLoading(true)
    try {
      const res = await getDashboardSummary(targetMonth)
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData(month)
  }, [month, fetchData])

  const firstName = user?.name?.split(' ')[0]

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">
            {firstName ? `Hi, ${firstName}` : 'Dashboard'}
          </h1>
          <p className="text-sm text-ink-light mt-0.5">Here's how your money moved this month.</p>
        </div>

        <div className="flex items-center gap-1 bg-white rounded-lg border border-slate-200 px-1.5 py-1.5 shadow-card">
          <button
            onClick={() => setMonth((m) => shiftMonth(m, -1))}
            className="p-1.5 rounded-md hover:bg-slate-50 text-ink-light"
            aria-label="Previous month"
          >
            <ChevronLeft size={18} />
          </button>
          <span className="text-sm font-medium text-ink px-2 min-w-[140px] text-center">
            {monthLabel(month)}
          </span>
          <button
            onClick={() => setMonth((m) => shiftMonth(m, 1))}
            className="p-1.5 rounded-md hover:bg-slate-50 text-ink-light"
            aria-label="Next month"
          >
            <ChevronRight size={18} />
          </button>
        </div>
      </div>

      {loading || !data ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-card border border-slate-100 p-5 h-[104px] animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="space-y-6">
          <SummaryCards summary={data.summary} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ExpenseBreakdownStrip breakdown={data.expense_breakdown} />
            <MonthlyTrendChart trend={data.monthly_trend} />
          </div>

          <RecentTransactions transactions={data.recent_transactions} />
        </div>
      )}
    </AppShell>
  )
}
