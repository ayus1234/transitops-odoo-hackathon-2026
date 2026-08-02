import api from './api';

export const vehicleApi = {
  // Vehicle CRUD
  getVehicles: (params) => api.get('/vehicles', { params }),
  getVehicle: (id) => api.get(`/vehicles/${id}`),
  createVehicle: (data) => api.post('/vehicles', data),
  updateVehicle: (id, data) => api.put(`/vehicles/${id}`, data),
  deleteVehicle: (id) => api.delete(`/vehicles/${id}`),
  getAvailableVehicles: () => api.get('/vehicles/available/list'),
  getVehicleStatistics: () => api.get('/vehicles/statistics/status'),

  // Vehicle 360 & Lifecycle
  getVehicle360: (id) => api.get(`/vehicles/${id}/360`),
  updateVehicleStatus: (id, data) => api.patch(`/vehicles/${id}/status`, data),
  getVehicleTCO: (id) => api.get(`/vehicles/${id}/tco`),

  // Odometer History
  recordOdometer: (id, data) => api.post(`/vehicles/${id}/odometer`, data),
  getOdometerHistory: (id, params) => api.get(`/vehicles/${id}/odometer`, { params }),
  getOdometerStats: (id) => api.get(`/vehicles/${id}/odometer/stats`),
};

export default vehicleApi;
