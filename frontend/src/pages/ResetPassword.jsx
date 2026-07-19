import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { resetPassword } from '../api/authApi'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ErrorBanner, SuccessBanner } from '../components/common/Card'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const res = await resetPassword(token, password)
      setSuccess(res.data.message)
      setTimeout(() => navigate('/login'), 2000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Reset failed. The link may have expired.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <span className="font-display text-3xl font-semibold text-white">
            Fin<span className="text-mint">Sight</span>
          </span>
        </div>
        <div className="bg-white rounded-xl shadow-soft p-8">
          <h1 className="font-display text-lg font-semibold text-ink mb-1">Set a new password</h1>
          <p className="text-ink-light text-sm mb-6">You'll need to log in again everywhere after this.</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="New password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              required
            />
            <ErrorBanner message={error} />
            <SuccessBanner message={success} />
            <Button type="submit" fullWidth disabled={loading || !token}>
              {loading ? 'Resetting...' : 'Reset password'}
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
