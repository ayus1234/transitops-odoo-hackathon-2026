import api from './api';

export const quickActionsApi = {
  /**
   * Fetch all available quick actions for the current user.
   */
  getAllActions: async () => {
    const response = await api.get('/quick-actions');
    return response.data;
  },

  /**
   * Search quick actions by keyword or category.
   * @param {string} keyword 
   * @param {string} category 
   */
  searchActions: async (keyword = '', category = '') => {
    const params = new URLSearchParams();
    if (keyword) params.append('keyword', keyword);
    if (category) params.append('category', category);
    const response = await api.get(`/quick-actions/search?${params.toString()}`);
    return response.data;
  },

  /**
   * Fetch user's favorite quick actions.
   */
  getFavorites: async () => {
    const response = await api.get('/quick-actions/favorites');
    return response.data;
  },

  /**
   * Fetch user's recent quick actions.
   * @param {number} limit 
   */
  getRecent: async (limit = 5) => {
    const response = await api.get(`/quick-actions/recent?limit=${limit}`);
    return response.data;
  },

  /**
   * Fetch quick action statistics.
   */
  getStatistics: async () => {
    const response = await api.get('/quick-actions/statistics');
    return response.data;
  },

  /**
   * Add a quick action to favorites.
   * @param {string} actionId 
   */
  addFavorite: async (actionId) => {
    const response = await api.post(`/quick-actions/favorites/add`, {
      action_id: actionId,
    });
    return response.data;
  },

  /**
   * Remove a quick action from favorites.
   * @param {string} actionId 
   */
  removeFavorite: async (actionId) => {
    const response = await api.post(`/quick-actions/favorites/remove`, {
      action_id: actionId,
    });
    return response.data;
  },

  /**
   * Get user permissions for quick actions.
   */
  getPermissions: async () => {
    const response = await api.get('/quick-actions/permissions');
    return response.data;
  },

  /**
   * Export quick actions data.
   * @param {string} type 
   * @param {string} format 
   */
  exportData: async (type, format) => {
    const response = await api.get(`/quick-actions/export/${type}?format=${format}`, {
      responseType: 'blob'
    });
    return response;
  },

  /**
   * Execute a quick action to log history and get routing metadata.
   * @param {string} actionId 
   */
  executeAction: async (actionId) => {
    const response = await api.post(`/quick-actions/${actionId}/execute`);
    return response.data;
  }
};
