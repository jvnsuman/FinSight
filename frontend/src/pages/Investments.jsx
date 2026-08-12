import { useEffect, useState } from 'react'
import { Plus, TrendingUp, TrendingDown, Landmark, Coins, Wallet, Trash2, Pencil, X, ArrowUpCircle, ArrowDownCircle, PiggyBank } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import {
  getInvestments,
  createInvestment,
  updateInvestment,
  deleteInvestment,
  getPortfolioSummary,
  getLivePrice,
} from '../api/investmentsApi'
import { getWallet, depositFunds, buyHolding, sellHolding } from '../api/tradingApi'

function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
}

function formatPercent(pct) {
  if (pct === null || pct === undefined) return 'â€”'
  const sign = pct > 0 ? '+' : ''
  return `${sign}${pct.toFixed(2)}%`
}

const ASSET_TYPE_LABELS = {
  stock: 'Stock',
  mutual_fund: 'Mutual Fund',
  etf: 'ETF',
  bond: 'Bond',
  gold: 'Gold',
  cash: 'Cash',
}

const ASSET_TYPE_ICONS = {
  stock: TrendingUp,
  mutual_fund: Landmark,
  etf: Landmark,
  bond: Landmark,
  gold: Coins,
  cash: Wallet,
}

function InvestmentFormModal({ existing, onClose, onSaved }) {
  const isEdit = Boolean(existing)
  const [form, setForm] = useState({
    asset_type: existing?.asset_type || 'stock',
    asset_name: existing?.asset_name || '',
    symbol: existing?.symbol || '',
    quantity: existing?.quantity ?? '',
    purchase_price: existing?.purchase_price ?? '',
    purchase_date: existing?.purchase_date || '',
    notes: existing?.notes || '',
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [livePrice, setLivePrice] = useState(null)
  const [fetchingPrice, setFetchingPrice] = useState(false)

  // Debounced live price fetcher
  useEffect(() => {
    if (!form.symbol) {
      setLivePrice(null)
      return
    }
    const timer = setTimeout(async () => {
      setFetchingPrice(true)
      try {
        const res = await getLivePrice(form.symbol)
        setLivePrice(res.data.price)
      } catch (err) {
        setLivePrice(null)
      } finally {
        setFetchingPrice(false)
      }
    }, 600)
    return () => clearTimeout(timer)
  }, [form.symbol])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = {
        asset_type: form.asset_type,
        asset_name: form.asset_name,
        symbol: form.symbol || undefined,
        quantity: parseFloat(form.quantity),
        purchase_price: parseFloat(form.purchase_price),
        purchase_date: form.purchase_date,
        notes: form.notes || undefined,
      }
      if (isEdit) {
        await updateInvestment(existing.investment_id, payload)
      } else {
        await createInvestment(payload)
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save this holding.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">
            {isEdit ? 'Edit holding' : 'Add holding'}
          </h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-ink mb-1.5">Asset type</label>
            <select
              value={form.asset_type}
              onChange={(e) => setForm({ ...form, asset_type: e.target.value })}
              className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
              disabled={isEdit}
            >
              {Object.entries(ASSET_TYPE_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <Input
            label="Asset name"
            value={form.asset_name}
            onChange={(e) => setForm({ ...form, asset_name: e.target.value })}
            placeholder="HDFC Bank"
            required
          />
          <Input
            label="Symbol / ticker (optional)"
            value={form.symbol}
            onChange={(e) => setForm({ ...form, symbol: e.target.value })}
            placeholder="e.g. TCS.NS or RELIANCE.BO"
          />
          {form.symbol && (
            <p className="text-xs text-ink-light -mt-2">
              {fetchingPrice ? 'Fetching live price...' : livePrice ? `Current market price: ${formatCurrency(livePrice)}` : 'Could not fetch live price for this symbol.'}
            </p>
          )}
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Quantity"
              type="number"
              step="0.0001"
              min="0.0001"
              value={form.quantity}
              onChange={(e) => setForm({ ...form, quantity: e.target.value })}
              placeholder="10"
              required
            />
            <Input
              label="Purchase price / unit"
              type="number"
              step="0.01"
              min="0.01"
              value={form.purchase_price}
              onChange={(e) => setForm({ ...form, purchase_price: e.target.value })}
              placeholder="1500.50"
              required
            />
          </div>
          <Input
            label="Purchase date"
            type="date"
            value={form.purchase_date}
            onChange={(e) => setForm({ ...form, purchase_date: e.target.value })}
            required
          />
          <Input
            label="Notes (optional)"
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
            placeholder="Initial buy"
          />
          <ErrorBanner message={error} />
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving}>
              {saving ? 'Saving...' : isEdit ? 'Save changes' : 'Add holding'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function DepositModal({ onClose, onSaved }) {
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      await depositFunds(parseFloat(amount))
      onSaved()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not add funds.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-sm p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Add funds</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <p className="text-xs text-ink-light mb-4">
          Transfer money from your Savings Pool to your simulated trading wallet (Demat account) to use for investments.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Amount"
            type="number"
            step="0.01"
            min="0.01"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="10000"
            required
            autoFocus
          />
          <ErrorBanner message={error} />
          <div className="flex gap-3 pt-1">
            <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
            <Button type="submit" fullWidth disabled={saving}>{saving ? 'Adding...' : 'Add funds'}</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

function TradeModal({ mode, holdings, walletBalance, onClose, onSaved }) {
  // mode: 'buy' or 'sell'
  const isBuy = mode === 'buy'
  const [form, setForm] = useState({
    investment_id: holdings[0]?.investment_id || '',
    asset_type: 'stock',
    asset_name: '',
    symbol: '',
    quantity: '',
    price: '',
  })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [livePrice, setLivePrice] = useState(null)
  const [fetchingPrice, setFetchingPrice] = useState(false)

  // Debounced live price fetcher for Buy mode
  useEffect(() => {
    if (!isBuy || !form.symbol) {
      setLivePrice(null)
      return
    }
    const timer = setTimeout(async () => {
      setFetchingPrice(true)
      try {
        const res = await getLivePrice(form.symbol)
        setLivePrice(res.data.price)
      } catch (err) {
        setLivePrice(null)
      } finally {
        setFetchingPrice(false)
      }
    }, 600)
    return () => clearTimeout(timer)
  }, [form.symbol, isBuy])

  const selectedHolding = !isBuy ? holdings.find((h) => h.investment_id === Number(form.investment_id)) : null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      if (isBuy) {
        await buyHolding({
          asset_type: form.asset_type,
          asset_name: form.asset_name,
          symbol: form.symbol || undefined,
          quantity: parseFloat(form.quantity),
          price: form.price ? parseFloat(form.price) : undefined,
        })
      } else {
        await sellHolding({
          investment_id: Number(form.investment_id),
          quantity: parseFloat(form.quantity),
          price: form.price ? parseFloat(form.price) : undefined,
        })
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(err.response?.data?.detail || `Could not complete this ${mode}.`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">
            {isBuy ? 'Buy' : 'Sell'}
          </h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <p className="text-xs text-ink-light mb-4">
          Simulated trade â€” no real money or brokerage is involved.
          {isBuy && ` Wallet balance: ${formatCurrency(walletBalance)}`}
        </p>

        {!isBuy && holdings.length === 0 ? (
          <p className="text-sm text-ink-light">You have no holdings to sell yet.</p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {isBuy ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-ink mb-1.5">Asset type</label>
                  <select
                    value={form.asset_type}
                    onChange={(e) => setForm({ ...form, asset_type: e.target.value })}
                    className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
                  >
                    {Object.entries(ASSET_TYPE_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </div>
                <Input
                  label="Asset name"
                  value={form.asset_name}
                  onChange={(e) => setForm({ ...form, asset_name: e.target.value })}
                  placeholder="HDFC Bank"
                  required
                />
                <Input
                  label="Symbol / ticker (optional)"
                  value={form.symbol}
                  onChange={(e) => setForm({ ...form, symbol: e.target.value })}
                  placeholder="e.g. TCS.NS or RELIANCE.BO"
                />
                {form.symbol && (
                  <p className="text-xs text-ink-light -mt-2">
                    {fetchingPrice ? 'Fetching live price...' : livePrice ? `Current market price: ${formatCurrency(livePrice)}` : 'Could not fetch live price for this symbol.'}
                  </p>
                )}
                <p className="text-xs text-ink-light -mt-2">
                  Buying more of a symbol you already hold averages into that holding rather than creating a new row.
                </p>
              </>
            ) : (
              <div>
                <label className="block text-sm font-medium text-ink mb-1.5">Holding</label>
                <select
                  value={form.investment_id}
                  onChange={(e) => setForm({ ...form, investment_id: e.target.value })}
                  className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
                >
                  {holdings.map((h) => (
                    <option key={h.investment_id} value={h.investment_id}>
                      {h.asset_name} ({h.quantity} held)
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Quantity"
                type="number"
                step="0.0001"
                min="0.0001"
                max={!isBuy ? selectedHolding?.quantity : undefined}
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                placeholder="10"
                required
              />
              <Input
                label="Price / unit (optional)"
                type="number"
                step="0.01"
                min="0.01"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
                placeholder="Uses market price"
              />
            </div>
            <p className="text-xs text-ink-light -mt-2">
              Leave price blank to use the current cached/market price for this symbol.
            </p>

            <ErrorBanner message={error} />
            <div className="flex gap-3 pt-1">
              <Button variant="secondary" onClick={onClose} fullWidth type="button">Cancel</Button>
              <Button type="submit" fullWidth disabled={saving}>
                {saving ? 'Submitting...' : isBuy ? 'Buy' : 'Sell'}
              </Button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default function Investments() {
  const [investments, setInvestments] = useState([])
  const [summary, setSummary] = useState(null)
  const [wallet, setWallet] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingInvestment, setEditingInvestment] = useState(null)
  const [tradeMode, setTradeMode] = useState(null) // 'buy' | 'sell' | null
  const [showDeposit, setShowDeposit] = useState(false)

  const load = async () => {
    setLoading(true)
    const [investmentsRes, summaryRes, walletRes] = await Promise.all([
      getInvestments(false, true),
      getPortfolioSummary(),
      getWallet(),
    ])
    setInvestments(investmentsRes.data)
    setSummary(summaryRes.data)
    setWallet(walletRes.data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (investmentId) => {
    if (!confirm('Remove this holding? Its historical return data will be preserved.')) return
    await deleteInvestment(investmentId)
    load()
  }

  const openEdit = (inv) => {
    setEditingInvestment(inv)
    setShowModal(true)
  }

  const openAdd = () => {
    setEditingInvestment(null)
    setShowModal(true)
  }

  const totalInvested = investments.reduce((sum, inv) => sum + (inv.invested_value || 0), 0)
  const isPositive = (summary?.total_return_amount || 0) >= 0

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-7 flex-wrap gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">Investments</h1>
          <p className="text-sm text-ink-light mt-0.5">Your portfolio holdings.</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="secondary" onClick={() => setShowDeposit(true)}><PiggyBank size={16} /> Add funds</Button>
          <Button variant="secondary" onClick={() => setTradeMode('sell')}><ArrowDownCircle size={16} /> Sell</Button>
          <Button onClick={() => setTradeMode('buy')}><ArrowUpCircle size={16} /> Buy</Button>
          <Button variant="secondary" onClick={openAdd}><Plus size={16} /> Add holding manually</Button>
        </div>
      </div>

      {!loading && wallet && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <Card className="p-5">
            <p className="text-xs text-ink-light mb-1">Simulated trading wallet</p>
            <p className="font-display text-xl font-semibold text-ink tabular-nums">{formatCurrency(wallet.cash_balance)}</p>
            <p className="text-xs text-ink-light mt-1">No real money — used for buying/selling in Finance Analytics Platform.</p>
          </Card>
          <Card className="p-5">
            <p className="text-xs text-ink-light mb-1">Savings pool</p>
            <p className="font-display text-xl font-semibold text-ink tabular-nums">{formatCurrency(wallet.savings_pool)}</p>
            <p className="text-xs text-ink-light mt-1">
              Refills monthly from income minus expenses, plus leftover wallet cash. Goal allocations and expense overspends draw from this.
            </p>
          </Card>
        </div>
      )}

      {!loading && investments.length > 0 && summary && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <Card className="p-5">
            <p className="text-xs text-ink-light mb-1">Total invested</p>
            <p className="font-display text-2xl font-semibold text-ink tabular-nums">
              {formatCurrency(summary.total_invested)}
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-xs text-ink-light mb-1">Current value</p>
            <p className="font-display text-2xl font-semibold text-ink tabular-nums">
              {formatCurrency(summary.total_current_value)}
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-xs text-ink-light mb-1">Overall return</p>
            <div className="flex items-baseline gap-2">
              <p className={`font-display text-2xl font-semibold tabular-nums ${isPositive ? 'text-mint' : 'text-coral'}`}>
                {formatCurrency(summary.total_return_amount)}
              </p>
              <span className={`text-sm font-medium flex items-center gap-0.5 ${isPositive ? 'text-mint' : 'text-coral'}`}>
                {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {formatPercent(summary.total_return_pct)}
              </span>
            </div>
          </Card>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <div key={i} className="bg-white rounded-xl border border-slate-100 h-16 animate-pulse" />)}
        </div>
      ) : investments.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-ink-light text-sm mb-4">No holdings yet. Buy your first stock, or add one manually if you already hold it elsewhere.</p>
          <div className="flex items-center justify-center gap-3">
            <Button variant="secondary" onClick={openAdd}><Plus size={16} /> Add manually</Button>
            <Button onClick={() => setTradeMode('buy')}><ArrowUpCircle size={16} /> Buy</Button>
          </div>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left text-xs text-ink-light">
                <th className="px-5 py-3 font-medium">Asset</th>
                <th className="px-5 py-3 font-medium">Type</th>
                <th className="px-5 py-3 font-medium text-right">Quantity</th>
                <th className="px-5 py-3 font-medium text-right">Purchase price</th>
                <th className="px-5 py-3 font-medium text-right">Invested value</th>
                <th className="px-5 py-3 font-medium text-right">Current value</th>
                <th className="px-5 py-3 font-medium text-right">Return</th>
                <th className="px-5 py-3 font-medium">Purchase date</th>
                <th className="px-5 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {investments.map((inv) => {
                const Icon = ASSET_TYPE_ICONS[inv.asset_type] || TrendingUp
                return (
                  <tr key={inv.investment_id} className="border-b border-slate-50 last:border-0 hover:bg-surface/60">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-teal/10 flex items-center justify-center shrink-0">
                          <Icon size={15} className="text-teal" />
                        </div>
                        <div>
                          <p className="font-medium text-ink">{inv.asset_name}</p>
                          {inv.symbol && <p className="text-xs text-ink-light">{inv.symbol}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-ink-light">{ASSET_TYPE_LABELS[inv.asset_type]}</td>
                    <td className="px-5 py-3.5 text-right tabular-nums text-ink">{inv.quantity}</td>
                    <td className="px-5 py-3.5 text-right tabular-nums text-ink">{formatCurrency(inv.purchase_price)}</td>
                    <td className="px-5 py-3.5 text-right tabular-nums text-ink">{formatCurrency(inv.invested_value)}</td>
                    <td className="px-5 py-3.5 text-right tabular-nums font-medium text-ink">
                      {inv.current_value != null ? formatCurrency(inv.current_value) : 'â€”'}
                    </td>
                    <td className="px-5 py-3.5 text-right tabular-nums">
                      {inv.return_pct != null ? (
                        <span className={inv.return_pct >= 0 ? 'text-mint' : 'text-coral'}>
                          {formatPercent(inv.return_pct)}
                        </span>
                      ) : (
                        <span className="text-ink-light">â€”</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-ink-light">{inv.purchase_date}</td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => openEdit(inv)}
                          className="text-ink-light hover:text-teal p-1.5"
                          aria-label="Edit holding"
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(inv.investment_id)}
                          className="text-ink-light hover:text-coral p-1.5"
                          aria-label="Remove holding"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </Card>
      )}

      {showModal && (
        <InvestmentFormModal
          existing={editingInvestment}
          onClose={() => setShowModal(false)}
          onSaved={load}
        />
      )}

      {showDeposit && (
        <DepositModal
          onClose={() => setShowDeposit(false)}
          onSaved={load}
        />
      )}

      {tradeMode && (
        <TradeModal
          mode={tradeMode}
          holdings={investments}
          walletBalance={wallet?.cash_balance || 0}
          onClose={() => setTradeMode(null)}
          onSaved={load}
        />
      )}
    </AppShell>
  )
}
