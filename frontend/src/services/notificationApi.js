import api from './api';

export const getNotifications = async (params) => {
  const response = await api.get('/notifications/', { params });
  return response.data;
};

export const getUnreadNotifications = async (params) => {
  const response = await api.get('/notifications/unread', { params });
  return response.data;
};

export const searchNotifications = async (query, params) => {
  const response = await api.get(`/notifications/search`, { params: { q: query, ...params } });
  return response.data;
};

export const getNotificationStatistics = async () => {
  const response = await api.get('/notifications/statistics');
  return response.data;
};

export const getNotificationById = async (id) => {
  const response = await api.get(`/notifications/${id}`);
  return response.data;
};

export const markAsRead = async (id) => {
  const response = await api.post(`/notifications/${id}/mark-read`);
  return response.data;
};

export const markAsUnread = async (id) => {
  const response = await api.patch(`/notifications/${id}/unread`);
  return response.data;
};

export const markAllAsRead = async () => {
  const response = await api.post('/notifications/mark-all-read');
  return response.data;
};

export const archiveNotification = async (id) => {
  const response = await api.post(`/notifications/${id}/archive`);
  return response.data;
};

export const unarchiveNotification = async (id) => {
  const response = await api.post(`/notifications/${id}/unarchive`);
  return response.data;
};

export const executeNotification = async (id) => {
  const response = await api.post(`/notifications/${id}/execute`);
  return response.data;
};

export const deleteNotification = async (id) => {
  const response = await api.delete(`/notifications/${id}`);
  return response.data;
};
