import axiosClient from './axiosClient'

export const getAccounts = (includeInactive = false) =>
  axiosClient.get(`/accounts${includeInactive ? '?include_inactive=true' : ''}`)

export const createAccount = (data) => axiosClient.post('/accounts', data)

export const updateAccount = (accountId, data) => axiosClient.put(`/accounts/${accountId}`, data)

export const deleteAccount = (accountId) => axiosClient.delete(`/accounts/${accountId}`)
