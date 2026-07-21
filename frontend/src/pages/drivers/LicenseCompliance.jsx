import React, { useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';

const LicenseCompliance = () => {
  const navigate = useNavigate();

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Pagination state
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  // Fetch summary data
  const fetchSummary = useCallback(async () => {
    const response = await api.get('/license-compliance/summary');
    return response.data;
  }, []);

  const { data: summaryData, loading: loadingSummary, error: summaryError, refresh: refreshSummary } = useDataSync(
    fetchSummary,
    [],
    'medium'
  );

  const fetchList = useCallback(async () => {
    const response = await api.get('/license-compliance?limit=1000');
    return response.data.data || [];
  }, []);

  const { data: listData, loading: loadingList, isSyncing, error: listError, refresh: refreshList } = useDataSync(
    fetchList,
    [],
    'medium'
  );

  const drivers = listData || [];
  const summary = summaryData || {
    total_drivers: 0,
    valid_licenses: 0,
    expired_licenses: 0,
    expiring_in_7_days: 0,
    expiring_in_30_days: 0,
    compliance_percentage: 100
  };

  const refreshAll = () => {
    refreshSummary();
    refreshList();
  };

  const loading = loadingSummary || loadingList;
  const error = summaryError || listError;

  // Search and Filter logic
  const filteredDrivers = useMemo(() => {
    return drivers.filter(d => {
      const matchesStatus = statusFilter === 'All' || d.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      
      const name = (d.full_name || '').toLowerCase();
      const license = (d.license_number || '').toLowerCase();
      
      const matchesSearch = name.includes(searchLower) || license.includes(searchLower);
      
      return matchesStatus && matchesSearch;
    });
  }, [drivers, searchTerm, statusFilter]);

  // Pagination logic
  const totalItems = filteredDrivers.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedDrivers = filteredDrivers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getStatusChip = (status) => {
    switch(status) {
      case 'Valid':
        return (
          <span className="status-chip bg-secondary-container/30 text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary mr-1.5"></span> Valid
          </span>
        );
      case 'Expiring Soon':
      case 'Expiring in 7 Days':
      case 'Expiring in 30 Days':
        return (
          <span className="status-chip bg-primary-container/20 text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary mr-1.5"></span> {status}
          </span>
        );
      case 'Expired':
        return (
          <span className="status-chip bg-error-container/50 text-error">
            <span className="w-1.5 h-1.5 rounded-full bg-error mr-1.5"></span> Expired
          </span>
        );
      case 'Suspended':
        return (
          <span className="status-chip bg-surface-container-high text-outline">
            <span className="w-1.5 h-1.5 rounded-full bg-outline mr-1.5"></span> Suspended
          </span>
        );
      default:
        return (
          <span className="status-chip bg-surface-container-high text-outline">
            <span className="w-1.5 h-1.5 rounded-full bg-outline mr-1.5"></span> {status}
          </span>
        );
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  };

  const handleExportCSV = async () => {
    console.log('TRANSITOPS_FIX_V3: EXPORTING CSV');
    try {
      const response = await api.get('/license-compliance/export/csv', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `license_compliance_report_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Export failed", err);
      alert("Failed to export CSV.");
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await api.get('/license-compliance/export/pdf', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `license_compliance_report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Export failed", err);
      alert("Failed to export PDF.");
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <section className="flex-1 overflow-y-auto p-3 md:p-lg space-y-lg custom-scrollbar min-w-0">
        
        {/* Top Header/Toolbar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/drivers')} 
              className="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-surface-container-low text-on-surface-variant transition-colors"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-on-surface">License Compliance</h1>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Monitor and manage driver license renewals</p>
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

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-md w-full">
          {[
            { title: 'Total Drivers', value: summary.total_drivers, icon: 'group', color: 'text-outline', bg: 'bg-surface-container-high/50' },
            { title: 'Valid Licences', value: summary.valid_licenses, icon: 'verified', color: 'text-secondary', bg: 'bg-secondary-container/20' },
            { title: 'Expiring in 7 Days', value: summary.expiring_in_7_days, icon: 'warning', color: 'text-primary', bg: 'bg-primary-container/20' },
            { title: 'Expiring in 30 Days', value: summary.expiring_in_30_days, icon: 'schedule', color: 'text-primary', bg: 'bg-primary-container/10' },
            { title: 'Expired Licences', value: summary.expired_licenses, icon: 'error', color: 'text-error', bg: 'bg-error-container/20' },
            { title: 'Compliance %', value: `${summary.compliance_percentage}%`, icon: 'analytics', color: 'text-secondary', bg: 'bg-secondary-container/10' },
          ].map((kpi, index) => (
            <div key={index} className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm flex flex-col gap-2">
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

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
            <span className="material-symbols-outlined">error</span>
            <p className="flex-1 font-bold">{error}</p>
            <button onClick={refreshAll} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
          </div>
        )}

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]" 
                placeholder="Search drivers or license..." 
                type="text"
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              />
            </div>
            <div className="flex items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant cursor-pointer hover:bg-surface-container transition-colors h-10">
              <span className="material-symbols-outlined text-[18px] text-outline">filter_list</span>
              <select 
                value={statusFilter}
                onChange={(e) => {setStatusFilter(e.target.value); setCurrentPage(1);}}
                className="bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="Valid">Valid</option>
                <option value="Expiring Soon">Expiring Soon</option>
                <option value="Expiring in 7 Days">Expiring in 7 Days</option>
                <option value="Expired">Expired</option>
                <option value="Suspended">Suspended</option>
              </select>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button onClick={handleExportCSV} className="h-10 px-4 bg-surface-container-low text-on-surface font-bold rounded-lg flex items-center gap-2 hover:bg-surface-container border border-outline-variant transition-all">
              <span className="material-symbols-outlined text-[18px]">table_chart</span>
              <span className="font-body-md text-body-md">Export CSV</span>
            </button>
            <button onClick={handleExportPDF} className="h-10 px-4 bg-surface-container-low text-on-surface font-bold rounded-lg flex items-center gap-2 hover:bg-surface-container border border-outline-variant transition-all">
              <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
              <span className="font-body-md text-body-md">Export PDF</span>
            </button>
          </div>
        </div>

        {/* Table Container */}
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead className="bg-surface-container-low sticky top-0 z-10">
                <tr>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Driver Details</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">License Details</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Vehicle Assignment</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-center">Expiry Date</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-center">Days Remaining</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Status</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="hover:bg-surface-container-low transition-colors animate-pulse">
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-32 mb-1"></div><div className="h-3 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-24 mb-1"></div><div className="h-3 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                      <td className="px-md py-4 text-center"><div className="h-4 bg-slate-200 rounded w-20 mx-auto"></div></td>
                      <td className="px-md py-4 text-center"><div className="h-4 bg-slate-200 rounded w-12 mx-auto"></div></td>
                      <td className="px-md py-4"><div className="h-6 bg-slate-200 rounded-full w-24"></div></td>
                      <td className="px-md py-4 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedDrivers.map(driver => (
                  <tr key={driver.id} className="hover:bg-surface-container-lowest bg-white transition-colors group">
                    <td className="px-md py-4">
                      <p className="font-data-tabular text-data-tabular text-on-surface font-semibold">{driver.full_name || 'Unknown'}</p>
                      <p className="text-[11px] text-outline">ID: {driver.id.split('-')[0].toUpperCase()}</p>
                    </td>
                    <td className="px-md py-4">
                      <p className="font-data-tabular text-data-tabular text-on-surface">{driver.license_category || 'N/A'}</p>
                      <p className="text-xs text-on-surface-variant">#{driver.license_number || 'N/A'}</p>
                    </td>
                    <td className="px-md py-4">
                      <span className="font-data-tabular text-data-tabular">{driver.vehicle_assignment || 'Unassigned'}</span>
                    </td>
                    <td className="px-md py-4 text-center">
                      <span className="font-data-tabular text-data-tabular">{formatDate(driver.license_expiry_date)}</span>
                    </td>
                    <td className="px-md py-4 text-center">
                      <span className={`font-data-tabular text-data-tabular font-bold ${driver.days_remaining <= 0 ? 'text-error' : driver.days_remaining <= 30 ? 'text-primary' : 'text-on-surface'}`}>
                        {driver.days_remaining <= 0 ? 'Expired' : `${driver.days_remaining} days`}
                      </span>
                    </td>
                    <td className="px-md py-4">
                      {getStatusChip(driver.status)}
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
                ))}
                {paginatedDrivers.length === 0 && !loading && (
                  <tr>
                    <td colSpan="7" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">description</span>
                      <p>No license data found.</p>
                    </td>
                  </tr>
                )}
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
              <button 
                onClick={() => handlePageChange('prev')}
                disabled={currentPage === 1}
                className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-outline transition-colors disabled:opacity-40"
              >
                <span className="material-symbols-outlined text-[20px]">chevron_left</span>
              </button>
              
              <button className="w-8 h-8 flex items-center justify-center rounded bg-primary text-on-primary text-xs font-bold">{currentPage}</button>
              
              {currentPage < totalPages && (
                <button className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-xs font-medium text-on-surface cursor-default">
                  of {totalPages}
                </button>
              )}
              
              <button 
                onClick={() => handlePageChange('next')}
                disabled={currentPage === totalPages || totalPages === 0}
                className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container text-outline transition-colors disabled:opacity-40"
              >
                <span className="material-symbols-outlined text-[20px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LicenseCompliance;
