import Sidebar from './Sidebar'

export default function AppShell({ children }) {
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 px-8 py-8 max-w-[1400px]">{children}</main>
    </div>
  )
}
