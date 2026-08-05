import axiosClient from './axiosClient'

export const registerUser = (data) => axiosClient.post('/auth/register', data)

export const verifyEmail = (token) => axiosClient.get(`/auth/verify-email?token=${encodeURIComponent(token)}`)

export const resendVerification = (email) => axiosClient.post('/auth/resend-verification', { email })

export const loginUser = (email, password) => {
  // Backend expects OAuth2PasswordRequestForm - form-encoded, not JSON
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)
  return axiosClient.post('/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export const forgotPassword = (email) => axiosClient.post('/auth/forgot-password', { email })

export const resetPassword = (token, new_password) =>
  axiosClient.post('/auth/reset-password', { token, new_password })

export const getProfile = () => axiosClient.get('/auth/me')

export const updateProfile = (data) => axiosClient.put('/auth/me', data)

export const changePassword = (current_password, new_password) =>
  axiosClient.post('/auth/change-password', { current_password, new_password })

export const getSessions = () => axiosClient.get('/auth/sessions')

export const revokeSession = (sessionId) => axiosClient.delete(`/auth/sessions/${sessionId}`)

export const deactivateAccount = (current_password, reason) =>
  axiosClient.delete('/auth/me', { data: { current_password, reason: reason || undefined } })
