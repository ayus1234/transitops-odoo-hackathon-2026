import React from 'react';

const ActivityTimeline = ({ activities, loading, onActivityClick }) => {

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'Critical': return { icon: 'report', color: 'text-on-error-container', bg: 'bg-error-container' };
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

  const groupActivities = (acts) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const groups = {
      'Today': [],
      'Yesterday': [],
      'Last 7 Days': [],
      'Last 30 Days': [],
      'Older': []
    };

    acts.forEach(act => {
      const d = new Date(act.created_at);
      const actDate = new Date(d);
      actDate.setHours(0, 0, 0, 0);
      
      const diffTime = today - actDate;
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) groups['Today'].push(act);
      else if (diffDays === 1) groups['Yesterday'].push(act);
      else if (diffDays <= 7) groups['Last 7 Days'].push(act);
      else if (diffDays <= 30) groups['Last 30 Days'].push(act);
      else groups['Older'].push(act);
    });

    return Object.entries(groups).filter(([_, groupActs]) => groupActs.length > 0);
  };

  return (
    <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col mx-1 md:mx-md mb-md min-w-0">
      <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
        <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Activity Timeline</h2>
      </div>
      
      <div className="flex-1 p-lg overflow-y-auto min-h-[400px]">
        {loading ? (
          <div className="space-y-md">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex gap-md relative pb-md animate-pulse">
                <div className="absolute left-4 top-8 bottom-0 w-[1px] bg-outline-variant/30"></div>
                <div className="w-8 h-8 rounded-full bg-slate-200 z-10 shrink-0"></div>
                <div className="space-y-2 flex-1">
                  <div className="h-4 bg-slate-200 rounded w-1/3"></div>
                  <div className="h-3 bg-slate-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        ) : activities.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-on-surface-variant p-8">
            <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">history</span>
            <p>No activities found matching your criteria.</p>
          </div>
        ) : (
          <div className="space-y-xl">
            {groupActivities(activities).map(([groupName, groupActs]) => (
              <div key={groupName} className="space-y-0 relative">
                <h3 className="font-title-sm text-outline font-bold uppercase tracking-wider mb-md sticky top-0 bg-surface-container-low/95 backdrop-blur z-20 py-2 -mx-md px-md border-y border-outline-variant/30">
                  {groupName}
                </h3>
                {groupActs.map((activity, index) => {
                  const severityStyle = getSeverityIcon(activity.severity);
                  const moduleIcon = getModuleIcon(activity.module);
                  
                  return (
                    <div key={activity.id} className="flex gap-md relative pb-lg last:pb-2 group">
                      {/* Timeline connecting line */}
                      {index !== groupActs.length - 1 && (
                        <div className="absolute left-5 top-10 bottom-0 w-[2px] bg-outline-variant/50 group-hover:bg-primary/30 transition-colors"></div>
                      )}
                      
                      {/* Icon Indicator */}
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center z-10 shrink-0 ${severityStyle.bg} shadow-sm border border-white relative mt-1`}>
                        <span className={`material-symbols-outlined text-[20px] ${severityStyle.color}`}>{severityStyle.icon}</span>
                      </div>
                      
                      {/* Content Card */}
                      <div 
                        className="flex-1 bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm hover:shadow transition-shadow cursor-pointer hover:border-primary/50"
                        onClick={() => onActivityClick(activity)}
                      >
                        <div className="flex flex-col md:flex-row justify-between items-start gap-2 mb-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="bg-surface-container-highest px-2 py-0.5 rounded text-[10px] font-bold text-on-surface uppercase tracking-wider flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">{moduleIcon}</span>
                              {activity.module}
                            </span>
                            {activity.status === 'Failed' && (
                              <span className="bg-error/10 text-error px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
                                Failed
                              </span>
                            )}
                            <h3 className="font-body-md font-bold text-on-surface">{activity.title}</h3>
                          </div>
                          <div className="text-[12px] text-on-surface-variant whitespace-nowrap flex items-center gap-1 font-medium bg-surface-container px-2 py-1 rounded">
                            <span className="material-symbols-outlined text-[14px]">schedule</span>
                            {new Date(activity.created_at).toLocaleString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })}
                          </div>
                        </div>
                        
                        <p className="text-body-sm text-on-surface-variant line-clamp-2 leading-relaxed">
                          {activity.description}
                        </p>
                        
                        {/* Footer / Context */}
                        <div className="mt-3 flex flex-wrap items-center gap-4 text-[12px] text-outline">
                          {activity.user && (
                            <div className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">person</span>
                              <span>{activity.user.first_name} {activity.user.last_name}</span>
                            </div>
                          )}
                          {activity.vehicle_id && (
                            <div className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">local_shipping</span>
                              <span>Vehicle {activity.vehicle_id.substring(0,8)}</span>
                            </div>
                          )}
                          {activity.driver_id && (
                            <div className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">badge</span>
                              <span>Driver {activity.driver_id.substring(0,8)}</span>
                            </div>
                          )}
                          {activity.trip_id && (
                            <div className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">route</span>
                              <span>Trip {activity.trip_id.substring(0,8)}</span>
                            </div>
                          )}
                          {activity.ip_address && (
                            <div className="flex items-center gap-1">
                              <span className="material-symbols-outlined text-[14px]">language</span>
                              <span>{activity.ip_address}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityTimeline;
