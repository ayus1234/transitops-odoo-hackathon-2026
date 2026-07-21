import React from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { downloadCSV, downloadPDF, downloadBlobFromResponse, getFormattedDate } from '../../utils/exportUtils';

const ActivityFilters = ({ filters, setFilters, onRefresh, loading }) => {
  const { addToast } = useToast();

  const handleExport = async (format) => {
    try {
      addToast(`Exporting activities as ${format.toUpperCase()}...`, 'info');
      // Use standard browser download for binary/file data to handle headers properly
      
      const queryParams = new URLSearchParams();
      queryParams.append('limit', '10000');
      if (filters.module) queryParams.append('module', filters.module);
      if (filters.severity) queryParams.append('severity', filters.severity);
      if (filters.activity_type) queryParams.append('activity_type', filters.activity_type);
      if (filters.search) queryParams.append('search', filters.search);
      if (filters.status) queryParams.append('status', filters.status);
      if (filters.start_date) queryParams.append('start_date', filters.start_date);
      if (filters.end_date) queryParams.append('end_date', filters.end_date);
      if (filters.user_id) queryParams.append('user_id', filters.user_id);
      if (filters.vehicle_id) queryParams.append('vehicle_id', filters.vehicle_id);
      if (filters.driver_id) queryParams.append('driver_id', filters.driver_id);
      
      const response = await api.get(`/activity?${queryParams.toString()}`);
      const data = response.data.items || [];
      
      const columns = [
        { label: 'Date', key: 'created_at', format: (v) => v ? new Date(v).toLocaleString() : '' },
        { label: 'Module', key: 'module' },
        { label: 'Type', key: 'activity_type' },
        { label: 'Title', key: 'title' },
        { label: 'Severity', key: 'severity' },
        { label: 'Status', key: 'status' }
      ];

      if (format === 'csv') {
        downloadCSV(data, `activity_export_${getFormattedDate()}.csv`, columns);
      } else if (format === 'pdf') {
        downloadPDF(data, `activity_export_${getFormattedDate()}.pdf`, 'Enterprise Activity Log', columns);
      }
      
      addToast(`${format.toUpperCase()} export completed successfully.`, 'success');
    } catch (err) {
      console.error("Export error:", err);
      addToast(`Failed to export as ${format.toUpperCase()}`, 'error');
    }
  };

  const handleChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleReset = () => {
    setFilters({
      module: '',
      severity: '',
      activity_type: '',
      status: '',
      search: '',
      start_date: '',
      end_date: '',
      user_id: '',
      vehicle_id: '',
      driver_id: ''
    });
  };

  return (
    <div className="flex flex-col gap-sm mx-md">
      {/* Top Row: Search and Export */}
      <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md">
        <div className="relative flex-1 md:max-w-xl min-w-[380px]">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none">search</span>
          <input 
            type="text" 
            placeholder="Search activities by title, description, or IDs..." 
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            className="h-10 pl-10 pr-4 w-full bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]"
          />
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={onRefresh} 
            disabled={loading}
            className="p-2 rounded-lg bg-surface-container hover:bg-surface-container-high transition-all text-on-surface-variant flex items-center justify-center disabled:opacity-50 border border-outline-variant"
            title="Refresh"
          >
            <span className={`material-symbols-outlined ${loading ? 'animate-spin' : ''}`}>sync</span>
          </button>
          
          <button onClick={() => handleExport('csv')} className="bg-surface-container-low border border-outline-variant text-on-surface hover:bg-surface-container transition-colors px-3 py-2 rounded-lg font-bold text-body-sm flex items-center gap-2" title="Export CSV">
            <span className="material-symbols-outlined text-[18px]">table_chart</span>
            <span className="hidden md:inline">CSV</span>
          </button>
          
          <button onClick={() => handleExport('pdf')} className="bg-surface-container-low border border-outline-variant text-on-surface hover:bg-surface-container transition-colors px-3 py-2 rounded-lg font-bold text-body-sm flex items-center gap-2" title="Export PDF">
            <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
            <span className="hidden md:inline">PDF</span>
          </button>
        </div>
      </div>
      
      {/* Bottom Row: Filters */}
      <div className="flex flex-wrap items-center gap-sm">
        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 w-full md:w-auto flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">category</span>
          <select 
            value={filters.module || ''}
            onChange={(e) => handleChange('module', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface-variant focus:text-on-surface focus:outline-none border-none cursor-pointer w-full"
          >
            <option value="">All Modules</option>
            <option value="Authentication">Authentication</option>
            <option value="Dashboard">Dashboard</option>
            <option value="Vehicle">Vehicle Registry</option>
            <option value="Driver">Driver Management</option>
            <option value="Trip">Trip Management</option>
            <option value="Maintenance">Maintenance</option>
            <option value="Fuel">Fuel Logs</option>
            <option value="Expense">Expenses</option>
            <option value="Reports">Reports</option>
            <option value="Settings">System Settings</option>
            <option value="Notification">Notification</option>
            <option value="Inventory">Inventory</option>
            <option value="Procurement">Procurement</option>
          </select>
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 w-full md:w-auto flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">error</span>
          <select 
            value={filters.severity || ''}
            onChange={(e) => handleChange('severity', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface-variant focus:text-on-surface focus:outline-none border-none cursor-pointer w-full"
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="Warning">Warning</option>
            <option value="Info">Info</option>
            <option value="Success">Success</option>
          </select>
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 w-full md:w-auto flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">bolt</span>
          <select 
            value={filters.activity_type || ''}
            onChange={(e) => handleChange('activity_type', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface-variant focus:text-on-surface focus:outline-none border-none cursor-pointer w-full"
          >
            <option value="">All Types</option>
            <option value="Created">Created</option>
            <option value="Updated">Updated</option>
            <option value="Deleted">Deleted</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
            <option value="Completed">Completed</option>
            <option value="System">System</option>
          </select>
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 w-full md:w-auto flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">rule</span>
          <select 
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface-variant focus:text-on-surface focus:outline-none border-none cursor-pointer w-full"
          >
            <option value="">All Statuses</option>
            <option value="Success">Success</option>
            <option value="Failed">Failed</option>
            <option value="Pending">Pending</option>
          </select>
        </div>

        {/* Reset Filters */}
        <button 
          onClick={handleReset}
          className="h-10 px-3 text-body-sm font-bold text-outline hover:text-on-surface bg-transparent hover:bg-surface-container-low rounded-lg transition-colors border border-transparent"
        >
          Reset
        </button>
      </div>

      {/* Advanced Filters Row */}
      <div className="flex flex-wrap items-center gap-sm mt-1">
        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">calendar_today</span>
          <input 
            type="date"
            value={filters.start_date || ''}
            onChange={(e) => handleChange('start_date', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface focus:outline-none border-none cursor-pointer"
            title="Start Date"
          />
        </div>
        <span className="text-outline text-body-sm px-1">-</span>
        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 flex-1 md:flex-none">
          <input 
            type="date"
            value={filters.end_date || ''}
            onChange={(e) => handleChange('end_date', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface focus:outline-none border-none cursor-pointer"
            title="End Date"
          />
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">person</span>
          <input 
            type="text"
            placeholder="User ID"
            value={filters.user_id || ''}
            onChange={(e) => handleChange('user_id', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface focus:outline-none border-none w-full md:w-32"
          />
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">local_shipping</span>
          <input 
            type="text"
            placeholder="Vehicle ID"
            value={filters.vehicle_id || ''}
            onChange={(e) => handleChange('vehicle_id', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface focus:outline-none border-none w-full md:w-32"
          />
        </div>

        <div className="flex items-center gap-1 bg-surface-container-lowest px-2 py-1 rounded-lg border border-outline-variant focus-within:border-primary transition-colors h-10 flex-1 md:flex-none">
          <span className="material-symbols-outlined text-[18px] text-outline">badge</span>
          <input 
            type="text"
            placeholder="Driver ID"
            value={filters.driver_id || ''}
            onChange={(e) => handleChange('driver_id', e.target.value)}
            className="bg-transparent font-body-sm text-body-sm text-on-surface focus:outline-none border-none w-full md:w-32"
          />
        </div>
      </div>
    </div>
  );
};

export default ActivityFilters;
