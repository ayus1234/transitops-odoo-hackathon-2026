import api from './api';

export const driverApi = {
  getDrivers: (params) => api.get('/drivers', { params }),
  getDriver: (id) => api.get(`/drivers/${id}`),
  createDriver: (data) => api.post('/drivers', data),
  updateDriver: (id, data) => api.put(`/drivers/${id}`, data),
  deleteDriver: (id) => api.delete(`/drivers/${id}`),
  getAvailableDrivers: () => api.get('/drivers/available/list'),
  getExpiringLicenses: (days = 30) => api.get('/drivers/expiring-licenses/list', { params: { days } }),
  getDriverStatistics: () => api.get('/drivers/statistics/status'),

  // Driver 360
  getDriver360: (id) => api.get(`/drivers/${id}/360`),
  getDriverPerformance: (id) => api.get(`/drivers/${id}/performance`),
};

export default driverApi;
