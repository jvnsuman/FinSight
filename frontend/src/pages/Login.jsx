import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TrendingUp, Wallet, PieChart, Shield } from 'lucide-react'
import { loginUser } from '../api/authApi'
import { useAuth } from '../context/AuthContext'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { ErrorBanner } from '../components/common/Card'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await loginUser(email, password)
      login(res.data.access_token, res.data.user)
      navigate('/dashboard')
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Login failed. Check your email and password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Left side - Image & Branding (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-navy items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-navy via-navy/80 to-teal/90 z-10" />
        <img 
          src="/login-bg.jpg" 
          alt="Financial Planning" 
          className="absolute inset-0 w-full h-full object-cover opacity-50 mix-blend-overlay"
        />
        
        <div className="relative z-30 p-12 text-center">
          <span className="font-display text-5xl font-semibold text-white tracking-tight">
            Fin<span className="text-mint">Sight</span>
          </span>
          <p className="text-slate-200 text-lg mt-6 max-w-sm mx-auto leading-relaxed">
            Your personal financial command center. Track expenses, monitor portfolios, and plan for your future.
          </p>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative overflow-hidden bg-slate-50">
        
        {/* Subtle background decoration */}
        <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-teal/5 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[400px] h-[400px] bg-navy/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="w-full max-w-md bg-white/90 backdrop-blur-xl p-8 sm:p-12 rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 relative z-10">
          
          {/* Mobile Branding */}
          <div className="text-center mb-8 lg:hidden">
            <span className="font-display text-3xl font-semibold text-navy">
              Fin<span className="text-teal">Sight</span>
            </span>
          </div>

          <div className="text-center mb-10">
            <div className="w-16 h-16 bg-gradient-to-br from-teal/10 to-navy/5 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-sm border border-teal/10 rotate-3 transition-transform hover:rotate-0 duration-300">
              <Wallet className="text-teal -rotate-3 transition-transform hover:rotate-0 duration-300" size={32} />
            </div>
            <h2 className="text-3xl font-bold text-navy tracking-tight">Welcome back</h2>
            <p className="text-slate-500 text-sm mt-3 font-medium">Let's look at your money.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            <ErrorBanner message={error} />

            <Button type="submit" fullWidth disabled={loading}>
              {loading ? 'Logging in...' : 'Log in'}
            </Button>

            <div className="flex items-center justify-between text-sm pt-4">
              <Link to="/forgot-password" className="text-teal hover:text-teal/80 font-medium transition-colors">
                Forgot password?
              </Link>
              <Link to="/register" className="text-teal hover:text-teal/80 font-medium transition-colors">
                Create an account
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
