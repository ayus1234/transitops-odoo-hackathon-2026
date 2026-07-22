import React, { useCallback } from 'react';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';

import KpiRow from './dashboard/KpiRow';
import ChartsSection from './dashboard/ChartsSection';
import MaintenanceTable from './dashboard/MaintenanceTable';
import ActivityFeed from './dashboard/ActivityFeed';

const Dashboard = () => {
  const fetchDashboardData = useCallback(async () => {
    const [overviewRes, alertsRes] = await Promise.all([
      api.get('/dashboard/overview'),
      api.get('/dashboard/alerts')
    ]);
    return {
      ...overviewRes.data.data,
      alerts: alertsRes.data.data
    };
  }, []);

  const { data, loading, isSyncing, error, refresh, lastUpdated } = useDataSync(
    fetchDashboardData,
    [],
    'medium'
  );

  return (
    <div className="p-3 md:p-md lg:p-lg space-y-lg flex-1 min-w-0">
      {/* Dashboard Toolbar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-lg">
        <div>
          <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Operations Dashboard</h1>
          {error ? (
            <p className="font-body-md text-body-md text-error font-bold animate-pulse mt-1">{error}</p>
          ) : (
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Live fleet overview • Last updated: {lastUpdated.toLocaleTimeString()}</p>
          )}
        </div>
        <div className="flex items-center gap-md">
          <button 
            onClick={refresh}
            disabled={loading || isSyncing}
            className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50"
            title="Refresh"
          >
            <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
          </button>
        </div>
      </div>

      <KpiRow data={data} loading={loading} />
      
      {/* Main Dashboard Layout Grid */}
      <div className="grid grid-cols-12 gap-lg">
        {/* Left Column (8 cols): Charts & Table */}
        <div className="col-span-12 lg:col-span-8 flex flex-col space-y-lg min-w-0">
          <ChartsSection data={data} loading={loading} />
          <MaintenanceTable data={data} loading={loading} />
        </div>
        
        {/* Right Column (4 cols): Feed & Map */}
        <ActivityFeed loading={loading} />
      </div>
    </div>
  );
};

export default Dashboard;
