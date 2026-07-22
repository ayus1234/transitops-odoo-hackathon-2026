import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { FleetMapModal } from '../fleet_map/FleetMapWrappers';
import FleetMapView from '../fleet_map/FleetMapView';
import { quickActionsApi } from '../../services/quickActionsApi';
import { useEffect } from 'react';

const ActivityFeed = ({ loading }) => {
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const fetchRecentActivities = useCallback(async () => {
    const response = await api.get('/activity/recent');
    return response.data;
  }, []);

  const { data: activitiesData, loading: fetchingActivities, error: fetchError, refresh: retryFetch } = useDataSync(
    fetchRecentActivities,
    [],
    'high'
  );

  const activities = activitiesData || [];
  
  const [isMapModalOpen, setIsMapModalOpen] = useState(false);
  const [permissions, setPermissions] = useState({ allowed: [], restricted: [] });
  const [actionsList, setActionsList] = useState([]);

  useEffect(() => {
    quickActionsApi.getPermissions().then(res => setPermissions(res.data)).catch(console.error);
    quickActionsApi.getAllActions().then(res => setActionsList(res.data)).catch(console.error);
  }, []);

  const handleDashboardAction = async (name, route) => {
    const action = actionsList.find(a => a.name.toLowerCase() === name.toLowerCase() || a.display_name.toLowerCase() === name.toLowerCase());
    if (!action) {
      addToast('Please wait, actions are loading...', 'error');
      return;
    }
    if (permissions.restricted.includes(action.id)) {
      addToast('Permission Denied', 'error');
      return;
    }
    
    try {
      const result = await quickActionsApi.executeAction(action.id);
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

      let toastMsg = 'Action executed successfully';
      if (lowerName.includes('register vehicle')) toastMsg = 'Vehicle Registration Started';
      else if (lowerName.includes('create trip')) toastMsg = 'Trip Creation Started';
      else if (lowerName.includes('assign driver')) toastMsg = 'Driver Assignment Started';
      else if (lowerName.includes('run report') || lowerName.includes('generate report')) toastMsg = 'Report Builder Opened';

      addToast(toastMsg, 'success');
    } catch (error) {
      console.error('Action execution failed:', error);
      addToast(error.response?.data?.message || 'Failed to execute action', 'error');
    }
  };

  const handleOpenMap = () => {
    if (window.innerWidth >= 1024) {
      setIsMapModalOpen(true);
    } else {
      navigate('/fleet-map/full');
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'Critical': return { icon: 'report_problem', color: 'text-on-error-container', bg: 'bg-error-container' };
      case 'Warning': return { icon: 'warning', color: 'text-on-tertiary-container', bg: 'bg-tertiary-container' };
      case 'Success': return { icon: 'check_circle', color: 'text-on-primary-container', bg: 'bg-primary-container' };
      case 'Info': 
      default: return { icon: 'info', color: 'text-on-secondary-container', bg: 'bg-secondary-container' };
    }
  };

  const getModuleIcon = (module) => {
    switch (module) {
      case 'Authentication': return 'login';
      case 'Dashboard': return 'dashboard';
      case 'Vehicle': return 'local_shipping';
      case 'Driver': return 'person_pin';
      case 'Trip': return 'route';
      case 'Maintenance': return 'build';
      case 'Fuel': return 'local_gas_station';
      case 'Expense': return 'payments';
      case 'Reports': return 'bar_chart';
      case 'Custom Reports': return 'query_stats';
      case 'Notification': return 'notifications';
      case 'Help Center': return 'support_agent';
      case 'Quick Actions': return 'bolt';
      case 'Settings': return 'settings';
      default: return 'widgets';
    }
  };

  const getTimeAgo = (dateString) => {
    const now = new Date();
    const past = new Date(dateString);
    const diffMs = now - past;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  };

  if (loading) {
    return (
      <div className="col-span-12 lg:col-span-4 space-y-lg animate-pulse">
        <div className="bg-surface border border-outline-variant rounded-xl p-lg h-[150px]"></div>
        <div className="bg-surface border border-outline-variant rounded-xl h-[400px]"></div>
        <div className="bg-surface border border-outline-variant rounded-xl h-[250px]"></div>
      </div>
    );
  }

  // The backend might return recent alerts. If not, use HTML exact mock to retain the visual requirement.
  return (
    <div className="col-span-12 lg:col-span-4 space-y-lg">
      {/* Quick Actions */}
      <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
        <h2 className="font-title-sm text-title-sm text-on-surface mb-md">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-sm">
          <button onClick={() => handleDashboardAction('Register Vehicle', '/vehicles/new')} className="flex flex-col items-center justify-center gap-sm p-md rounded-xl bg-surface-container-low hover:bg-primary-container/10 border border-outline-variant transition-all hover:border-primary group">
            <span className="material-symbols-outlined text-primary p-2 bg-white rounded-full shadow-sm group-hover:scale-110 transition-transform">local_shipping</span>
            <span className="font-body-sm font-bold text-on-surface">Register Vehicle</span>
          </button>
          <button onClick={() => handleDashboardAction('Create Trip', '/trips/new')} className="flex flex-col items-center justify-center gap-sm p-md rounded-xl bg-surface-container-low hover:bg-primary-container/10 border border-outline-variant transition-all hover:border-primary group">
            <span className="material-symbols-outlined text-primary p-2 bg-white rounded-full shadow-sm group-hover:scale-110 transition-transform">add_road</span>
            <span className="font-body-sm font-bold text-on-surface">Create Trip</span>
          </button>
          <button onClick={() => handleDashboardAction('Assign Driver', '/drivers')} className="flex flex-col items-center justify-center gap-sm p-md rounded-xl bg-surface-container-low hover:bg-primary-container/10 border border-outline-variant transition-all hover:border-primary group">
            <span className="material-symbols-outlined text-primary p-2 bg-white rounded-full shadow-sm group-hover:scale-110 transition-transform">assignment_ind</span>
            <span className="font-body-sm font-bold text-on-surface">Assign Driver</span>
          </button>
          <button onClick={() => handleDashboardAction('Generate Report', '/custom-reports/new')} className="flex flex-col items-center justify-center gap-sm p-md rounded-xl bg-surface-container-low hover:bg-primary-container/10 border border-outline-variant transition-all hover:border-primary group">
            <span className="material-symbols-outlined text-primary p-2 bg-white rounded-full shadow-sm group-hover:scale-110 transition-transform">description</span>
            <span className="font-body-sm font-bold text-on-surface">Run Report</span>
          </button>
        </div>
      </section>

      {/* Recent Activity Feed */}
      <section className="bg-surface border border-outline-variant rounded-xl flex flex-col shadow-sm max-h-[400px]">
        <div className="px-lg py-md border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center shrink-0">
          <h2 className="font-title-sm text-title-sm text-on-surface">Recent Activity</h2>
          <span className="bg-primary-fixed text-on-primary-fixed px-2 py-0.5 rounded text-[11px] font-bold">LIVE</span>
        </div>
        <div className="p-lg overflow-y-auto scroll-hide space-y-md">
          {fetchingActivities && activities.length === 0 ? (
            // Skeleton Loader
            [...Array(4)].map((_, i) => (
              <div key={i} className="flex gap-md relative pb-md animate-pulse">
                <div className="absolute left-4 top-8 bottom-0 w-[1px] bg-outline-variant/30"></div>
                <div className="w-8 h-8 rounded-full bg-slate-200 z-10 shrink-0"></div>
                <div className="space-y-2 flex-1 pt-1">
                  <div className="h-4 bg-slate-200 rounded w-3/4"></div>
                  <div className="h-3 bg-slate-200 rounded w-1/4"></div>
                </div>
              </div>
            ))
          ) : fetchError ? (
            // Error State
            <div className="flex flex-col items-center justify-center h-32 text-on-surface-variant">
              <span className="material-symbols-outlined text-[32px] mb-2 opacity-50">error</span>
              <p className="text-body-sm font-medium">Unable to load recent activity.</p>
              <button 
                onClick={retryFetch}
                className="mt-2 px-3 py-1 bg-surface-container border border-outline-variant rounded-lg text-body-sm hover:bg-surface-container-high transition-colors"
              >
                Retry
              </button>
            </div>
          ) : activities.length === 0 ? (
            // Empty State
            <div className="flex flex-col items-center justify-center h-32 text-on-surface-variant">
              <span className="material-symbols-outlined text-[32px] mb-2 opacity-50">history</span>
              <p className="text-body-sm font-medium">No recent activity available.</p>
            </div>
          ) : (
            // Data State
            activities.map((activity, index) => {
              const severityStyle = getSeverityIcon(activity.severity);
              const moduleIcon = getModuleIcon(activity.module);
              
              return (
                <div key={activity.id} className="flex gap-md relative pb-md last:pb-0 group">
                  {/* Timeline connector */}
                  {index !== activities.length - 1 && (
                    <div className="absolute left-4 top-8 bottom-0 w-[1px] bg-outline-variant/30 group-hover:bg-primary/30 transition-colors"></div>
                  )}
                  
                  {/* Icon */}
                  <div className={`w-8 h-8 rounded-full ${severityStyle.bg} flex items-center justify-center z-10 shrink-0 border border-white relative`} title={`${activity.severity} - ${activity.module}`}>
                    <span className={`material-symbols-outlined ${severityStyle.color} text-[16px]`}>{moduleIcon}</span>
                  </div>
                  
                  {/* Content */}
                  <div className="space-y-1 w-full">
                    <p className="font-body-sm text-on-surface line-clamp-2">
                      <span className="font-bold mr-1">{activity.title}</span>
                      <span className="text-on-surface-variant">{activity.description}</span>
                    </p>
                    <div className="flex items-center gap-2">
                      <p className="text-[11px] text-on-surface-variant font-medium bg-surface-container px-1.5 py-0.5 rounded">
                        {getTimeAgo(activity.created_at)}
                      </p>
                      {activity.status === 'Failed' && (
                        <span className="text-[10px] bg-error/10 text-error px-1.5 py-0.5 rounded font-bold uppercase">
                          Failed
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
        <button 
          onClick={() => navigate('/activity')}
          className="p-md text-center text-primary font-body-sm font-bold border-t border-outline-variant hover:bg-surface-container-low transition-colors w-full"
        >
          View All Activity
        </button>
      </section>

      {/* Real-time Map Teaser */}
      <section className="h-64 md:h-[350px]">
        <FleetMapView isWidget={true} onExpand={handleOpenMap} />
      </section>

      {isMapModalOpen && <FleetMapModal onClose={() => setIsMapModalOpen(false)} />}
    </div>
  );
};

export default ActivityFeed;
