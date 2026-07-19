import axiosClient from './axiosClient'

export const getDashboardSummary = (month) =>
  axiosClient.get(`/dashboard/summary${month ? `?month=${month}` : ''}`)
