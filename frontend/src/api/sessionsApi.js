import axiosClient from './axiosClient'

export const getSessions = () => axiosClient.get('/sessions')

export const revokeSession = (sessionId) => axiosClient.delete(`/sessions/${sessionId}`)

export const revokeOtherSessions = () => axiosClient.post('/sessions/revoke-others')
