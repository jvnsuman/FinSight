import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { MailCheck, Loader2 } from 'lucide-react'
import { resendVerification, getVerificationStatus, loginUser } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import Button from '../components/common/Button'
import { ErrorBanner, SuccessBanner } from '../components/common/Card'

const POLL_INTERVAL_MS = 4000
const RESEND_COOLDOWN_SECONDS = 30

export default function VerifyPending() {
  const location = useLocation()
  const navigate = useNavigate()
  const { login } = useAuth()

  // Came from a failed login attempt - held only in memory (router state),
  // never persisted, so we can silently log the user in the moment their
  // email verifies without asking them to type their password again.
  const { email, password } = location.state || {}

  const [resendCooldown, setResendCooldown] = useState(0)
  const [resendError, setResendError] = useState('')
  const [resendSuccess, setResendSuccess] = useState('')
  const [autoLoggingIn, setAutoLoggingIn] = useState(false)
  const pollRef = useRef(null)

  // No email in state means someone landed here directly (refresh, bookmark,
  // back button) - nothing to poll for, so the effects below just no-op.
  const hasPendingVerification = Boolean(email)

  useEffect(() => {
    if (!hasPendingVerification) return undefined

    const poll = async () => {
      try {
        const res = await getVerificationStatus(email)
        if (res.data.is_verified) {
          clearInterval(pollRef.current)
          setAutoLoggingIn(true)
          try {
            const loginRes = await loginUser(email, password)
            login(loginRes.data.access_token, loginRes.data.user)
            navigate('/dashboard')
          } catch {
            // Verified but auto-login failed for some other reason (e.g. password
            // changed elsewhere in the meantime) - send them to log in manually.
            navigate('/login')
          }
        }
      } catch {
        // Transient network hiccup - just try again on the next tick.
      }
    }

    pollRef.current = setInterval(poll, POLL_INTERVAL_MS)
    poll() // check immediately too, don't make them wait a full interval
    return () => clearInterval(pollRef.current)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasPendingVerification, email])

  useEffect(() => {
    if (resendCooldown <= 0) return undefined
    const t = setTimeout(() => setResendCooldown((s) => s - 1), 1000)
    return () => clearTimeout(t)
  }, [resendCooldown])

  if (!hasPendingVerification) {
    return (
      <div className="min-h-screen bg-navy flex items-center justify-center px-4">
        <div className="w-full max-w-md bg-white rounded-xl shadow-soft p-8 text-center">
          <MailCheck className="mx-auto mb-4 text-teal" size={40} />
          <h1 className="font-display text-xl font-semibold text-ink mb-2">Verify your email</h1>
          <p className="text-ink-light text-sm mb-6">
            Log in again to resume email verification for your account.
          </p>
          <Link to="/login"><Button fullWidth>Back to login</Button></Link>
        </div>
      </div>
    )
  }

  const handleResend = async () => {
    setResendError('')
    setResendSuccess('')
    try {
      await resendVerification(email)
      setResendSuccess('Verification email sent. Check your inbox.')
      setResendCooldown(RESEND_COOLDOWN_SECONDS)
    } catch (err) {
      setResendError(err.response?.data?.detail || 'Could not resend the email. Try again shortly.')
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-soft p-8 text-center">
        {autoLoggingIn ? (
          <>
            <Loader2 className="mx-auto mb-4 animate-spin text-teal" size={40} />
            <h1 className="font-display text-xl font-semibold text-ink mb-2">Email verified!</h1>
            <p className="text-ink-light text-sm">Logging you in...</p>
          </>
        ) : (
          <>
            <MailCheck className="mx-auto mb-4 text-teal" size={40} />
            <h1 className="font-display text-xl font-semibold text-ink mb-2">Verify your email</h1>
            <p className="text-ink-light text-sm mb-1">
              We sent a verification link to
            </p>
            <p className="text-ink font-medium text-sm mb-6">{email}</p>
            <p className="text-ink-light text-xs mb-6">
              This page will automatically log you in as soon as you click the link -
              no need to come back and retry.
            </p>

            <ErrorBanner message={resendError} />
            <SuccessBanner message={resendSuccess} />

            <Button
              variant="secondary"
              fullWidth
              onClick={handleResend}
              disabled={resendCooldown > 0}
              className="mt-4"
            >
              {resendCooldown > 0 ? `Resend available in ${resendCooldown}s` : 'Resend verification email'}
            </Button>

            <Link to="/login" className="block text-sm text-teal hover:underline mt-4">
              Back to login
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
