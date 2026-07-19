import { useState } from 'react'
import { User as UserIcon, Lock, X } from 'lucide-react'
import AppShell from '../components/layout/AppShell'
import { Card, ErrorBanner, SuccessBanner, PageLoader } from '../components/common/Card'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import { updateProfile, changePassword } from '../api/authApi'
import { useAuth } from '../context/AuthContext'

// Mirrors the backend's validate_indian_mobile rule: exactly 10 digits,
// first digit 6-9 (how Indian mobile numbers are actually allocated).
function isValidIndianMobile(value) {
  return /^[6-9]\d{9}$/.test(value)
}

function ProfileDetailsForm({ user, onSaved }) {
  const [form, setForm] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    profession: user?.profession || '',
    monthly_income: user?.monthly_income ?? '',
    currency: user?.currency || 'INR',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (form.phone && !isValidIndianMobile(form.phone)) {
      setError('Enter a valid 10-digit mobile number.')
      return
    }

    setSaving(true)
    try {
      const res = await updateProfile({
        name: form.name,
        phone: form.phone || undefined,
        profession: form.profession || undefined,
        monthly_income: form.monthly_income !== '' ? parseFloat(form.monthly_income) : undefined,
        currency: form.currency,
      })
      onSaved(res.data)
      setSuccess('Profile updated.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update profile.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card className="p-6">
      <h2 className="font-display text-base font-semibold text-ink mb-4">Profile details</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <ErrorBanner message={error} />
        <SuccessBanner message={success} />

        <Input
          label="Full name"
          value={form.name}
          onChange={handleChange('name')}
          required
        />

        <Input label="Email" value={user?.email || ''} disabled className="opacity-60 cursor-not-allowed" />

        <Input
          label="Mobile number"
          value={form.phone}
          onChange={handleChange('phone')}
          placeholder="9876543210"
          maxLength={10}
          inputMode="numeric"
        />

        <Input
          label="Profession"
          value={form.profession}
          onChange={handleChange('profession')}
          placeholder="Salaried, Business Owner, Student, Freelancer..."
        />

        <Input
          label="Monthly income"
          type="number"
          value={form.monthly_income}
          onChange={handleChange('monthly_income')}
          placeholder="50000"
        />

        <div>
          <label className="block text-sm font-medium text-ink mb-1.5">Currency</label>
          <select
            value={form.currency}
            onChange={handleChange('currency')}
            className="w-full rounded-lg border border-slate-200 px-3.5 py-2.5 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal"
          >
            <option value="INR">INR (₹)</option>
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€)</option>
          </select>
        </div>

        <Button type="submit" fullWidth disabled={saving}>
          {saving ? 'Saving...' : 'Save changes'}
        </Button>
      </form>
    </Card>
  )
}

function ChangePasswordModal({ onClose, onChanged }) {
  const [form, setForm] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (form.new_password.length < 8) {
      setError('New password must be at least 8 characters.')
      return
    }
    if (form.new_password !== form.confirm_password) {
      setError('New password and confirmation do not match.')
      return
    }

    setSaving(true)
    try {
      const res = await changePassword(form.current_password, form.new_password)
      onChanged(res.data)
      setSuccess('Password changed.')
      setForm({ current_password: '', new_password: '', confirm_password: '' })
      setTimeout(onClose, 1200)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not change password.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center px-4 z-50">
      <div className="bg-white rounded-xl shadow-soft w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-display text-lg font-semibold text-ink">Change password</h2>
          <button onClick={onClose} className="text-ink-light hover:text-ink"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <ErrorBanner message={error} />
          <SuccessBanner message={success} />

          <Input
            label="Current password"
            type="password"
            value={form.current_password}
            onChange={handleChange('current_password')}
            required
          />
          <Input
            label="New password"
            type="password"
            value={form.new_password}
            onChange={handleChange('new_password')}
            required
          />
          <Input
            label="Confirm new password"
            type="password"
            value={form.confirm_password}
            onChange={handleChange('confirm_password')}
            required
          />

          <Button type="submit" fullWidth disabled={saving}>
            {saving ? 'Updating...' : 'Update password'}
          </Button>
        </form>
      </div>
    </div>
  )
}

export default function Profile() {
  const { user, setUser, loading, login } = useAuth()
  const [showPasswordModal, setShowPasswordModal] = useState(false)

  if (loading) return <PageLoader />

  return (
    <AppShell>
      <div className="max-w-lg space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-mint-light flex items-center justify-center">
            <UserIcon size={20} className="text-teal" />
          </div>
          <h1 className="font-display text-2xl font-semibold text-ink">Profile</h1>
        </div>

        <ProfileDetailsForm user={user} onSaved={(updatedUser) => setUser(updatedUser)} />

        <Card className="p-6 flex items-center justify-between">
          <div>
            <h2 className="font-display text-base font-semibold text-ink">Password</h2>
            <p className="text-sm text-ink-light mt-0.5">Change the password used to log in.</p>
          </div>
          <Button variant="secondary" onClick={() => setShowPasswordModal(true)}>
            <Lock size={16} />
            Change password
          </Button>
        </Card>

        {showPasswordModal && (
          <ChangePasswordModal
            onClose={() => setShowPasswordModal(false)}
            onChanged={(data) => {
              // Backend issues a fresh token (old one is invalidated on other
              // sessions) - re-store it so this session keeps working seamlessly.
              login(data.access_token, data.user)
            }}
          />
        )}
      </div>
    </AppShell>
  )
}
