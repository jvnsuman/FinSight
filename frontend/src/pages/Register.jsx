import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser } from '../api/authApi'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ErrorBanner, SuccessBanner } from '../components/common/Card'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = { name: form.name, email: form.email, password: form.password }
      if (form.phone) payload.phone = form.phone
      const res = await registerUser(payload)
      setSuccess(res.data.message)
      setTimeout(
        () => navigate('/verify-pending', { state: { email: form.email, password: form.password } }),
        1200
      )
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(' '))
      } else {
        setError(detail || 'Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="font-display text-3xl font-semibold text-white">
            Fin<span className="text-mint">Sight</span>
          </span>
          <p className="text-slate-400 text-sm mt-2">Create your account to get started.</p>
        </div>

        <div className="bg-white rounded-xl shadow-soft p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Full name" value={form.name} onChange={handleChange('name')} placeholder="Arjun Mehta" required />
            <Input label="Email" type="email" value={form.email} onChange={handleChange('email')} placeholder="you@example.com" required />
            <Input
              label="Password"
              type="password"
              value={form.password}
              onChange={handleChange('password')}
              placeholder="At least 8 characters"
              minLength={8}
              required
            />
            <Input
              label="Phone (optional)"
              type="tel"
              value={form.phone}
              onChange={handleChange('phone')}
              placeholder="10-digit Indian mobile number"
            />

            <ErrorBanner message={error} />
            <SuccessBanner message={success} />

            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </Button>

            <p className="text-center text-sm pt-1">
              Already have an account?{' '}
              <Link to="/login" className="text-teal hover:underline">Log in</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
