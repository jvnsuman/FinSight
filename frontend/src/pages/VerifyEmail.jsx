import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { verifyEmail } from '../api/authApi'
import Button from '../components/common/Button'

export default function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [status, setStatus] = useState('loading') // loading | success | error
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('No verification token found in the link.')
      return
    }
    verifyEmail(token)
      .then((res) => {
        setStatus('success')
        setMessage(res.data.message)
      })
      .catch((err) => {
        setStatus('error')
        setMessage(err.response?.data?.detail || 'Verification failed.')
      })
  }, [token])

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-soft p-8 text-center">
        {status === 'loading' && (
          <>
            <Loader2 className="mx-auto mb-4 animate-spin text-teal" size={40} />
            <p className="text-ink-light text-sm">Verifying your email...</p>
          </>
        )}
        {status === 'success' && (
          <>
            <CheckCircle2 className="mx-auto mb-4 text-mint" size={48} />
            <h1 className="font-display text-xl font-semibold text-ink mb-2">Email verified</h1>
            <p className="text-ink-light text-sm mb-6">{message}</p>
            <Link to="/login"><Button fullWidth>Go to login</Button></Link>
          </>
        )}
        {status === 'error' && (
          <>
            <XCircle className="mx-auto mb-4 text-coral" size={48} />
            <h1 className="font-display text-xl font-semibold text-ink mb-2">Verification failed</h1>
            <p className="text-ink-light text-sm mb-6">{message}</p>
            <Link to="/login"><Button variant="secondary" fullWidth>Back to login</Button></Link>
          </>
        )}
      </div>
    </div>
  )
}
