export function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl shadow-card border border-slate-100 ${className}`}>
      {children}
    </div>
  )
}

export function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-teal border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-ink-light">Loading FinSight...</p>
      </div>
    </div>
  )
}

export function ErrorBanner({ message }) {
  if (!message) return null
  return (
    <div className="bg-coral-light border border-coral/20 text-coral text-sm rounded-lg px-4 py-3">
      {message}
    </div>
  )
}

export function SuccessBanner({ message }) {
  if (!message) return null
  return (
    <div className="bg-mint-light border border-mint/30 text-navy text-sm rounded-lg px-4 py-3">
      {message}
    </div>
  )
}
