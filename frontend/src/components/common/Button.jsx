export default function Button({
  children,
  variant = 'primary',
  type = 'button',
  onClick,
  disabled = false,
  fullWidth = false,
  className = '',
}) {
  const base = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold text-sm px-4 py-2.5 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed'

  const variants = {
    primary: 'bg-teal text-white hover:bg-navy',
    secondary: 'bg-white text-ink border border-slate-200 hover:bg-slate-50',
    ghost: 'bg-transparent text-teal hover:bg-mint-light',
    danger: 'bg-white text-coral border border-coral/30 hover:bg-coral-light',
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${fullWidth ? 'w-full' : ''} ${className}`}
    >
      {children}
    </button>
  )
}
