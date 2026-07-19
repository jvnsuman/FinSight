import axiosClient from './axiosClient'

export const getWallet = () => axiosClient.get('/trading/wallet')

export const depositFunds = (amount) => axiosClient.post('/trading/deposit', { amount })

export const buyHolding = (data) => axiosClient.post('/trading/buy', data)

export const sellHolding = (data) => axiosClient.post('/trading/sell', data)

export const getTradeHistory = () => axiosClient.get('/trading/history')
