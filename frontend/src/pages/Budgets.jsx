import { useEffect, useState, useCallback } from 'react'
import { Plus, X, Trash2, AlertTriangle, ChevronLeft, ChevronRight, Receipt } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { getBudgets, getBudget, createBudget, deleteBudget } from '../api/budgetsApi'
import { getCategories } from '../api/categoriesApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

function currentMonthValue() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
}

function monthLabel(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
}

function shiftMonth(dateStr, delta) {
  const d = new Date(dateStr + 'T00:00:00')
  d.setMonth(d.getMonth() + delta)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
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

function BudgetDetailModal({ budgetId, onClose }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')
    getBudget(budgetId)
      .then((res) => { if (!cancelled) setDetail(res.data) })
      .catch(() => { if (!cancelled) setError('Could not load budget details.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [budgetId])

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-lg p-6 max-h-[85vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">
            {detail?.category_name || 'Overall budget'}
          </h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-12 rounded-lg bg-slate-100 animate-pulse" />)}
          </div>
        ) : error ? (
          <ErrorBanner message={error} />
        ) : (
          <>
            <div className="bg-surface rounded-lg p-4 mb-5">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-ink-light">
                  {formatCurrency(detail.spent_amount)} of {formatCurrency(detail.amount)}
                </span>
                <span className={`text-sm font-semibold ${detail.is_exceeded ? 'text-coral' : 'text-ink'}`}>
                  {detail.utilization_percent}%
                </span>
              </div>
              <BudgetBar budget={detail} />
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-ink-light">
                  {monthLabel(detail.month)}
                </span>
                <span className="text-xs text-ink-light">
                  {formatCurrency(Math.max(detail.remaining_amount, 0))} remaining
                </span>
              </div>
            </div>

            <h3 className="text-sm font-semibold text-ink mb-3">
              Transactions ({detail.transactions.length})
            </h3>
            {detail.transactions.length === 0 ? (
              <p className="text-sm text-ink-light text-center py-6">
                No expenses recorded against this budget yet.
              </p>
            ) : (
              <div className="space-y-2">
                {detail.transactions.map((t) => (
                  <div key={t.transaction_id} className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-coral-light flex items-center justify-center shrink-0">
                        <Receipt size={14} className="text-coral" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm text-ink truncate">{t.description || t.category?.category_name || 'Expense'}</p>
                        <p className="text-xs text-ink-light">{formatDate(t.transaction_date)}</p>
                      </div>
                    </div>
                    <span className="text-sm font-medium text-ink tabular-nums shrink-0 ml-3">
                      {formatCurrency(t.amount)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function Budgets() {
  const [month, setMonth] = useState(currentMonthValue())
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedBudgetId, setSelectedBudgetId] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    const [budgetsRes, catRes] = await Promise.all([getBudgets(month), getCategories()])
    setBudgets(budgetsRes.data)
    setCategories(catRes.data)
    setLoading(false)
  }, [month])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this budget?')) return
    await deleteBudget(id)
    load()
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Budgets</h1>
          <p className="text-sm text-ink-light mt-0.5">See how much you've set aside, month by month.</p>
        </div>
        <Button onClick={() => setShowModal(true)}><Plus size={16} /> Set a budget</Button>
      </div>

      <div className="flex items-center gap-1 bg-white rounded-lg border border-slate-200 px-1.5 py-1.5 shadow-card w-fit mb-6">
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

      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[1, 2].map((i) => <div key={i} className="bg-white rounded-xl border border-slate-100 h-32 animate-pulse" />)}
        </div>
      ) : budgets.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-ink-light text-sm mb-4">No budgets set for {monthLabel(month)} yet.</p>
          <Button onClick={() => setShowModal(true)} className="mx-auto"><Plus size={16} /> Set a budget</Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {budgets.map((b) => (
            <Card
              key={b.budget_id}
              className="p-5 cursor-pointer hover:shadow-soft transition-shadow"
              onClick={() => setSelectedBudgetId(b.budget_id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-semibold text-ink">{b.category_name || 'Overall budget'}</p>
                  <p className="text-xs text-ink-light">
                    {formatCurrency(b.spent_amount)} of {formatCurrency(b.amount)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {b.is_exceeded && <AlertTriangle size={16} className="text-coral" />}
                  <button onClick={(e) => handleDelete(b.budget_id, e)} className="text-ink-light hover:text-coral p-1">
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

      {selectedBudgetId && (
        <BudgetDetailModal
          budgetId={selectedBudgetId}
          onClose={() => setSelectedBudgetId(null)}
        />
      )}
    </AppShell>
  )
}
