import { useState } from 'react'
import { Link } from 'react-router-dom'
import { forgotPassword } from '../api/authApi'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ErrorBanner, SuccessBanner } from '../components/common/Card'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const res = await forgotPassword(email)
      setSuccess(res.data.message)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="font-display text-3xl font-semibold text-white">
            Finance <span className="text-mint">Analytics</span>
          </span>
        </div>
        <div className="bg-white rounded-xl shadow-soft p-8">
          <h1 className="font-display text-lg font-semibold text-ink mb-1">Reset your password</h1>
          <p className="text-ink-light text-sm mb-6">We'll email you a link to reset it. The link expires in 15 minutes.</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            <ErrorBanner message={error} />
            <SuccessBanner message={success} />
            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </Button>
            <p className="text-center text-sm pt-1">
              <Link to="/login" className="text-teal hover:underline">Back to login</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
