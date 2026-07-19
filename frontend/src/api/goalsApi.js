import axiosClient from './axiosClient'

export const getGoals = () => axiosClient.get('/goals')

export const getGoal = (goalId) => axiosClient.get(`/goals/${goalId}`)

export const createGoal = (data) => axiosClient.post('/goals', data)

export const updateGoal = (goalId, data) => axiosClient.put(`/goals/${goalId}`, data)

export const deleteGoal = (goalId) => axiosClient.delete(`/goals/${goalId}`)

export const allocateSavings = (source, percent) =>
  axiosClient.post('/goals/allocate-savings', { source, percent })

export const coverShortfall = (withdrawals) =>
  axiosClient.post('/goals/cover-shortfall', { withdrawals })

export const fundGoal = (goalId, data) =>
  axiosClient.post(`/goals/${goalId}/fund`, data)
