export default function Input({ label, error, className = '', ...props }) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-ink mb-1.5">{label}</label>
      )}
      <input
        className={`w-full rounded-lg border px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-light/60
          focus:outline-none focus:ring-2 focus:ring-teal/30 focus:border-teal
          ${error ? 'border-coral' : 'border-slate-200'} ${className}`}
        {...props}
      />
      {error && <p className="mt-1.5 text-xs text-coral">{error}</p>}
    </div>
  )
}
