import api from './api';

export const dispatchApi = {
  getDispatchBoard: async () => {
    const response = await api.get('/dispatch/board');
    return response.data;
  },

  validateDispatch: async (data) => {
    const response = await api.post('/dispatch/validate', data);
    return response.data;
  },

  assignAndDispatch: async (data) => {
    const response = await api.post('/dispatch/assign-and-dispatch', data);
    return response.data;
  },

  getRecommendations: async (jobId) => {
    const response = await api.get(`/dispatch/recommendations/${jobId}`);
    return response.data;
  }
};
