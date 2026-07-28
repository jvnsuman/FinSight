import axiosClient from './axiosClient'

export const getNotifications = (unreadOnly = false, limit = 50) =>
  axiosClient.get('/notifications', { params: { unread_only: unreadOnly, limit } })

export const getUnreadCount = () => axiosClient.get('/notifications/unread-count')

export const markNotificationRead = (notificationId) =>
  axiosClient.patch(`/notifications/${notificationId}/read`)

export const markAllNotificationsRead = () => axiosClient.patch('/notifications/read-all')
