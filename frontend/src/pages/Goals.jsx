import { useEffect, useState } from 'react'
import { Plus, Target, Trash2, Pencil, X, CheckCircle2, AlertTriangle, PiggyBank } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { getGoals, createGoal, updateGoal, deleteGoal, allocateSavings, fundGoal } from '../api/goalsApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

const STATUS_STYLES = {
  on_track: { label: 'On track', bar: 'bg-teal', badge: 'bg-teal/10 text-teal' },
  at_risk: { label: 'At risk', bar: 'bg-coral', badge: 'bg-coral/10 text-coral' },
  completed: { label: 'Completed', bar: 'bg-mint', badge: 'bg-mint/10 text-mint' },
}

function GoalFormModal({ existing, onClose, onSaved }) {
  const isEdit = Boolean(existing)
  const [form, setForm] = useState({
    goal_name: existing?.goal_name || '',
    goal_type: existing?.goal_type || '',
    target_amount: existing?.target_amount ?? '',
    current_amount: existing?.current_amount ?? 0,
    target_date: existing?.target_date || '',
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = {
        goal_name: form.goal_name,
        goal_type: form.goal_type || undefined,
        target_amount: parseFloat(form.target_amount),
        current_amount: parseFloat(form.current_amount) || 0,
        target_date: form.target_date,
      }
      if (isEdit) {
        // target_date/goal_name rarely change once set; still allowed via edit
        await updateGoal(existing.goal_id, payload)
      } else {
        await createGoal(payload)
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save this goal.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">
            {isEdit ? 'Edit goal' : 'New goal'}
          </h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Goal name"
            value={form.goal_name}
            onChange={(e) => setForm({ ...form, goal_name: e.target.value })}
            placeholder="Buy a Home"
            required
          />
          <Input
            label="Category (optional)"
            value={form.goal_type}
            onChange={(e) => setForm({ ...form, goal_type: e.target.value })}
            placeholder="home, retirement, travel, education..."
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Target amount"
              type="number"
              step="0.01"
              min="0.01"
              value={form.target_amount}
              onChange={(e) => setForm({ ...form, target_amount: e.target.value })}
              placeholder="5000000"
              required
            />
            <Input
              label="Saved so far"
              type="number"
              step="0.01"
              min="0"
              value={form.current_amount}
              onChange={(e) => setForm({ ...form, current_amount: e.target.value })}
              placeholder="0"
            />
          </div>
          <Input
            label="Target date"
            type="date"
            value={form.target_date}
            onChange={(e) => setForm({ ...form, target_date: e.target.value })}
            required
          />
          <ErrorBanner message={error} />
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving}>
              {saving ? 'Saving...' : isEdit ? 'Save changes' : 'Create goal'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function AllocateSavingsModal({ onClose, onSaved }) {
  const [source, setSource] = useState('wallet')
  const [percent, setPercent] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const res = await allocateSavings(source, parseFloat(percent))
      setResult(res.data)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not allocate savings right now.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Allocate savings to goals</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>

        {result ? (
          <div className="space-y-4">
            <p className="text-sm text-ink">
              Allocated <span className="font-semibold tabular-nums">{formatCurrency(result.total_allocated)}</span> across
              {' '}{result.allocations.length} active goal{result.allocations.length !== 1 ? 's' : ''}, weighted by how much each still needs.
            </p>
            <div className="space-y-2">
              {result.allocations.map((line) => (
                <div key={line.goal_id} className="flex items-center justify-between text-sm border-b border-slate-100 pb-2 last:border-0">
                  <span className="text-ink font-medium">{line.goal_name}</span>
                  <span className="text-ink-light tabular-nums">
                    +{formatCurrency(line.amount_allocated)} → {line.new_progress_pct.toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
            <Button onClick={onClose} fullWidth>Done</Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-xs text-ink-light">
              This is a one-time action: it distributes a percentage of your chosen savings
              source across every active goal now, proportional to how much each still needs
              (goals further from their target get a bigger share).
            </p>
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">Savings source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
              >
                <option value="wallet">Simulated trading wallet balance</option>
                <option value="income_savings">Savings pool (refilled monthly from income − expenses)</option>
              </select>
            </div>
            <Input
              label="Percent to allocate"
              type="number"
              step="0.1"
              min="0.1"
              max="100"
              value={percent}
              onChange={(e) => setPercent(e.target.value)}
              placeholder="25"
              required
            />
            <ErrorBanner message={error} />
            <div className="flex gap-3 pt-1">
              <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
              <Button type="submit" fullWidth disabled={saving}>{saving ? 'Allocating...' : 'Allocate'}</Button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

function FundGoalModal({ goal, onClose, onSaved }) {
  const [source, setSource] = useState('wallet')
  const [mode, setMode] = useState('amount') // 'amount' | 'percent'
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = { source }
      if (mode === 'amount') payload.amount = parseFloat(value)
      else payload.percent = parseFloat(value)

      const res = await fundGoal(goal.goal_id, payload)
      setResult(res.data)
      onSaved()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not fund this goal.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Fund "{goal.goal_name}"</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>

        {result ? (
          <div className="space-y-4">
            <p className="text-sm text-ink">
              Added <span className="font-semibold tabular-nums">{formatCurrency(result.amount_funded)}</span> to
              {' '}"{result.goal_name}" — now at {result.new_progress_pct.toFixed(0)}% funded.
            </p>
            <p className="text-xs text-ink-light">
              Remaining {result.source === 'wallet' ? 'wallet' : 'savings pool'} balance: {formatCurrency(result.remaining_source_balance)}
            </p>
            <Button onClick={onClose} fullWidth>Done</Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <p className="text-xs text-ink-light">
              This funds only this goal, directly — it doesn't touch any other goal.
            </p>
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">Source</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
              >
                <option value="wallet">Simulated trading wallet</option>
                <option value="income_savings">Savings pool</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => { setMode('amount'); setValue('') }}
                className={`py-2 rounded-lg text-sm font-medium border transition-colors ${
                  mode === 'amount' ? 'bg-teal text-white border-teal' : 'bg-white text-ink-light border-slate-200 hover:bg-slate-50'
                }`}
              >
                Fixed amount
              </button>
              <button
                type="button"
                onClick={() => { setMode('percent'); setValue('') }}
                className={`py-2 rounded-lg text-sm font-medium border transition-colors ${
                  mode === 'percent' ? 'bg-teal text-white border-teal' : 'bg-white text-ink-light border-slate-200 hover:bg-slate-50'
                }`}
              >
                Percent of source
              </button>
            </div>

            <Input
              label={mode === 'amount' ? 'Amount' : 'Percent'}
              type="number"
              step={mode === 'amount' ? '0.01' : '0.1'}
              min="0.01"
              max={mode === 'percent' ? '100' : undefined}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={mode === 'amount' ? '5000' : '25'}
              required
            />

            <ErrorBanner message={error} />
            <div className="flex gap-3 pt-1">
              <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
              <Button type="submit" fullWidth disabled={saving}>{saving ? 'Funding...' : 'Fund goal'}</Button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default function Goals() {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingGoal, setEditingGoal] = useState(null)
  const [showAllocateModal, setShowAllocateModal] = useState(false)
  const [fundingGoal, setFundingGoal] = useState(null)

  const load = async () => {
    setLoading(true)
    const res = await getGoals()
    setGoals(res.data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (goalId) => {
    if (!confirm('Delete this goal? This cannot be undone.')) return
    await deleteGoal(goalId)
    load()
  }

  const openEdit = (goal) => {
    setEditingGoal(goal)
    setShowModal(true)
  }

  const openAdd = () => {
    setEditingGoal(null)
    setShowModal(true)
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7 flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Financial Goals</h1>
          <p className="text-sm text-ink-light mt-0.5">Track progress toward what matters to you.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={() => setShowAllocateModal(true)}>
            <PiggyBank size={16} /> Allocate savings
          </Button>
          <Button onClick={openAdd}><Plus size={16} /> New goal</Button>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1, 2].map((i) => <div key={i} className="bg-white rounded-xl border border-slate-100 h-40 animate-pulse" />)}
        </div>
      ) : goals.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-ink-light text-sm mb-4">No goals yet. Set your first savings target.</p>
          <Button onClick={openAdd} className="mx-auto"><Plus size={16} /> New goal</Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {goals.map((goal) => {
            const style = STATUS_STYLES[goal.status] || STATUS_STYLES.on_track
            return (
              <Card key={goal.goal_id} className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-lg bg-teal/10 flex items-center justify-center shrink-0">
                      <Target size={16} className="text-teal" />
                    </div>
                    <div>
                      <p className="font-medium text-ink">{goal.goal_name}</p>
                      {goal.goal_type && <p className="text-xs text-ink-light capitalize">{goal.goal_type}</p>}
                    </div>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full flex items-center gap-1 ${style.badge}`}>
                    {goal.status === 'completed' && <CheckCircle2 size={12} />}
                    {goal.status === 'at_risk' && <AlertTriangle size={12} />}
                    {style.label}
                  </span>
                </div>

                <div className="mb-2">
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-sm font-medium text-ink tabular-nums">
                      {formatCurrency(goal.current_amount)}
                    </span>
                    <span className="text-xs text-ink-light tabular-nums">
                      of {formatCurrency(goal.target_amount)}
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${style.bar}`}
                      style={{ width: `${goal.progress_pct}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-ink-light mt-3">
                  <span>{goal.progress_pct.toFixed(0)}% funded</span>
                  <span>
                    {goal.status === 'completed'
                      ? 'Goal reached'
                      : `${goal.days_remaining} days left`}
                  </span>
                </div>

                {goal.required_monthly_saving != null && goal.status !== 'completed' && (
                  <p className="text-xs text-ink-light mt-2 pt-2 border-t border-slate-100">
                    Needs ~{formatCurrency(goal.required_monthly_saving)}/month to hit target
                  </p>
                )}

                <div className="flex items-center justify-between mt-3 -mb-1 -mr-1">
                  {goal.status !== 'completed' ? (
                    <button
                      onClick={() => setFundingGoal(goal)}
                      className="text-xs font-medium text-teal hover:underline flex items-center gap-1"
                    >
                      <PiggyBank size={13} /> Fund this goal
                    </button>
                  ) : <span />}
                  <div className="flex items-center gap-1">
                    <button onClick={() => openEdit(goal)} className="text-ink-light hover:text-teal p-1.5" aria-label="Edit goal">
                      <Pencil size={14} />
                    </button>
                    <button onClick={() => handleDelete(goal.goal_id)} className="text-ink-light hover:text-coral p-1.5" aria-label="Delete goal">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      {showModal && (
        <GoalFormModal
          existing={editingGoal}
          onClose={() => setShowModal(false)}
          onSaved={load}
        />
      )}

      {showAllocateModal && (
        <AllocateSavingsModal
          onClose={() => setShowAllocateModal(false)}
          onSaved={load}
        />
      )}

      {fundingGoal && (
        <FundGoalModal
          goal={fundingGoal}
          onClose={() => setFundingGoal(null)}
          onSaved={load}
        />
      )}
    </AppShell>
  )
}
