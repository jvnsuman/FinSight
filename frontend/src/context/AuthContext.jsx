import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { getProfile } from '../api/authApi'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadProfile = useCallback(async () => {
    const token = localStorage.getItem('finsight_token')
    if (!token) {
      setLoading(false)
      return
    }
    try {
      const res = await getProfile()
      setUser(res.data)
    } catch {
      localStorage.removeItem('finsight_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadProfile()
  }, [loadProfile])

  const login = (token, userData) => {
    localStorage.setItem('finsight_token', token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('finsight_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, logout, refreshProfile: loadProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
