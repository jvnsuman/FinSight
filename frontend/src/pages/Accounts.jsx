import { useEffect, useState } from 'react'
import { Plus, Landmark, CreditCard, Wallet, Trash2, X } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { getAccounts, createAccount, deleteAccount } from '../api/accountsApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

const ACCOUNT_ICONS = { bank: Landmark, card: CreditCard, wallet: Wallet }

function AccountFormModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ account_name: '', account_type: 'bank', bank_name: '', balance: '' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await createAccount({
        account_name: form.account_name,
        account_type: form.account_type,
        bank_name: form.bank_name || undefined,
        balance: form.balance ? parseFloat(form.balance) : 0,
      })
      onCreated()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create account.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Add account</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Account name"
            value={form.account_name}
            onChange={(e) => setForm({ ...form, account_name: e.target.value })}
            placeholder="HDFC Savings"
            required
          />
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Account type</label>
            <select
              value={form.account_type}
              onChange={(e) => setForm({ ...form, account_type: e.target.value })}
              className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
            >
              <option value="bank">Bank</option>
              <option value="card">Card</option>
              <option value="wallet">Wallet</option>
            </select>
          </div>
          <Input
            label="Bank / provider name (optional)"
            value={form.bank_name}
            onChange={(e) => setForm({ ...form, bank_name: e.target.value })}
            placeholder="HDFC Bank"
          />
          <Input
            label="Starting balance"
            type="number"
            step="0.01"
            min="0"
            value={form.balance}
            onChange={(e) => setForm({ ...form, balance: e.target.value })}
            placeholder="0"
          />
          <ErrorBanner message={error} />
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving}>{saving ? 'Adding...' : 'Add account'}</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function Accounts() {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)

  const load = async () => {
    setLoading(true)
    const res = await getAccounts()
    setAccounts(res.data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (accountId) => {
    if (!confirm('Remove this account? Its transaction history will be preserved.')) return
    await deleteAccount(accountId)
    load()
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Accounts</h1>
          <p className="text-sm text-ink-light mt-0.5">Your banks, cards, and wallets.</p>
        </div>
        <Button onClick={() => setShowModal(true)}><Plus size={16} /> Add account</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <div key={i} className="bg-white rounded-xl border border-slate-100 h-32 animate-pulse" />)}
        </div>
      ) : accounts.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-ink-light text-sm mb-4">No accounts yet. Add your first bank account, card, or wallet.</p>
          <Button onClick={() => setShowModal(true)} className="mx-auto"><Plus size={16} /> Add account</Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {accounts.map((acc) => {
            const Icon = ACCOUNT_ICONS[acc.account_type] || Wallet
            return (
              <Card key={acc.account_id} className="p-5">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 rounded-lg bg-teal/10 flex items-center justify-center">
                    <Icon size={18} className="text-teal" />
                  </div>
                  {!acc.is_default && (
                    <button
                      onClick={() => handleDelete(acc.account_id)}
                      className="text-ink-light hover:text-coral p-1"
                      aria-label="Remove account"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-ink">{acc.account_name}</p>
                  {acc.is_default && (
                    <span className="text-[10px] font-medium text-teal bg-teal/10 px-1.5 py-0.5 rounded">Default</span>
                  )}
                </div>
                <p className="text-xs text-ink-light mb-2">{acc.bank_name || acc.account_type}</p>
                <p className="font-display text-xl font-semibold text-ink tabular-nums">{formatCurrency(acc.balance)}</p>
              </Card>
            )
          })}
        </div>
      )}

      {showModal && <AccountFormModal onClose={() => setShowModal(false)} onCreated={load} />}
    </AppShell>
  )
}
