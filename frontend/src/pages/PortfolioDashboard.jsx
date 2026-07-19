import { useEffect, useState } from 'react'
import AppShell from '../components/layout/AppShell'
import PortfolioSummaryCards from '../components/dashboard/PortfolioSummaryCards'
import AllocationStrip from '../components/dashboard/AllocationStrip'
import TopHoldingsTable from '../components/dashboard/TopHoldingsTable'
import GoalsOverviewStrip from '../components/dashboard/GoalsOverviewStrip'
import { getInvestments, getPortfolioSummary } from '../api/investmentsApi'
import { getGoals } from '../api/goalsApi'

export default function PortfolioDashboard() {
  const [investments, setInvestments] = useState([])
  const [summary, setSummary] = useState(null)
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      const [investmentsRes, summaryRes, goalsRes] = await Promise.all([
        getInvestments(false, true),
        getPortfolioSummary(),
        getGoals(),
      ])
      setInvestments(investmentsRes.data)
      setSummary(summaryRes.data)
      setGoals(goalsRes.data)
      setLoading(false)
    }
    load()
  }, [])

  return (
    <AppShell>
      <div className="mb-7">
        <h1 className="font-display text-2xl font-semibold text-ink">Portfolio Overview</h1>
        <p className="text-sm text-ink-light mt-0.5">
          Your investments and goals, in one place.
        </p>
      </div>

      {loading || !summary ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white rounded-xl shadow-card border border-slate-100 p-5 h-[104px] animate-pulse" />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-100 h-72 animate-pulse" />
            <div className="bg-white rounded-xl border border-slate-100 h-72 animate-pulse" />
          </div>
        </div>
      ) : investments.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-100 p-10 text-center">
          <p className="text-ink-light text-sm">
            No holdings yet. Add an investment from the Investments page to see your portfolio here.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <PortfolioSummaryCards summary={summary} holdingsCount={investments.length} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AllocationStrip allocation={summary.allocation} />
            <TopHoldingsTable investments={investments} />
          </div>

          <GoalsOverviewStrip goals={goals} />
        </div>
      )}
    </AppShell>
  )
}
