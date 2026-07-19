import axiosClient from './axiosClient'

export const getBudgets = (month) => axiosClient.get(`/budgets${month ? `?month=${month}` : ''}`)

export const getBudget = (budgetId) => axiosClient.get(`/budgets/${budgetId}`)

export const createBudget = (data) => axiosClient.post('/budgets', data)

export const updateBudget = (budgetId, data) => axiosClient.put(`/budgets/${budgetId}`, data)

export const deleteBudget = (budgetId) => axiosClient.delete(`/budgets/${budgetId}`)
