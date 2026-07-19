import axiosClient from './axiosClient'

export const getTransactions = (filters = {}) => {
  const params = new URLSearchParams()
  if (filters.account_id) params.append('account_id', filters.account_id)
  if (filters.category_id) params.append('category_id', filters.category_id)
  if (filters.transaction_type) params.append('transaction_type', filters.transaction_type)
  if (filters.limit) params.append('limit', filters.limit)
  if (filters.offset) params.append('offset', filters.offset)
  const qs = params.toString()
  return axiosClient.get(`/transactions${qs ? `?${qs}` : ''}`)
}

export const createTransaction = (data) => axiosClient.post('/transactions', data)

export const updateTransaction = (transactionId, data) => axiosClient.put(`/transactions/${transactionId}`, data)

export const deleteTransaction = (transactionId) => axiosClient.delete(`/transactions/${transactionId}`)
