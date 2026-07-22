import React from 'react';

const ActivityDetailsModal = ({ isOpen, onClose, activity }) => {
  if (!isOpen || !activity) return null;

  const renderMetadata = (details) => {
    if (!details) return <p className="text-body-sm text-outline italic">No additional metadata available.</p>;
    
    return (
      <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-sm overflow-x-auto">
        <pre className="text-[12px] font-data-tabular text-on-surface-variant m-0">
          {JSON.stringify(details, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100]" onClick={onClose}></div>
      <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface rounded-xl shadow-xl z-[110] flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-200" style={{ width: '100%', maxWidth: '672px' }}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-md border-b border-outline-variant">
          <h2 className="font-title-md text-title-md font-bold text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">feed</span>
            Activity Details
          </h2>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-surface-container-high transition-colors text-on-surface-variant hover:text-on-surface">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-md overflow-y-auto flex-1 space-y-md">
          {/* Main Info */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-md">
            <div className="flex items-center gap-2 mb-3">
              <span className="bg-primary-container/20 text-primary px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider border border-primary/20">
                {activity.module}
              </span>
              <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider border ${
                activity.severity === 'Critical' ? 'bg-error/10 text-error border-error/20' : 
                activity.severity === 'Warning' ? 'bg-tertiary-container/30 text-tertiary border-tertiary/20' :
                'bg-surface-container text-on-surface-variant border-outline-variant'
              }`}>
                {activity.severity}
              </span>
              {activity.status && (
                <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider border ${
                  activity.status === 'Success' ? 'bg-primary-container/20 text-primary border-primary/20' :
                  activity.status === 'Failed' ? 'bg-error/10 text-error border-error/20' :
                  'bg-surface-container text-on-surface-variant border-outline-variant'
                }`}>
                {activity.status}
              </span>
              )}
            </div>
            
            <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface mb-2">{activity.title}</h3>
            <p className="text-body-md text-on-surface-variant">{activity.description}</p>
          </div>

          {/* Context Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="space-y-1">
              <p className="text-[11px] uppercase tracking-wider font-bold text-outline">Timestamp</p>
              <p className="text-body-sm font-medium text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">calendar_today</span>
                {new Date(activity.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true })}
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-[11px] uppercase tracking-wider font-bold text-outline">Activity Type</p>
              <p className="text-body-sm font-medium text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">label</span>
                {activity.activity_type}
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-[11px] uppercase tracking-wider font-bold text-outline">User</p>
              <p className="text-body-sm font-medium text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-[16px]">person</span>
                {activity.user ? `${activity.user.first_name} ${activity.user.last_name}` : 'System'}
              </p>
            </div>
            
            {(activity.ip_address || activity.user_agent) && (
              <div className="space-y-1">
                <p className="text-[11px] uppercase tracking-wider font-bold text-outline">Network</p>
                <p className="text-body-sm font-medium text-on-surface flex items-center gap-2" title={activity.user_agent}>
                  <span className="material-symbols-outlined text-[16px]">language</span>
                  {activity.ip_address || 'Unknown IP'}
                </p>
              </div>
            )}
          </div>
          
          {/* Related Entities (if any) */}
          {(activity.vehicle_id || activity.driver_id || activity.trip_id) && (
            <div>
              <p className="text-[11px] uppercase tracking-wider font-bold text-outline mb-2">Related Entities</p>
              <div className="flex flex-wrap gap-2">
                {activity.vehicle_id && (
                  <span className="bg-surface-container px-2 py-1 rounded text-[12px] text-on-surface flex items-center gap-1 font-data-tabular">
                    <span className="material-symbols-outlined text-[14px]">local_shipping</span>
                    {activity.vehicle_id}
                  </span>
                )}
                {activity.driver_id && (
                  <span className="bg-surface-container px-2 py-1 rounded text-[12px] text-on-surface flex items-center gap-1 font-data-tabular">
                    <span className="material-symbols-outlined text-[14px]">badge</span>
                    {activity.driver_id}
                  </span>
                )}
                {activity.trip_id && (
                  <span className="bg-surface-container px-2 py-1 rounded text-[12px] text-on-surface flex items-center gap-1 font-data-tabular">
                    <span className="material-symbols-outlined text-[14px]">route</span>
                    {activity.trip_id}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Metadata Block */}
          <div>
            <p className="text-[11px] uppercase tracking-wider font-bold text-outline mb-2">Technical Details & Metadata</p>
            {renderMetadata(activity.metadata)}
          </div>
        </div>

        {/* Footer */}
        <div className="p-md border-t border-outline-variant bg-surface-container-lowest flex justify-end">
          <button 
            onClick={onClose}
            className="px-4 py-2 border border-outline-variant text-on-surface font-bold text-body-sm rounded-lg hover:bg-surface-container transition-colors"
          >
            Close Details
          </button>
        </div>
      </div>
    </>
  );
};

export default ActivityDetailsModal;
