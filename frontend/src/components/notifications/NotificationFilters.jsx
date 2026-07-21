import React from 'react';

const NotificationFilters = ({ filters, onFilterChange }) => {
  return (
    <div className="p-3 border-b border-outline-variant bg-surface flex flex-col gap-3">
      {/* Search */}
      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">
          search
        </span>
        <input
          type="text"
          placeholder="Search notifications..."
          value={filters.search || ''}
          onChange={(e) => onFilterChange({ search: e.target.value })}
          className="w-full bg-surface-container-low border border-outline-variant rounded-md py-1.5 pl-9 pr-3 text-body-sm text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
        />
      </div>
      
      {/* Filters row */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        <select
          value={filters.priority || ''}
          onChange={(e) => onFilterChange({ priority: e.target.value || null })}
          className="bg-surface-container-low border border-outline-variant rounded px-2 py-1 text-body-sm text-on-surface-variant focus:outline-none focus:border-primary shrink-0"
        >
          <option value="">All Priorities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        
        <select
          value={filters.category || ''}
          onChange={(e) => onFilterChange({ category: e.target.value || null })}
          className="bg-surface-container-low border border-outline-variant rounded px-2 py-1 text-body-sm text-on-surface-variant focus:outline-none focus:border-primary shrink-0"
        >
          <option value="">All Categories</option>
          <option value="Vehicles">Vehicles</option>
          <option value="Drivers">Drivers</option>
          <option value="Trips">Trips</option>
          <option value="Maintenance">Maintenance</option>
          <option value="Fuel">Fuel</option>
          <option value="Expenses">Expenses</option>
          <option value="Reports">Reports</option>
          <option value="Settings">Settings</option>
          <option value="Quick Actions">Quick Actions</option>
          <option value="Dashboard">Dashboard</option>
          <option value="System">System</option>
        </select>
        
        <select
          value={filters.type || ''}
          onChange={(e) => onFilterChange({ type: e.target.value || null })}
          className="bg-surface-container-low border border-outline-variant rounded px-2 py-1 text-body-sm text-on-surface-variant focus:outline-none focus:border-primary shrink-0"
        >
          <option value="">All Types</option>
          <option value="Info">Info</option>
          <option value="Success">Success</option>
          <option value="Warning">Warning</option>
          <option value="Critical">Critical</option>
        </select>
      </div>
    </div>
  );
};

export default NotificationFilters;
