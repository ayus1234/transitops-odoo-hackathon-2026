import api from './api';

export const vendorApi = {
  getVendors: (params) => api.get('/vendors', { params }),
  getVendor: (id) => api.get(`/vendors/${id}`),
  createVendor: (data) => api.post('/vendors', data),
  updateVendor: (id, data) => api.put(`/vendors/${id}`, data),
  deleteVendor: (id) => api.delete(`/vendors/${id}`),
  getVendorScorecard: (id) => api.get(`/vendors/${id}/scorecard`),
};

export default vendorApi;
