import React, { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { downloadBlobFromResponse, getFormattedDate } from '../../utils/exportUtils';
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
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const FleetCompliance = () => {
  const navigate = useNavigate();
  const [filterPeriod, setFilterPeriod] = useState('Weekly');
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchSummary = useCallback(async () => {
    const response = await api.get('/fleet-compliance/summary');
    return response.data;
  }, []);

  const { data: summaryData, loading: loadingSummary, error: summaryError, refresh: refreshSummary } = useDataSync(
    fetchSummary,
    [],
    'medium'
  );

  const fetchAnalytics = useCallback(async () => {
    const response = await api.get('/fleet-compliance/analytics');
    return response.data;
  }, []);

  const { data: analyticsData, loading: loadingAnalytics, error: analyticsError, refresh: refreshAnalytics } = useDataSync(
    fetchAnalytics,
    [],
    'medium'
  );

  const fetchList = useCallback(async () => {
    const response = await api.get('/fleet-compliance');
    return response.data.data || [];
  }, []);

  const { data: listData, loading: loadingList, isSyncing, error: listError, refresh: refreshList } = useDataSync(
    fetchList,
    [],
    'medium'
  );

  const refreshAll = () => {
    refreshSummary();
    refreshAnalytics();
    refreshList();
  };

  const loading = loadingSummary || loadingAnalytics || loadingList;
  const error = summaryError || analyticsError || listError;

  const summary = summaryData || {
    fleet_compliance_score: 0,
    driver_compliance_score: 0,
    vehicle_compliance_score: 0,
    maintenance_compliance_score: 0,
    inspection_compliance_score: 0
  };
  
  const analytics = analyticsData || { weekly_trends: [], monthly_trends: [] };
  const categories = listData || [];

  // Pagination logic
  const totalItems = categories.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
  const paginatedCategories = categories.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/fleet-compliance/export/csv', { responseType: 'blob' });
      downloadBlobFromResponse(response, `fleet_compliance_report_${getFormattedDate()}.csv`);
    } catch (err) {
      console.error(err);
      alert("Failed to export CSV.");
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await api.get('/fleet-compliance/export/pdf', { responseType: 'blob' });
      downloadBlobFromResponse(response, `fleet_compliance_report_${getFormattedDate()}.pdf`);
    } catch (err) {
      console.error(err);
      alert("Failed to export PDF.");
    }
  };

  const trendData = filterPeriod === 'Weekly' ? analytics.weekly_trends : analytics.monthly_trends;
  const chartLabels = trendData.map(d => d.label);
  const chartValues = trendData.map(d => d.value);

  const lineChartData = useMemo(() => ({
    labels: chartLabels,
    datasets: [
      {
        label: 'Fleet Compliance Score',
        data: chartValues,
        borderColor: '#4338CA', // Primary
        backgroundColor: 'rgba(67, 56, 202, 0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#4338CA',
      }
    ]
  }), [chartLabels, chartValues]);

  const barChartData = useMemo(() => ({
    labels: ['Driver', 'Vehicle', 'Maintenance', 'Inspection'],
    datasets: [
      {
        label: 'Compliance (%)',
        data: [
          summary.driver_compliance_score, 
          summary.vehicle_compliance_score, 
          summary.maintenance_compliance_score, 
          summary.inspection_compliance_score
        ],
        backgroundColor: ['#4338CA', '#0D9488', '#D97706', '#E11D48'],
        borderRadius: 4,
      }
    ]
  }), [summary.driver_compliance_score, summary.vehicle_compliance_score, summary.maintenance_compliance_score, summary.inspection_compliance_score]);

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
    },
    scales: {
      y: { min: 0, max: 100, grid: { color: '#F1F5F9' }, border: { display: false } },
      x: { grid: { display: false }, border: { display: false } }
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
              <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Fleet Compliance Report</h1>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Holistic organization compliance tracking</p>
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
            { title: 'Fleet Score', value: `${summary.fleet_compliance_score}%`, icon: 'score', bg: 'bg-primary-container/20', color: 'text-primary' },
            { title: 'Driver', value: `${summary.driver_compliance_score}%`, icon: 'person', bg: 'bg-secondary-container/20', color: 'text-secondary' },
            { title: 'Vehicle', value: `${summary.vehicle_compliance_score}%`, icon: 'local_shipping', bg: 'bg-tertiary-container/20', color: 'text-tertiary' },
            { title: 'Maintenance', value: `${summary.maintenance_compliance_score}%`, icon: 'build', bg: 'bg-error-container/20', color: 'text-error' },
            { title: 'Inspection', value: `${summary.inspection_compliance_score}%`, icon: 'plumbing', bg: 'bg-surface-container-high', color: 'text-outline' },
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

        {/* Analytics Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg">
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col min-h-[350px]">
            <div className="flex justify-between items-center mb-md">
              <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Compliance Trends</h2>
              <select 
                value={filterPeriod}
                onChange={(e) => setFilterPeriod(e.target.value)}
                className="bg-surface-container-low text-xs font-bold text-on-surface rounded-lg px-2 py-1 border border-outline-variant outline-none"
              >
                <option value="Weekly">Weekly</option>
                <option value="Monthly">Monthly</option>
                <option value="Quarterly">Quarterly</option>
                <option value="Yearly">Yearly</option>
              </select>
            </div>
            <div className="flex-1 relative">
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center bg-surface/50"><span className="material-symbols-outlined animate-spin text-primary">sync</span></div>
              ) : (
                <Line data={lineChartData} options={chartOptions} />
              )}
            </div>
          </div>
          
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col min-h-[350px]">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface mb-md">Compliance Breakdown</h2>
            <div className="flex-1 relative">
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center bg-surface/50"><span className="material-symbols-outlined animate-spin text-primary">sync</span></div>
              ) : (
                <Bar data={barChartData} options={chartOptions} />
              )}
            </div>
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex justify-end gap-2 mt-4">
          <button onClick={handleExportCSV} className="h-10 px-4 bg-surface-container-low text-on-surface font-bold rounded-lg flex items-center gap-2 hover:bg-surface-container border border-outline-variant transition-all">
            <span className="material-symbols-outlined text-[18px]">table_chart</span>
            <span className="font-body-md text-body-md">Export CSV</span>
          </button>
          <button onClick={handleExportPDF} className="h-10 px-4 bg-surface-container-low text-on-surface font-bold rounded-lg flex items-center gap-2 hover:bg-surface-container border border-outline-variant transition-all">
            <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
            <span className="font-body-md text-body-md">Export PDF</span>
          </button>
        </div>

        {/* Table Container */}
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[700px]">
              <thead className="bg-surface-container-low sticky top-0 z-10">
                <tr>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Compliance Category</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Compliance Percentage</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Risk Level</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Status</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-right">Last Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(4)].map((_, i) => (
                    <tr key={i} className="hover:bg-surface-container-low transition-colors animate-pulse">
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                      <td className="px-md py-4"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-4 text-right"><div className="h-4 bg-slate-200 rounded w-20 ml-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedCategories.map((cat, i) => (
                  <tr key={i} className="hover:bg-surface-container-lowest bg-white transition-colors group">
                    <td className="px-md py-4">
                      <p className="font-data-tabular text-data-tabular text-on-surface font-semibold">{cat.category}</p>
                    </td>
                    <td className="px-md py-4">
                      <div className="flex items-center gap-2">
                        <span className="font-data-tabular text-data-tabular">{cat.percentage}%</span>
                        <div className="w-24 h-1.5 bg-surface-container rounded-full overflow-hidden">
                          <div className={`h-full ${cat.percentage >= 80 ? 'bg-secondary' : cat.percentage >= 60 ? 'bg-primary' : 'bg-error'}`} style={{ width: `${cat.percentage}%` }}></div>
                        </div>
                      </div>
                    </td>
                    <td className="px-md py-4">
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
                        cat.risk_level === 'Low' ? 'bg-secondary-container/50 text-secondary' :
                        cat.risk_level === 'Medium' ? 'bg-primary-container/50 text-primary' :
                        'bg-error-container/50 text-error'
                      }`}>{cat.risk_level}</span>
                    </td>
                    <td className="px-md py-4">
                      <span className="font-data-tabular text-data-tabular">{cat.status}</span>
                    </td>
                    <td className="px-md py-4 text-right text-on-surface-variant font-data-tabular">
                      {new Date(cat.last_updated).toLocaleDateString('en-GB')}
                    </td>
                  </tr>
                ))}
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
              <button onClick={() => handlePageChange('next')} disabled={currentPage === totalPages} className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-outline transition-colors disabled:opacity-40">
                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FleetCompliance;
