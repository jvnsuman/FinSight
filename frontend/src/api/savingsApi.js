import axiosClient from './axiosClient'

export const getSavingsBreakdown = () => axiosClient.get('/savings/breakdown')
