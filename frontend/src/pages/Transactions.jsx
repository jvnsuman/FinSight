import { useEffect, useState, useCallback } from 'react'
import { Plus, ArrowUpRight, ArrowDownRight, ArrowLeftRight, Trash2, X, AlertTriangle } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { getTransactions, createTransaction, deleteTransaction } from '../api/transactionsApi'
import { getAccounts } from '../api/accountsApi'
import { getCategories } from '../api/categoriesApi'
import { getGoals, coverShortfall } from '../api/goalsApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

const TYPE_ICON = { income: ArrowUpRight, expense: ArrowDownRight, transfer: ArrowLeftRight }
const TYPE_COLOR = {
  income: { bg: 'bg-mint-light', text: 'text-mint' },
  expense: { bg: 'bg-coral-light', text: 'text-coral' },
  transfer: { bg: 'bg-teal/10', text: 'text-teal' },
}

function ShortfallWarningModal({ warning, onClose, onResolved }) {
  const [goals, setGoals] = useState([])
  const [loadingGoals, setLoadingGoals] = useState(true)
  const [selections, setSelections] = useState({}) // goal_id -> amount string
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [done, setDone] = useState(false)

  useEffect(() => {
    getGoals().then((res) => {
      setGoals(res.data.filter((g) => g.status !== 'completed' && g.current_amount > 0))
      setLoadingGoals(false)
    })
  }, [])

  const totalSelected = Object.values(selections).reduce((sum, v) => sum + (parseFloat(v) || 0), 0)

  const handleCover = async () => {
    setError('')
    const withdrawals = Object.entries(selections)
      .filter(([, amount]) => parseFloat(amount) > 0)
      .map(([goal_id, amount]) => ({ goal_id: Number(goal_id), amount: parseFloat(amount) }))

    if (withdrawals.length === 0) {
      setError('Enter an amount for at least one goal, or skip for now.')
      return
    }

    setSaving(true)
    try {
      await coverShortfall(withdrawals)
      onResolved()
      setDone(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not withdraw from the selected goal(s).')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 rounded-lg bg-coral-light flex items-center justify-center shrink-0">
            <AlertTriangle size={16} className="text-coral" />
          </div>
          <h2 className="font-display text-lg font-semibold text-ink">Savings ran short</h2>
        </div>

        {done ? (
          <div className="space-y-4">
            <p className="text-sm text-ink">The shortfall has been covered from your selected goal(s).</p>
            <Button onClick={onClose} fullWidth>Done</Button>
          </div>
        ) : (
          <>
            <p className="text-sm text-ink mb-1">{warning.message}</p>
            <p className="text-xs text-ink-light mb-4">
              Uncovered amount: <span className="font-semibold text-coral tabular-nums">{formatCurrency(warning.remaining_shortfall)}</span>
            </p>

            {loadingGoals ? (
              <p className="text-sm text-ink-light">Loading your goals...</p>
            ) : goals.length === 0 ? (
              <p className="text-sm text-ink-light mb-4">You have no funded goals to draw from right now. You can close this and cover it manually later.</p>
            ) : (
              <div className="space-y-3 mb-4">
                {goals.map((goal) => (
                  <div key={goal.goal_id} className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-ink font-medium truncate">{goal.goal_name}</p>
                      <p className="text-xs text-ink-light">Available: {formatCurrency(goal.current_amount)}</p>
                    </div>
                    <input
                      type="number"
                      min="0"
                      max={goal.current_amount}
                      step="0.01"
                      placeholder="0"
                      value={selections[goal.goal_id] || ''}
                      onChange={(e) => setSelections({ ...selections, [goal.goal_id]: e.target.value })}
                      className="w-28 rounded-lg border border-slate-200 px-3 py-2 text-sm text-right tabular-nums focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
                    />
                  </div>
                ))}
                <p className="text-xs text-ink-light text-right pt-1 border-t border-slate-100">
                  Selected total: <span className="font-medium tabular-nums">{formatCurrency(totalSelected)}</span>
                </p>
              </div>
            )}

            <ErrorBanner message={error} />
            <div className="flex gap-3 pt-1">
              <Button variant="secondary" onClick={onClose} fullWidth type="button">Skip for now</Button>
              {goals.length > 0 && (
                <Button onClick={handleCover} fullWidth disabled={saving}>
                  {saving ? 'Covering...' : 'Cover shortfall'}
                </Button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function TransactionFormModal({ accounts, categories, onClose, onCreated }) {
  const [form, setForm] = useState({
    account_id: accounts[0]?.account_id || '',
    category_id: '',
    transaction_type: 'expense',
    amount: '',
    description: '',
    payment_mode: 'UPI',
    transaction_date: new Date().toISOString().slice(0, 10),
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [shortfallWarning, setShortfallWarning] = useState(null)

  const relevantCategories = categories.filter((c) =>
    form.transaction_type === 'income' ? c.category_type === 'income' : c.category_type === 'expense'
  )

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const res = await createTransaction({
        account_id: Number(form.account_id),
        category_id: form.category_id ? Number(form.category_id) : null,
        transaction_type: form.transaction_type,
        amount: parseFloat(form.amount),
        description: form.description || undefined,
        payment_mode: form.payment_mode || undefined,
        transaction_date: form.transaction_date,
      })
      onCreated()
      if (res.data.savings_warning) {
        // Don't close yet - let the user choose which goal(s) to cover the
        // remaining shortfall from before dismissing.
        setShortfallWarning(res.data.savings_warning)
      } else {
        onClose()
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add transaction.')
    } finally {
      setSaving(false)
    }
  }

  if (shortfallWarning) {
    return (
      <ShortfallWarningModal
        warning={shortfallWarning}
        onClose={onClose}
        onResolved={onCreated}
      />
    )
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Add transaction</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-3 gap-2">
            {['income', 'expense', 'transfer'].map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setForm({ ...form, transaction_type: type, category_id: '' })}
                className={`py-2 rounded-lg text-sm font-medium capitalize border transition-colors ${
                  form.transaction_type === type
                    ? 'bg-teal text-white border-teal'
                    : 'bg-white text-ink-light border-slate-200 hover:bg-slate-50'
                }`}
              >
                {type}
              </button>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Account</label>
            <select
              value={form.account_id}
              onChange={(e) => setForm({ ...form, account_id: e.target.value })}
              className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
              required
            >
              {accounts.map((a) => (
                <option key={a.account_id} value={a.account_id}>{a.account_name}</option>
              ))}
            </select>
          </div>

          {form.transaction_type !== 'transfer' && (
            <div>
              <label className="block text-sm font-medium text-ink mb-1.5">Category</label>
              <select
                value={form.category_id}
                onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
              >
                <option value="">Uncategorized</option>
                {relevantCategories.map((c) => (
                  <option key={c.category_id} value={c.category_id}>{c.category_name}</option>
                ))}
              </select>
            </div>
          )}

          <Input
            label="Amount"
            type="number"
            step="0.01"
            min="0.01"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
            placeholder="0.00"
            required
          />
          <Input
            label="Description (optional)"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Grocery shopping"
          />
          <Input
            label="Date"
            type="date"
            value={form.transaction_date}
            onChange={(e) => setForm({ ...form, transaction_date: e.target.value })}
            required
          />

          <ErrorBanner message={error} />
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving || !form.account_id}>
              {saving ? 'Adding...' : 'Add transaction'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [accounts, setAccounts] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [typeFilter, setTypeFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    const [txnsRes, accRes, catRes] = await Promise.all([
      getTransactions(typeFilter ? { transaction_type: typeFilter, limit: 100 } : { limit: 100 }),
      getAccounts(),
      getCategories(),
    ])
    setTransactions(txnsRes.data)
    setAccounts(accRes.data)
    setCategories(catRes.data)
    setLoading(false)
  }, [typeFilter])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id) => {
    if (!confirm('Delete this transaction? This will adjust the account balance.')) return
    await deleteTransaction(id)
    load()
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Transactions</h1>
          <p className="text-sm text-ink-light mt-0.5">Every rupee, tracked.</p>
        </div>
        <Button onClick={() => setShowModal(true)} disabled={accounts.length === 0}>
          <Plus size={16} /> Add transaction
        </Button>
      </div>

      <div className="flex gap-2 mb-5">
        {['', 'income', 'expense', 'transfer'].map((type) => (
          <button
            key={type || 'all'}
            onClick={() => setTypeFilter(type)}
            className={`px-3.5 py-1.5 rounded-full text-sm font-medium capitalize border transition-colors ${
              typeFilter === type
                ? 'bg-navy text-white border-navy'
                : 'bg-white text-ink-light border-slate-200 hover:bg-slate-50'
            }`}
          >
            {type || 'All'}
          </button>
        ))}
      </div>

      {accounts.length === 0 && !loading && (
        <Card className="p-6 mb-5 text-sm text-ink-light">
          You need at least one account before adding transactions. Add one from the Accounts page first.
        </Card>
      )}

      <Card>
        {loading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3, 4].map((i) => <div key={i} className="h-14 bg-slate-50 rounded-lg animate-pulse" />)}
          </div>
        ) : transactions.length === 0 ? (
          <p className="p-10 text-center text-sm text-ink-light">No transactions found.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {transactions.map((t) => {
              const Icon = TYPE_ICON[t.transaction_type]
              const colors = TYPE_COLOR[t.transaction_type]
              const isIncome = t.transaction_type === 'income'
              return (
                <div key={t.transaction_id} className="flex items-center justify-between px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-9 h-9 rounded-full flex items-center justify-center shrink-0 ${colors.bg}`}>
                      <Icon size={16} className={colors.text} strokeWidth={2.5} />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-ink">{t.description || t.category?.category_name || 'Transaction'}</p>
                      <p className="text-xs text-ink-light">
                        {t.category?.category_name || 'Uncategorized'} · {t.payment_mode || '—'} ·{' '}
                        {new Date(t.transaction_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-sm font-semibold tabular-nums ${isIncome ? 'text-mint' : t.transaction_type === 'expense' ? 'text-coral' : 'text-teal'}`}>
                      {isIncome ? '+' : t.transaction_type === 'expense' ? '-' : ''}{formatCurrency(t.amount)}
                    </span>
                    <button
                      onClick={() => handleDelete(t.transaction_id)}
                      className="text-ink-light hover:text-coral p-1"
                      aria-label="Delete transaction"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Card>

      {showModal && (
        <TransactionFormModal
          accounts={accounts}
          categories={categories}
          onClose={() => setShowModal(false)}
          onCreated={load}
        />
      )}
    </AppShell>
  )
}
