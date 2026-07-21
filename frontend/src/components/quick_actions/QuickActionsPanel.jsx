import React, { useState, useEffect, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../../contexts/ToastContext';
import { quickActionsApi } from '../../services/quickActionsApi';
import { downloadBlobFromResponse, getFormattedDate } from '../../utils/exportUtils';

import QuickActionCard from './QuickActionCard';
import QuickActionCategory from './QuickActionCategory';
import QuickActionSearch from './QuickActionSearch';

const QuickActionsPanel = ({ isOpen, onClose }) => {
  const [actions, setActions] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [recent, setRecent] = useState([]);
  const [permissions, setPermissions] = useState({ allowed: [], restricted: [] });
  const [statistics, setStatistics] = useState(null);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'favorites', 'recent', 'analytics'

  const { showToast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    let interval;
    if (isOpen) {
      fetchData();
      interval = setInterval(() => {
        quickActionsApi.getFavorites().then(res => setFavorites(res.data || [])).catch(console.error);
        quickActionsApi.getRecent().then(res => setRecent(res.data || [])).catch(console.error);
        quickActionsApi.getStatistics().then(res => setStatistics(res.data || null)).catch(console.error);
      }, 30000);
    }
    return () => clearInterval(interval);
  }, [isOpen]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [actionsRes, favRes, recentRes, permRes, statRes] = await Promise.all([
        quickActionsApi.getAllActions(),
        quickActionsApi.getFavorites(),
        quickActionsApi.getRecent(),
        quickActionsApi.getPermissions(),
        quickActionsApi.getStatistics()
      ]);
      
      setActions(actionsRes.data || []);
      setFavorites(favRes.data || []);
      setRecent(recentRes.data || []);
      setPermissions(permRes.data || { allowed: [], restricted: [] });
      setStatistics(statRes.data || null);
    } catch (error) {
      console.error('Failed to load quick actions:', error);
      showToast('Failed to load Quick Actions', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleFavorite = async (actionId, isFavorite) => {
    // Optimistic UI Update
    const updatedFavs = isFavorite 
      ? [...favorites, actions.find(a => a.id === actionId)].filter(Boolean)
      : favorites.filter(f => f.id !== actionId);
    
    setFavorites(updatedFavs);
    
    try {
      if (isFavorite) {
        await quickActionsApi.addFavorite(actionId);
      } else {
        await quickActionsApi.removeFavorite(actionId);
      }
      showToast(isFavorite ? 'Added to favorites' : 'Removed from favorites', 'success');
      // Refresh to ensure sync
      fetchData();
    } catch (error) {
      console.error('Toggle favorite failed:', error);
      showToast('Failed to update favorite', 'error');
      fetchData(); // Revert on failure
    }
  };

  const handleExecuteAction = async (actionId, route, name) => {
    // Check permissions first
    if (permissions.restricted.includes(actionId)) {
      showToast('Permission Denied', 'error');
      return; // Do not open workflow
    }

    try {
      onClose(); // Close panel immediately for better UX
      const result = await quickActionsApi.executeAction(actionId);
      
      let targetRoute = result?.data?.target_route || route;
      const lowerName = name?.toLowerCase() || '';
      
      // Override for specific requested behaviors
      if (lowerName.includes('assign driver')) {
        targetRoute = '/drivers/new';
      }
      
      if (targetRoute) {
        if (targetRoute === '/custom-reports/new') {
          navigate('/reports/builder');
        } else if (targetRoute.startsWith('/settings/')) {
          navigate('/settings', { state: { openModal: true, action: targetRoute } });
        } else if (targetRoute.endsWith('/new')) {
          const baseRoute = targetRoute.replace('/new', '');
          navigate(baseRoute, { state: { openModal: true } });
        } else {
          navigate(targetRoute);
        }
      }

      // Determine specific success toast
      let toastMsg = 'Action executed successfully';
      if (lowerName.includes('register vehicle')) toastMsg = 'Vehicle Registration Started';
      else if (lowerName.includes('create trip')) toastMsg = 'Trip Creation Started';
      else if (lowerName.includes('assign driver')) toastMsg = 'Driver Assignment Started';
      else if (lowerName.includes('run report') || lowerName.includes('generate report')) toastMsg = 'Report Builder Opened';

      showToast(toastMsg, 'success');
    } catch (error) {
      console.error('Action execution failed:', error);
      showToast(error.response?.data?.message || 'Failed to execute action', 'error');
    }
  };

  const handleExport = async (type, format) => {
    try {
      const response = await quickActionsApi.exportData(type, format);
      downloadBlobFromResponse(response, `quick_actions_${type}_${getFormattedDate()}.${format}`);
      showToast(`Exported ${type} as ${format.toUpperCase()}`, 'success');
    } catch (error) {
      console.error('Export failed:', error);
      showToast('Failed to export data', 'error');
    }
  };

  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  // Derive categories and filter by search
  const filteredActions = useMemo(() => {
    let source = actions;
    if (activeTab === 'favorites') source = favorites;
    if (activeTab === 'recent') source = recent.map(r => ({...r.action, timestamp: r.last_accessed_at}));

    if (!searchQuery) return source;

    const lowerQuery = searchQuery.toLowerCase();
    return source.filter(a => 
      a?.name?.toLowerCase().includes(lowerQuery) || 
      a?.display_name?.toLowerCase().includes(lowerQuery) ||
      a?.description?.toLowerCase().includes(lowerQuery) ||
      a?.category?.toLowerCase().includes(lowerQuery) ||
      a?.module?.toLowerCase().includes(lowerQuery)
    );
  }, [actions, favorites, recent, activeTab, searchQuery]);

  const categories = useMemo(() => {
    const groups = {};
    filteredActions.forEach(action => {
      if (!action) return;
      if (!groups[action.category]) {
        groups[action.category] = [];
      }
      groups[action.category].push(action);
    });
    return groups;
  }, [filteredActions]);

  // Icons for generic categories
  const categoryIcons = {
    'Fleet': 'local_shipping',
    'Trips': 'route',
    'Maintenance': 'build',
    'Fuel': 'local_gas_station',
    'Finance': 'payments',
    'Reports': 'bar_chart',
    'Administration': 'admin_panel_settings',
    'Support': 'support_agent'
  };

  if (!isOpen) return null;

  return createPortal(
    <>
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
        style={{ zIndex: 105 }}
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div 
        className="fixed inset-y-0 right-0 w-full sm:w-[500px] md:w-[640px] lg:w-[720px] max-w-[100vw] bg-surface shadow-2xl flex flex-col border-l border-outline-variant transition-transform"
        style={{ zIndex: 110 }}
      >
        
        {/* Header */}
        <div className="flex items-center justify-between px-lg py-md border-b border-outline-variant bg-surface-container-lowest">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <span className="material-symbols-outlined text-primary text-[28px]">bolt</span>
            <h2 className="font-headline-sm text-headline-sm font-bold text-on-surface">Quick Actions</h2>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-surface-variant text-on-surface-variant transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Search */}
        <div className="p-md border-b border-outline-variant bg-surface">
          <QuickActionSearch onSearch={setSearchQuery} />
        </div>

        {/* Tabs */}
        {!searchQuery && (
          <div className="flex w-full pt-sm border-b border-outline-variant bg-surface overflow-x-auto hide-scrollbar whitespace-nowrap min-h-[48px]">
            <button 
              className={`flex-1 flex justify-center items-center pb-sm px-2 font-bold text-label-lg transition-colors border-b-2 ${activeTab === 'all' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('all')}
            >
              All Actions
            </button>
            <button 
              className={`flex-1 flex justify-center items-center gap-1 pb-sm px-2 font-bold text-label-lg transition-colors border-b-2 ${activeTab === 'favorites' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('favorites')}
            >
              <span className="material-symbols-outlined text-[16px]">star</span>
              Favorites
            </button>
            <button 
              className={`flex-1 flex justify-center items-center gap-1 pb-sm px-2 font-bold text-label-lg transition-colors border-b-2 ${activeTab === 'recent' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('recent')}
            >
              <span className="material-symbols-outlined text-[16px]">history</span>
              Recent
            </button>
            <button 
              className={`flex-1 flex justify-center items-center gap-1 pb-sm px-2 font-bold text-label-lg transition-colors border-b-2 ${activeTab === 'analytics' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('analytics')}
            >
              <span className="material-symbols-outlined text-[16px]">monitoring</span>
              Analytics
            </button>
          </div>
        )}

        {/* Export Controls for specific tabs */}
        {!searchQuery && !isLoading && ['recent', 'favorites', 'analytics'].includes(activeTab) && (
          <div className="flex justify-end items-center gap-2 px-lg py-2 bg-surface-container-lowest border-b border-outline-variant flex-wrap">
            <span className="text-body-sm text-on-surface-variant mr-auto self-center font-bold">Export Data:</span>
            {['csv', 'json', 'pdf'].map(fmt => (
              <button 
                key={fmt}
                onClick={() => handleExport(activeTab === 'analytics' ? 'statistics' : activeTab, fmt)}
                className="px-3 py-1.5 text-label-sm font-bold border border-outline-variant rounded hover:bg-surface-variant transition-colors uppercase text-on-surface"
              >
                {fmt}
              </button>
            ))}
          </div>
        )}

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-lg bg-surface-container-lowest">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="animate-pulse flex items-start gap-4 p-4 border border-outline-variant rounded-xl">
                  <div className="w-10 h-10 bg-surface-variant rounded-full"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-surface-variant rounded w-1/3"></div>
                    <div className="h-3 bg-surface-variant rounded w-2/3"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : filteredActions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-on-surface-variant">
              <span className="material-symbols-outlined text-[64px] mb-4 opacity-50">search_off</span>
              <h3 className="font-title-lg text-title-lg font-bold mb-2">No actions found</h3>
              <p className="text-body-md max-w-[250px]">
                {searchQuery 
                  ? `No actions found.` 
                  : activeTab === 'favorites' ? `No favorite actions yet.` : activeTab === 'recent' ? `No recent actions yet.` : `No actions found.`}
              </p>
            </div>
          ) : activeTab === 'analytics' ? (
            <div className="space-y-4">
              <h3 className="font-title-md font-bold mb-4 text-on-surface">Usage Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-md bg-surface border border-outline-variant rounded-xl flex flex-col items-center justify-center text-center">
                  <span className="material-symbols-outlined text-primary text-[32px] mb-2">bolt</span>
                  <span className="text-headline-md font-bold text-on-surface">{statistics?.total_executions || 0}</span>
                  <span className="text-label-sm text-on-surface-variant">Total Executions</span>
                </div>
                <div className="p-md bg-surface border border-outline-variant rounded-xl flex flex-col items-center justify-center text-center">
                  <span className="material-symbols-outlined text-primary text-[32px] mb-2">star</span>
                  <span className="text-headline-md font-bold text-on-surface">{statistics?.active_actions || 0}</span>
                  <span className="text-label-sm text-on-surface-variant">Active Actions</span>
                </div>
              </div>
              {statistics?.most_used_action && (
                <div className="p-md bg-surface border border-outline-variant rounded-xl">
                  <h4 className="text-label-md font-bold text-on-surface-variant mb-2 uppercase tracking-wider">Most Used Action</h4>
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-success">trending_up</span>
                    <div>
                      <p className="font-bold text-on-surface">{statistics.most_used_action.name}</p>
                      <p className="text-body-sm text-on-surface-variant">{statistics.most_used_action.executions} executions</p>
                    </div>
                  </div>
                </div>
              )}
              {statistics?.least_used_action && (
                <div className="p-md bg-surface border border-outline-variant rounded-xl">
                  <h4 className="text-label-md font-bold text-on-surface-variant mb-2 uppercase tracking-wider">Least Used Action</h4>
                  <div className="flex items-center gap-3">
                    <span className="material-symbols-outlined text-error">trending_down</span>
                    <div>
                      <p className="font-bold text-on-surface">{statistics.least_used_action.name}</p>
                      <p className="text-body-sm text-on-surface-variant">{statistics.least_used_action.executions} executions</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(categories).map(([catName, acts]) => (
                <QuickActionCategory 
                  key={catName} 
                  title={catName} 
                  icon={categoryIcons[catName] || 'apps'}
                >
                  {acts.map(action => (
                    <QuickActionCard 
                      key={action.id} 
                      action={action}
                      isFavorite={favorites.some(f => f.id === action.id)}
                      isRestricted={permissions.restricted.includes(action.id)}
                      onExecute={(id, route) => handleExecuteAction(id, route, action.name)}
                      onToggleFavorite={handleToggleFavorite}
                    />
                  ))}
                </QuickActionCategory>
              ))}
            </div>
          )}
        </div>
        
      </div>
    </>,
    document.body
  );
};

export default QuickActionsPanel;
