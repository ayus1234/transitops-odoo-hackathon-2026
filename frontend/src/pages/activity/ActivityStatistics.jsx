import React from 'react';

const ActivityStatistics = ({ stats }) => {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-md mx-md">
      {/* Total Activities */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] lg:col-span-2">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-label-caps text-outline font-bold">TOTAL ACTIVITIES</p>
          <span className="material-symbols-outlined text-primary">history</span>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{stats.total_activities.toLocaleString()}</h2>
        <p className="text-body-sm text-secondary font-medium mt-xs">All Time Logs</p>
      </div>

      {/* Critical Activities */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-label-caps text-outline font-bold">CRITICAL</p>
          <div className="w-2 h-2 rounded-full bg-error"></div>
        </div>
        <h2 className="text-display-md font-display-md text-on-surface">
          {stats.activities_by_severity.Critical || 0}
        </h2>
        <p className="text-body-sm text-error font-medium mt-xs">Immediate Action</p>
      </div>

      {/* Warning Activities */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-label-caps text-outline font-bold">WARNING</p>
          <div className="w-2 h-2 rounded-full bg-tertiary"></div>
        </div>
        <h2 className="text-display-md font-display-md text-on-surface">
          {stats.activities_by_severity.Warning || 0}
        </h2>
        <p className="text-body-sm text-tertiary font-medium mt-xs">Attention Needed</p>
      </div>
      
      {/* Success Activities */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-label-caps text-outline font-bold">SUCCESS</p>
          <div className="w-2 h-2 rounded-full bg-primary"></div>
        </div>
        <h2 className="text-display-md font-display-md text-on-surface">
          {stats.activities_by_severity.Success || 0}
        </h2>
        <p className="text-body-sm text-primary font-medium mt-xs">Completed OK</p>
      </div>
      
      {/* Info Activities */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-label-caps text-outline font-bold">INFO</p>
          <div className="w-2 h-2 rounded-full bg-secondary"></div>
        </div>
        <h2 className="text-display-md font-display-md text-on-surface">
          {stats.activities_by_severity.Info || 0}
        </h2>
        <p className="text-body-sm text-secondary font-medium mt-xs">General Logs</p>
      </div>
    </div>
  );
};

export default ActivityStatistics;
