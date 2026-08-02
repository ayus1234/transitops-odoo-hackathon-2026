import api from './api';

export const documentApi = {
  getDocuments: (params) => api.get('/documents', { params }),
  getDocument: (id) => api.get(`/documents/${id}`),
  createDocument: (data) => api.post('/documents', data),
  updateDocument: (id, data) => api.put(`/documents/${id}`, data),
  deleteDocument: (id) => api.delete(`/documents/${id}`),
  verifyDocument: (id, data) => api.patch(`/documents/${id}/verify`, data),
  getExpiringDocuments: (days = 30) => api.get('/documents/expiring', { params: { days } }),
  getExpiredDocuments: () => api.get('/documents/expired'),
  uploadFile: (formData) => api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

export default documentApi;
