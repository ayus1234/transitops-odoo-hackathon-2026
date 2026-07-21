import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Technicians = () => {
  const location = useLocation();
  const { showToast } = useToast();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchTechnicians = useCallback(async () => {
    const response = await api.get('/maintenance/technicians');
    return response.data.data || [];
  }, []);

  const { data: techniciansData, loading, isSyncing, error, refresh } = useDataSync(
    fetchTechnicians,
    [],
    'medium'
  );
  
  const technicians = techniciansData || [];

  // Compute KPIs
  const kpis = useMemo(() => {
    const total = technicians.length;
    const active = technicians.filter(t => t.status !== 'Off Duty' && t.status !== 'On Leave').length;
    const available = technicians.filter(t => t.status === 'Available').length;
    const assigned = technicians.filter(t => t.status === 'Assigned').length;
    const overloaded = technicians.filter(t => t.utilization_pct >= 100).length;
    const utilPct = total > 0 ? Math.round(technicians.reduce((acc, t) => acc + t.utilization_pct, 0) / total) : 0;
    
    return { total, active, available, assigned, overloaded, utilPct };
  }, [technicians]);

  // Search & Filter
  const filteredTechnicians = useMemo(() => {
    return technicians.filter(t => {
      const matchesStatus = statusFilter === 'All' || t.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const tName = (t.name || '').toLowerCase();
      const tId = (t.id || '').toLowerCase();
      const matchesSearch = 
        tName.includes(searchLower) ||
        tId.includes(searchLower);
      
      return matchesStatus && matchesSearch;
    });
  }, [technicians, searchTerm, statusFilter]);

  const totalItems = filteredTechnicians.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedTechnicians = filteredTechnicians.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getStatusChip = (status) => {
    switch(status) {
      case 'Available':
        return (
          <span className="bg-[#4CAF50]/20 text-[#4CAF50] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#4CAF50]"></span> Available
          </span>
        );
      case 'Assigned':
        return (
          <span className="bg-[#2196F3]/20 text-[#2196F3] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#2196F3]"></span> Assigned
          </span>
        );
      case 'Busy':
        return (
          <span className="bg-[#FF9800]/20 text-[#FF9800] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF9800]"></span> Busy
          </span>
        );
      case 'On Leave':
        return (
          <span className="bg-[#F44336]/20 text-[#F44336] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#F44336]"></span> On Leave
          </span>
        );
      case 'Off Duty':
      default:
        return (
          <span className="bg-[#9E9E9E]/20 text-[#9E9E9E] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[#9E9E9E]"></span> Off Duty
          </span>
        );
    }
  };

  // Chart Data
  const workloadChartData = useMemo(() => {
    const labels = technicians.slice(0, 10).map(t => (t.name || 'Unknown').split(' ')[0]);
    const activeTasks = technicians.slice(0, 10).map(t => t.assigned_jobs);
    return {
      labels,
      datasets: [
        {
          label: 'Active Tasks',
          data: activeTasks,
          backgroundColor: '#2196F3',
          borderRadius: 4,
        }
      ]
    };
  }, [technicians]);

  const statusChartData = useMemo(() => {
    return {
      labels: ['Available', 'Assigned', 'Busy', 'Off Duty', 'On Leave'],
      datasets: [
        {
          data: [kpis.available, kpis.assigned, technicians.filter(t=>t.status==='Busy').length, technicians.filter(t=>t.status==='Off Duty').length, technicians.filter(t=>t.status==='On Leave').length],
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#9E9E9E', '#F44336'],
          borderWidth: 0,
        }
      ]
    };
  }, [kpis, technicians]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#888', font: { size: 12 } } },
    }
  };

  const handleExportCSV = async () => {
    try {
      const response = await api.get('/maintenance/technicians/export?format=csv');
      // If endpoint returns direct csv text, or JSON with base64/url, adapt based on actual implementation.
      // For simplicity, fallback to frontend export:
      downloadCSV(technicians, 'technicians_export.csv');
    } catch {
      showToast('Export failed', 'error');
    }
  };

  const handleExportPDF = () => {
    try {
      downloadPDF(technicians, 'technicians_export.pdf', 'Technician Directory');
    } catch {
      showToast('Export failed', 'error');
    }
  };

  return (
    <div className="p-3 md:p-gutter flex flex-col gap-gutter flex-1 min-w-0">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full px-md mt-4 gap-4">
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Manage Technicians</h1>
        <div className="flex items-center gap-md">
          <button 
            onClick={refresh} 
            disabled={loading || isSyncing}
            className="p-2 rounded-full hover:bg-surface-container-high transition-all text-on-surface-variant flex items-center justify-center disabled:opacity-50"
            title="Refresh"
          >
            <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-md p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
          <span className="material-symbols-outlined">error</span>
          <p className="flex-1 font-bold">{error}</p>
          <button onClick={refresh} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-6 gap-md mx-md">
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">TOTAL TECHS</p>
          <h2 className="text-title-lg font-bold text-on-surface">{kpis.total}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">ACTIVE</p>
          <h2 className="text-title-lg font-bold text-[#2196F3]">{kpis.active}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">AVAILABLE</p>
          <h2 className="text-title-lg font-bold text-[#4CAF50]">{kpis.available}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">ASSIGNED</p>
          <h2 className="text-title-lg font-bold text-outline">{kpis.assigned}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">OVERLOADED</p>
          <h2 className="text-title-lg font-bold text-[#F44336]">{kpis.overloaded}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">UTILIZATION</p>
          <h2 className="text-title-lg font-bold text-on-surface">{kpis.utilPct}%</h2>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-md mx-md">
        <div className="md:col-span-2 bg-surface border border-outline-variant rounded-lg p-md shadow-sm h-72 flex flex-col">
          <h3 className="font-title-sm text-title-sm font-bold text-on-surface mb-4">Workload Distribution</h3>
          <div className="flex-1 relative">
            <Bar data={workloadChartData} options={chartOptions} />
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-lg p-md shadow-sm h-72 flex flex-col">
          <h3 className="font-title-sm text-title-sm font-bold text-on-surface mb-4">Status Breakdown</h3>
          <div className="flex-1 relative pb-2">
            <Pie data={statusChartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Action & Filter Bar */}
      <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md mx-md">
        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto w-full md:w-auto">
          <div className="relative flex-1 md:flex-none">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
            <input 
              type="text" 
              placeholder="Search technicians..." 
              value={searchTerm}
              onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all"
            />
          </div>
          <div className="flex items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant h-10">
            <span className="material-symbols-outlined text-[18px] text-outline">filter_list</span>
            <select 
              value={statusFilter}
              onChange={(e) => {setStatusFilter(e.target.value); setCurrentPage(1);}}
              className="bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
            >
              <option value="All">All Statuses</option>
              <option value="Available">Available</option>
              <option value="Assigned">Assigned</option>
              <option value="Busy">Busy</option>
              <option value="Off Duty">Off Duty</option>
              <option value="On Leave">On Leave</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col mx-1 md:mx-md mb-md min-w-0">
        <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
          <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Technician Directory</h2>
          <div className="flex items-center gap-2">
            <button onClick={handleExportPDF} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download PDF">
              <span className="material-symbols-outlined text-[20px]">picture_as_pdf</span>
            </button>
            <button onClick={handleExportCSV} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[900px]">
            <thead>
              <tr className="bg-surface-container text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                <th className="px-md py-3.5">ID</th>
                <th className="px-md py-3.5">Name</th>
                <th className="px-md py-3.5">Status</th>
                <th className="px-md py-3.5">Assigned Vehicles</th>
                <th className="px-md py-3.5">Active Jobs</th>
                <th className="px-md py-3.5">Utilization %</th>
                <th className="px-md py-3.5">Skills</th>
                <th className="px-md py-3.5">Experience</th>
                <th className="px-md py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-outline-variant animate-pulse">
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                    <td className="px-md py-3.5"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-12"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-12"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                  </tr>
                ))
              ) : paginatedTechnicians.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-12 text-on-surface-variant flex flex-col items-center">
                    <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">engineering</span>
                    <p>No technicians found matching your criteria.</p>
                  </td>
                </tr>
              ) : paginatedTechnicians.map(tech => (
                <tr key={tech.id} className="border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                  <td className="px-md py-3.5 font-bold text-primary font-data-tabular">
                    {tech.id.split('-')[0].toUpperCase()}
                  </td>
                  <td className="px-md py-3.5 font-medium">{tech.name}</td>
                  <td className="px-md py-3.5">{getStatusChip(tech.status)}</td>
                  <td className="px-md py-3.5 font-data-tabular">{tech.assigned_vehicles || 0}</td>
                  <td className="px-md py-3.5 font-data-tabular">{tech.assigned_jobs}</td>
                  <td className="px-md py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-surface-container-highest rounded-full h-1.5 overflow-hidden w-16">
                        <div 
                          className={`h-full ${tech.utilization_pct >= 100 ? 'bg-error' : tech.utilization_pct > 75 ? 'bg-[#FF9800]' : 'bg-[#4CAF50]'}`}
                          style={{width: `${Math.min(tech.utilization_pct, 100)}%`}}
                        ></div>
                      </div>
                      <span className="text-xs font-bold w-8 text-right font-data-tabular">{tech.utilization_pct}%</span>
                    </div>
                  </td>
                  <td className="px-md py-3.5 truncate max-w-[150px]" title={tech.skills.join(', ')}>
                    {tech.skills.join(', ')}
                  </td>
                  <td className="px-md py-3.5 capitalize">{tech.experience_level}</td>
                  <td className="px-md py-3.5 text-right">
                    <button onClick={() => showToast('View Technician Details coming soon', 'info')} className="p-1.5 rounded hover:bg-primary-container text-outline hover:text-primary transition-all">
                      <span className="material-symbols-outlined text-[18px]">visibility</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="mt-auto p-md border-t border-outline-variant flex flex-col md:flex-row items-center justify-between gap-4 flex-wrap bg-surface-container-lowest">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <span className="text-body-sm text-outline">Rows per page:</span>
            <select 
              value={itemsPerPage}
              onChange={(e) => {setItemsPerPage(Number(e.target.value)); setCurrentPage(1);}}
              className="bg-transparent border-none text-body-sm font-bold text-on-surface focus:ring-0 cursor-pointer outline-none"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
            </select>
          </div>
          <div className="flex items-center gap-md">
            <span className="text-body-sm text-outline">
              {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems}
            </span>
            <div className="flex items-center gap-xs">
              <button onClick={() => handlePageChange('prev')} disabled={currentPage === 1} className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors">
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0} className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors">
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Technicians;
