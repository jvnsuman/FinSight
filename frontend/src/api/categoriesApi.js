import axiosClient from './axiosClient'

export const getCategories = () => axiosClient.get('/categories')

export const createCategory = (data) => axiosClient.post('/categories', data)

export const updateCategory = (categoryId, data) => axiosClient.put(`/categories/${categoryId}`, data)

export const deleteCategory = (categoryId) => axiosClient.delete(`/categories/${categoryId}`)
