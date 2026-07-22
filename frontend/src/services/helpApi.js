import api from './api';

export const helpApi = {
  // Categories
  getCategories: (params) => api.get('/help/categories', { params }),
  createCategory: (data) => api.post('/help/categories', data),
  
  // Articles
  getArticles: (params) => api.get('/help/articles', { params }),
  getPopularArticles: (params) => api.get('/help/articles/popular', { params }),
  searchArticles: (params) => api.get('/help/search', { params }),
  getArticle: (id) => api.get(`/help/articles/${id}`),
  getArticleBySlug: (slug) => api.get(`/help/articles/slug/${slug}`),
  createArticle: (data) => api.post('/help/articles', data),
  
  // Tickets
  getTickets: (params) => api.get('/help/tickets', { params }),
  getTicket: (id) => api.get(`/help/tickets/${id}`),
  createTicket: (data) => api.post('/help/tickets', data),
  updateTicket: (id, data) => api.put(`/help/tickets/${id}`, data),
  assignTicket: (id, assignToId) => api.post(`/help/tickets/${id}/assign`, null, { params: { assign_to_id: assignToId } }),
  resolveTicket: (id, resolutionNotes) => api.post(`/help/tickets/${id}/resolve`, null, { params: { resolution_notes: resolutionNotes } }),
  closeTicket: (id) => api.post(`/help/tickets/${id}/close`),
  searchTickets: (params) => api.get('/help/tickets/search', { params }),
  filterTickets: (params) => api.get('/help/tickets/filter', { params }),
  uploadAttachment: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/help/tickets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Feedback
  submitFeedback: (data) => api.post('/help/feedback', data),
  
  // Stats
  getStatistics: () => api.get('/help/statistics'),
};
