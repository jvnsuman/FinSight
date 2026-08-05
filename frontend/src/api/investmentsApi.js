import axiosClient from './axiosClient'

export const getInvestments = (includeInactive = false, includeMarketData = false) => {
  const params = new URLSearchParams()
  if (includeInactive) params.set('include_inactive', 'true')
  if (includeMarketData) params.set('include_market_data', 'true')
  const qs = params.toString()
  return axiosClient.get(`/investments${qs ? `?${qs}` : ''}`)
}

export const getInvestment = (investmentId) => axiosClient.get(`/investments/${investmentId}`)

export const createInvestment = (data) => axiosClient.post('/investments', data)

export const updateInvestment = (investmentId, data) => axiosClient.put(`/investments/${investmentId}`, data)

export const deleteInvestment = (investmentId) => axiosClient.delete(`/investments/${investmentId}`)

export const getPortfolioSummary = () => axiosClient.get('/investments/summary/allocation')
