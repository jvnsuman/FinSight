import { useEffect, useState, useCallback } from 'react'
import { Plus, X, Trash2, AlertTriangle } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { getBudgets, createBudget, deleteBudget } from '../api/budgetsApi'
import { getCategories } from '../api/categoriesApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function currentMonthValue() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
}

function BudgetFormModal({ categories, defaultMonth, onClose, onCreated }) {
  const [form, setForm] = useState({ category_id: '', amount: '', month: defaultMonth })
  const [error, setError] = useState('')
  const [confirmPrompt, setConfirmPrompt] = useState(null) // { message } when a Tier 3 override is being asked for
  const [saving, setSaving] = useState(false)

  const expenseCategories = categories.filter((c) => c.category_type === 'expense')

  const submitBudget = async (confirmOverride) => {
    setError('')
    setSaving(true)
    try {
      await createBudget({
        category_id: form.category_id ? Number(form.category_id) : null,
        amount: parseFloat(form.amount),
        month: form.month,
        confirm_override: confirmOverride,
      })
      onCreated()
      onClose()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (err.response?.status === 409 && detail?.message) {
        // Tier 3: exceeds income + savings. Ask the user to confirm before resubmitting.
        setConfirmPrompt({ message: detail.message })
      } else {
        // detail can be a plain string (most errors) or an object (409 case above,
        // already handled) - never pass a raw object into ErrorBanner, React can't
        // render it and will throw ("Objects are not valid as a React child").
        setError(typeof detail === 'string' ? detail : 'Could not create budget.')
      }
    } finally {
      setSaving(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setConfirmPrompt(null)
    await submitBudget(false)
  }

  const handleConfirmOverride = async () => {
    await submitBudget(true)
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Set a budget</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Scope</label>
            <select
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
              className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
            >
              <option value="">Overall (all spending)</option>
              {expenseCategories.map((c) => (
                <option key={c.category_id} value={c.category_id}>{c.category_name}</option>
              ))}
            </select>
          </div>
          <Input
            label="Budget amount"
            type="number"
            step="0.01"
            min="0.01"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
            placeholder="8000"
            required
          />
          <Input
            label="Month"
            type="month"
            value={form.month.slice(0, 7)}
            onChange={(e) => setForm({ ...form, month: `${e.target.value}-01` })}
            required
          />
          <ErrorBanner message={error} />
          {confirmPrompt && (
            <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm rounded-lg px-4 py-3 space-y-2">
              <p>{confirmPrompt.message}</p>
              <Button
                type="button"
                variant="secondary"
                onClick={handleConfirmOverride}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Yes, create it anyway'}
              </Button>
            </div>
          )}
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving}>{saving ? 'Saving...' : 'Set budget'}</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function BudgetBar({ budget }) {
  const pct = Math.min(budget.utilization_percent, 100)
  const barColor = budget.is_exceeded ? 'bg-coral' : pct > 80 ? 'bg-amber-400' : 'bg-mint'

  return (
    <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
      <div className={`h-full rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
    </div>
  )
}

export default function Budgets() {
  const [month] = useState(currentMonthValue())
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    const [budgetsRes, catRes] = await Promise.all([getBudgets(month), getCategories()])
    setBudgets(budgetsRes.data)
    setCategories(catRes.data)
    setLoading(false)
  }, [month])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id) => {
    if (!confirm('Delete this budget?')) return
    await deleteBudget(id)
    load()
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Budgets</h1>
          <p className="text-sm text-ink-light mt-0.5">
            {new Date(month + 'T00:00:00').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
          </p>
        </div>
        <Button onClick={() => setShowModal(true)}><Plus size={16} /> Set a budget</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2].map((i) => <div key={i} className="bg-white rounded-xl border border-slate-100 h-32 animate-pulse" />)}
        </div>
      ) : budgets.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-ink-light text-sm mb-4">No budgets set for this month yet.</p>
          <Button onClick={() => setShowModal(true)} className="mx-auto"><Plus size={16} /> Set a budget</Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {budgets.map((b) => (
            <Card key={b.budget_id} className="p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold text-ink">{b.category_name || 'Overall budget'}</p>
                  <p className="text-xs text-ink-light">
                    {formatCurrency(b.spent_amount)} of {formatCurrency(b.amount)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {b.is_exceeded && <AlertTriangle size={16} className="text-coral" />}
                  <button onClick={() => handleDelete(b.budget_id)} className="text-ink-light hover:text-coral p-1">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <BudgetBar budget={b} />
              <div className="flex items-center justify-between mt-2">
                <span className={`text-xs font-medium ${b.is_exceeded ? 'text-coral' : 'text-ink-light'}`}>
                  {b.utilization_percent}% used
                </span>
                <span className="text-xs text-ink-light">
                  {formatCurrency(Math.max(b.remaining_amount, 0))} left
                </span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {showModal && (
        <BudgetFormModal
          categories={categories}
          defaultMonth={month}
          onClose={() => setShowModal(false)}
          onCreated={load}
        />
      )}
    </AppShell>
  )
}
