import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const SafetyInsights = () => {
  const navigate = useNavigate();
  const [filterPeriod, setFilterPeriod] = useState('Weekly');
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch Summary
  const fetchSummary = useCallback(async () => {
    const response = await api.get('/safety-insights/summary');
    return response.data;
  }, []);

  const { data: summaryData, loading: loadingSummary, error: summaryError, refresh: refreshSummary } = useDataSync(
    fetchSummary,
    [],
    'medium'
  );

  // Fetch Analytics
  const fetchAnalytics = useCallback(async () => {
    const response = await api.get('/safety-insights/analytics');
    return response.data;
  }, []);

  const { data: analyticsData, loading: loadingAnalytics, error: analyticsError, refresh: refreshAnalytics } = useDataSync(
    fetchAnalytics,
    [],
    'medium'
  );

  // Fetch Rankings
  const fetchRankings = useCallback(async () => {
    const response = await api.get('/safety-insights/rankings');
    return response.data.data || [];
  }, []);

  const { data: rankingsData, loading: loadingRankings, isSyncing, error: rankingsError, refresh: refreshRankings } = useDataSync(
    fetchRankings,
    [],
    'medium'
  );

  // Fetch Alerts
  const fetchAlerts = useCallback(async () => {
    const response = await api.get('/safety-insights/alerts');
    return response.data.data || [];
  }, []);

  const { data: alertsData, loading: loadingAlerts, refresh: refreshAlerts } = useDataSync(
    fetchAlerts,
    [],
    'medium'
  );

  const refreshAll = () => {
    refreshSummary();
    refreshAnalytics();
    refreshRankings();
    refreshAlerts();
  };

  const loading = loadingSummary || loadingAnalytics || loadingRankings || loadingAlerts;
  const error = summaryError || analyticsError || rankingsError;

  const summary = summaryData || {
    fleet_safety_score: 0,
    excellent_count: 0,
    good_count: 0,
    average_count: 0,
    needs_attention_count: 0
  };
  
  const analytics = analyticsData || { weekly_trends: [], monthly_trends: [], unsafe_driving_statistics: [] };
  const rankings = rankingsData || [];
  const alerts = alertsData || [];

  // Derived KPIs
  const highestDriverScore = rankings.length > 0 ? Math.max(...rankings.map(r => r.safety_score)) : 0;
  const lowestDriverScore = rankings.length > 0 ? Math.min(...rankings.map(r => r.safety_score)) : 0;
  const totalAlerts = alerts.length;

  // Search Logic
  const filteredRankings = useMemo(() => {
    const searchLower = searchTerm.toLowerCase();
    return rankings.filter(r => (r.full_name || '').toLowerCase().includes(searchLower) || (r.id || '').toLowerCase().includes(searchLower));
  }, [rankings, searchTerm]);

  // Pagination logic
  const totalItems = filteredRankings.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
  const paginatedRankings = filteredRankings.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getScoreColors = (score) => {
    const num = Number(score) || 0;
    if (num >= 90) return { bg: 'bg-secondary', text: 'text-secondary', container: 'bg-secondary-container/20' }; // Excellent (Green mapped to secondary)
    if (num >= 75) return { bg: 'bg-tertiary', text: 'text-tertiary', container: 'bg-tertiary-container/20' }; // Good (Blue mapped to tertiary)
    if (num >= 60) return { bg: 'bg-primary', text: 'text-primary', container: 'bg-primary-container/20' }; // Average (Orange mapped to primary)
    return { bg: 'bg-error', text: 'text-error', container: 'bg-error-container/20' }; // Needs Attention (Red)
  };

  const trendData = filterPeriod === 'Weekly' ? analytics.weekly_trends : analytics.monthly_trends;
  const chartLabels = trendData.map(d => d.label);
  const chartValues = trendData.map(d => d.value);

  const lineChartData = useMemo(() => ({
    labels: chartLabels,
    datasets: [
      {
        label: 'Fleet Safety Score',
        data: chartValues,
        borderColor: '#0D9488', // Secondary
        backgroundColor: 'rgba(13, 148, 136, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#0D9488',
      }
    ]
  }), [chartLabels, chartValues]);

  const doughnutData = useMemo(() => ({
    labels: ['Excellent', 'Good', 'Average', 'Needs Attention'],
    datasets: [
      {
        data: [summary.excellent_count, summary.good_count, summary.average_count, summary.needs_attention_count],
        backgroundColor: ['#0D9488', '#2563EB', '#D97706', '#E11D48'],
        borderWidth: 0,
        hoverOffset: 4
      }
    ]
  }), [summary.excellent_count, summary.good_count, summary.average_count, summary.needs_attention_count]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1E293B',
        titleFont: { size: 13, family: "'Inter', sans-serif" },
        bodyFont: { size: 13, family: "'Inter', sans-serif" },
        padding: 12,
        cornerRadius: 8,
      }
    }
  }), []);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <section className="flex-1 overflow-y-auto p-3 md:p-lg space-y-lg custom-scrollbar min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/drivers')} 
              className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-surface-container-low text-on-surface-variant transition-colors"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Safety Insights</h1>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Driver performance and risk analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-md">
            <button 
              onClick={refreshAll} 
              disabled={loading || isSyncing}
              className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50"
              title="Refresh"
            >
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
            <span className="material-symbols-outlined">error</span>
            <p className="flex-1 font-bold">{error}</p>
            <button onClick={refreshAll} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-5 gap-md w-full">
          {[
            { title: 'Fleet Safety Score', value: summary.fleet_safety_score, icon: 'shield', color: 'text-secondary', bg: 'bg-secondary-container/20' },
            { title: 'Highest Score', value: highestDriverScore, icon: 'keyboard_double_arrow_up', color: 'text-secondary', bg: 'bg-secondary-container/20' },
            { title: 'Lowest Score', value: lowestDriverScore, icon: 'keyboard_double_arrow_down', color: 'text-error', bg: 'bg-error-container/20' },
            { title: 'Avg Score', value: summary.fleet_safety_score, icon: 'trending_flat', color: 'text-tertiary', bg: 'bg-tertiary-container/20' },
            { title: 'Total Alerts', value: totalAlerts, icon: 'notifications_active', color: 'text-primary', bg: 'bg-primary-container/20' },
          ].map((kpi, idx) => (
            <div key={idx} className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm flex flex-col gap-2">
              <div className={`w-10 h-10 rounded-lg ${kpi.bg} flex items-center justify-center mb-1`}>
                <span className={`material-symbols-outlined ${kpi.color}`}>{kpi.icon}</span>
              </div>
              <div>
                <p className="text-[11px] font-bold text-outline uppercase tracking-wider">{kpi.title}</p>
                <p className="text-xl font-bold">{loading ? '...' : kpi.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Charts & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-lg">
          <div className="col-span-12 lg:col-span-8 grid grid-cols-1 md:grid-cols-2 gap-lg">
            <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col min-h-[300px]">
              <div className="flex justify-between items-center mb-md">
                <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Score Trends</h2>
                <select 
                  value={filterPeriod}
                  onChange={(e) => setFilterPeriod(e.target.value)}
                  className="bg-surface-container-low text-xs font-bold text-on-surface rounded-lg px-2 py-1 border border-outline-variant outline-none"
                >
                  <option value="Weekly">Weekly</option>
                  <option value="Monthly">Monthly</option>
                </select>
              </div>
              <div className="flex-1 relative">
                {loading ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-surface/50"><span className="material-symbols-outlined animate-spin text-primary">sync</span></div>
                ) : (
                  <Line data={lineChartData} options={{...chartOptions, scales: { y: { min: 0, max: 100, border: {display: false} }, x: { grid: { display: false }, border: {display: false} }}}} />
                )}
              </div>
            </div>
            
            <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col min-h-[300px]">
              <h2 className="font-title-sm text-title-sm font-bold text-on-surface mb-md">Score Distribution</h2>
              <div className="flex-1 relative flex items-center justify-center">
                {loading ? (
                  <div className="absolute inset-0 flex items-center justify-center bg-surface/50"><span className="material-symbols-outlined animate-spin text-primary">sync</span></div>
                ) : (
                  <div className="w-full max-w-[200px] aspect-square relative">
                    <Doughnut data={doughnutData} options={chartOptions} />
                    <div className="absolute inset-0 flex items-center justify-center flex-col pointer-events-none">
                      <span className="text-2xl font-bold text-on-surface">{summary.excellent_count}</span>
                      <span className="text-[10px] uppercase font-bold text-outline tracking-wider">Excellent</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Alerts Feed */}
          <div className="col-span-12 lg:col-span-4 bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col h-[300px] overflow-hidden">
             <h2 className="font-title-sm text-title-sm font-bold text-on-surface mb-md flex items-center gap-2">
               <span className="material-symbols-outlined text-primary">warning</span>
               Safety Alerts
             </h2>
             <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3">
                {loading ? (
                  [...Array(3)].map((_, i) => (
                    <div key={i} className="p-3 rounded-lg border border-outline-variant animate-pulse bg-surface-container-lowest">
                      <div className="h-4 bg-slate-200 rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-slate-200 rounded w-1/2"></div>
                    </div>
                  ))
                ) : alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <div key={i} className={`p-3 rounded-lg border ${alert.severity === 'Critical' ? 'bg-error-container/20 border-error/20' : 'bg-primary-container/20 border-primary/20'}`}>
                       <p className="text-sm font-bold text-on-surface mb-1">{alert.alert_type}</p>
                       <p className="text-xs text-on-surface-variant flex justify-between">
                         <span>{alert.driver_name}</span>
                         <span className="font-data-tabular">{new Date(alert.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                       </p>
                    </div>
                  ))
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-on-surface-variant">
                    <span className="material-symbols-outlined text-4xl mb-2 opacity-50">check_circle</span>
                    <p className="text-sm">No safety alerts.</p>
                  </div>
                )}
             </div>
          </div>
        </div>

        {/* Table Container */}
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0 mt-lg">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Driver Safety Rankings</h2>
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-9 pl-10 pr-4 w-full md:w-64 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none" 
                placeholder="Search drivers..." 
                type="text"
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              />
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead className="bg-surface-container-low sticky top-0 z-10">
                <tr>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Rank</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Driver Name</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-center">Safety Score</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Performance Category</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="hover:bg-surface-container-low transition-colors animate-pulse">
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-8"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                      <td className="px-md py-4 text-center"><div className="h-4 bg-slate-200 rounded w-12 mx-auto"></div></td>
                      <td className="px-md py-4"><div className="h-6 bg-slate-200 rounded-full w-24"></div></td>
                      <td className="px-md py-4 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedRankings.map((driver) => {
                  const colors = getScoreColors(driver.safety_score);
                  return (
                    <tr key={driver.id} className="hover:bg-surface-container-lowest bg-white transition-colors group">
                      <td className="px-md py-4">
                        <div className="flex items-center gap-2 font-data-tabular">
                          {driver.rank <= 3 ? (
                            <span className="material-symbols-outlined text-secondary">workspace_premium</span>
                          ) : (
                            <span className="w-6 text-center text-outline">#{driver.rank}</span>
                          )}
                        </div>
                      </td>
                      <td className="px-md py-4">
                        <p className="font-data-tabular text-data-tabular text-on-surface font-semibold">{driver.full_name}</p>
                        <p className="text-[11px] text-outline">ID: {driver.id.split('-')[0].toUpperCase()}</p>
                      </td>
                      <td className="px-md py-4">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`font-data-tabular text-data-tabular font-bold ${colors.text}`}>{driver.safety_score}</span>
                          <div className="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden">
                            <div className={`h-full ${colors.bg}`} style={{ width: `${driver.safety_score}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-md py-4">
                        <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${colors.container} ${colors.text}`}>
                          {driver.performance}
                        </span>
                      </td>
                      <td className="px-md py-4 text-right">
                        <button 
                          onClick={() => navigate('/drivers', { state: { filter: driver.full_name } })}
                          className="p-1 hover:bg-surface-container rounded text-outline hover:text-primary transition-colors"
                          title="View Driver"
                        >
                          <span className="material-symbols-outlined text-[20px]">visibility</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          
          <div className="px-md py-3 bg-surface border-t border-outline-variant flex items-center justify-between">
            <div className="flex items-center gap-2">
              <p className="text-xs text-on-surface-variant">
                Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0} to {Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems}
              </p>
              <select 
                value={itemsPerPage}
                onChange={(e) => {setItemsPerPage(Number(e.target.value)); setCurrentPage(1);}}
                className="bg-transparent border-none text-xs font-bold text-on-surface focus:ring-0 cursor-pointer outline-none ml-2"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <button onClick={() => handlePageChange('prev')} disabled={currentPage === 1} className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-outline transition-colors disabled:opacity-40">
                <span className="material-symbols-outlined text-[20px]">chevron_left</span>
              </button>
              <button className="w-8 h-8 flex items-center justify-center rounded bg-primary text-on-primary text-xs font-bold">{currentPage}</button>
              <button onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0} className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-outline transition-colors disabled:opacity-40">
                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SafetyInsights;
