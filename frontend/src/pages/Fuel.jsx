import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadCSV } from '../utils/exportUtils';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import FuelModal from './fuel/FuelModal';
import ConfirmDeleteDialog from '../components/ui/ConfirmDeleteDialog';
import { useToast } from '../contexts/ToastContext';

const Fuel = () => {
  const location = useLocation();
  const { showToast } = useToast();

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modals and Dialogs
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Pagination state
  const [itemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchData = useCallback(async () => {
    const [fuelRes, effRes] = await Promise.all([
      api.get('/fuel'),
      api.get('/fuel/efficiency')
    ]);
    return {
      records: fuelRes.data.data || [],
      efficiencyStats: effRes.data.data || []
    };
  }, []);

  const { data, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchData,
    [],
    'low'
  );

  const records = data?.records || [];
  const efficiencyStats = data?.efficiencyStats || [];

  useEffect(() => {
    if (location.state?.openModal) {
      openModal();
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Compute KPIs from local data
  const kpis = useMemo(() => {
    // Total fuel cost (all time or just sum of records)
    const totalCost = records.reduce((sum, r) => sum + parseFloat(r.total_cost || 0), 0);
    
    // Avg efficiency
    let avgEfficiency = 0;
    if (efficiencyStats.length > 0) {
      const totalEff = efficiencyStats.reduce((sum, s) => sum + parseFloat(s.avg_fuel_efficiency_kmpl || 0), 0);
      avgEfficiency = totalEff / efficiencyStats.length;
    }

    return { 
      totalCost: totalCost.toLocaleString('en-IN', { style: 'currency', currency: 'INR' }), 
      avgEfficiency: avgEfficiency.toFixed(1) + ' KMPL'
    };
  }, [records, efficiencyStats]);

  // Generate simple chart data
  const chartData = useMemo(() => {
    if (records.length === 0) return null;
    
    // Sort by date ascending
    const sorted = [...records].sort((a,b) => new Date(a.refuel_date) - new Date(b.refuel_date));
    
    // Group by date string
    const grouped = {};
    sorted.forEach(r => {
      const d = new Date(r.refuel_date).toISOString().split('T')[0];
      if (!grouped[d]) grouped[d] = 0;
      grouped[d] += parseFloat(r.total_cost);
    });

    const entries = Object.entries(grouped);
    if (entries.length === 0) return null;

    // For SVG: map to X [0, 1000], Y [240, 0]
    const maxCost = Math.max(...entries.map(e => e[1]), 100); // at least 100 to avoid div by zero
    
    const points = entries.map((entry, idx) => {
      const x = entries.length > 1 ? (idx / (entries.length - 1)) * 1000 : 500;
      const y = 240 - ((entry[1] / maxCost) * 200); // leaving some margin at top
      return { x, y, date: entry[0], cost: entry[1] };
    });

    const polylineStr = points.map(p => `${p.x},${p.y}`).join(' ');
    const fillStr = `0,240 ${polylineStr} 1000,240`;

    return { points, polylineStr, fillStr };
  }, [records]);


  // Search and Filter logic
  const filteredRecords = useMemo(() => {
    return records.filter(r => {
      const searchLower = searchTerm.toLowerCase();
      
      const vId = (r.vehicle?.registration_number || '').toLowerCase();
      const type = (r.fuel_type || '').toLowerCase();
      const station = (r.station_name || '').toLowerCase();
      
      return vId.includes(searchLower) || 
             type.includes(searchLower) || 
             station.includes(searchLower);
    }).sort((a, b) => new Date(b.refuel_date) - new Date(a.refuel_date)); // desc
  }, [records, searchTerm]);

  // Pagination logic
  const totalItems = filteredRecords.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedRecords = filteredRecords.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  // ---------------- Handlers ----------------

  const openModal = async (record = null) => {
    if (record) {
      try {
        const response = await api.get(`/fuel/${record.id}`);
        setEditingRecord(response.data.data);
      } catch {
        alert("Failed to fetch full record details.");
        return;
      }
    } else {
      setEditingRecord(null);
    }
    setIsModalOpen(true);
  };

  const handleSaveRecord = async (payload) => {
    setIsSaving(true);
    try {
      if (editingRecord) {
        await api.put(`/fuel/${editingRecord.id}`, payload);
      } else {
        await api.post('/fuel', payload);
      }
      setIsModalOpen(false);
      silentRefresh();
    } finally {
      setIsSaving(false);
    }
  };

  const openDeleteDialog = (record) => {
    setRecordToDelete(record);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteRecord = async () => {
    if (!recordToDelete) return;
    setIsDeleting(true);
    try {
      await api.delete(`/fuel/${recordToDelete.id}`);
      setIsDeleteDialogOpen(false);
      setRecordToDelete(null);
      silentRefresh();
    } catch {
      alert("Failed to delete record.");
    } finally {
      setIsDeleting(false);
    }
  };

  // ---------------- UI Helpers ----------------

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-background">
      
      {/* Dashboard Content Scrollable Area */}
      <div className="flex-1 overflow-y-auto p-3 md:p-lg custom-scrollbar min-w-0">
        
        {error && (
          <div className="mb-lg p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
            <span className="material-symbols-outlined">error</span>
            <p className="flex-1 font-bold">{error}</p>
            <button onClick={fetchData} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
          </div>
        )}

        {/* Top Header/Toolbar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-md mb-lg">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Fuel & Expense Analytics</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Monitoring operational costs across the fleet</p>
          </div>
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <div className="flex items-center bg-surface-container-lowest border border-outline-variant rounded-lg px-3 py-2 mr-2 hidden md:flex">
              <span className="material-symbols-outlined text-outline text-sm mr-2">calendar_month</span>
              <select onChange={(e) => showToast(`Date filter updated: ${e.target.value}`, 'info')} className="bg-transparent border-none text-body-sm font-medium p-0 focus:ring-0 cursor-pointer outline-none">
                <option>All Time</option>
                <option>This Month</option>
                <option>Last Month</option>
              </select>
            </div>
            <button 
              onClick={refresh} 
              disabled={loading || isSyncing}
              className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50"
              title="Refresh"
            >
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
            <button 
              onClick={() => openModal()}
              className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm whitespace-nowrap"
            >
              <span className="material-symbols-outlined">add</span>
              <span className="font-body-md text-body-md">Log New Expense</span>
            </button>
          </div>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-md mb-lg">
          {/* KPI Card 1: Fuel Cost */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
                <span className="material-symbols-outlined">local_gas_station</span>
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Total Fuel Cost</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">{kpis.totalCost}</h3>
            <div className="mt-4 flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
              <div className="flex-1 h-1 bg-surface-variant rounded-full overflow-hidden">
                <div className="h-full bg-primary w-[65%]"></div>
              </div>
            </div>
          </div>

          {/* KPI Card 2: Efficiency */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-secondary-container/20 text-secondary group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span className="material-symbols-outlined">speed</span>
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Avg. Fuel Efficiency</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">{kpis.avgEfficiency}</h3>
            <p className="text-body-sm text-on-surface-variant mt-2">Fleet average</p>
          </div>

          {/* KPI Card 3: Non-Fuel Expenses (Static) */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-tertiary-fixed/20 text-tertiary group-hover:bg-tertiary group-hover:text-on-tertiary transition-colors">
                <span className="material-symbols-outlined">account_balance_wallet</span>
              </div>
              <div className="flex items-center gap-xs text-outline font-bold text-xs bg-surface-container-highest px-2 py-1 rounded">
                Static
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Non-Fuel Expenses</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">₹18,290.00</h3>
            <p className="text-body-sm text-on-surface-variant mt-2">Maintenance, Tolls, Insurance</p>
          </div>
        </div>

        {/* Charts Section: Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-md mb-lg">
          
          {/* Fuel Trends Line Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-lg shadow-sm">
            <div className="flex justify-between items-center mb-xl">
              <div>
                <h4 className="font-title-sm text-title-sm">Fuel Spending Trends</h4>
                <p className="text-body-sm text-on-surface-variant">Daily fuel expenditure</p>
              </div>
            </div>
            <div className="h-[240px] w-full relative flex flex-col justify-end">
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
              </div>
              
              {chartData ? (
                <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 1000 240">
                  <defs>
                    <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#0040a1" stopOpacity="0.2"></stop>
                      <stop offset="100%" stopColor="#0040a1" stopOpacity="0"></stop>
                    </linearGradient>
                  </defs>
                  <polygon points={chartData.fillStr} fill="url(#chartFill)"></polygon>
                  <polyline points={chartData.polylineStr} fill="none" stroke="#0040a1" strokeWidth="3"></polyline>
                  {chartData.points.map((p, i) => (
                    <circle key={i} cx={p.x} cy={p.y} fill="#0040a1" r="4">
                      <title>{p.date}: ₹{p.cost.toFixed(2)}</title>
                    </circle>
                  ))}
                </svg>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center text-on-surface-variant">
                  <p>Not enough data to graph.</p>
                </div>
              )}
            </div>
          </div>

          {/* Expense Breakdown Doughnut Chart (Static representation) */}
          <div className="bg-white rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col">
            <h4 className="font-title-sm text-title-sm mb-1">Expense Breakdown</h4>
            <p className="text-body-sm text-on-surface-variant mb-xl">Allocation of non-fuel costs</p>
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="relative w-48 h-48 mb-lg">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" fill="none" r="40" stroke="#f1f3f5" strokeWidth="12"></circle>
                  <circle cx="50" cy="50" fill="none" r="40" stroke="#0040a1" strokeDasharray="251.2" strokeDashoffset="150" strokeWidth="12"></circle>
                  <circle cx="50" cy="50" fill="none" r="40" stroke="#1b6d24" strokeDasharray="251.2" strokeDashoffset="210" strokeWidth="12"></circle>
                  <circle cx="50" cy="50" fill="none" r="40" stroke="#773300" strokeDasharray="251.2" strokeDashoffset="240" strokeWidth="12"></circle>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-label-caps text-outline">TOTAL</span>
                  <span className="font-title-sm">₹18,300</span>
                </div>
              </div>
              <div className="w-full space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                    <div className="w-3 h-3 rounded-full bg-primary"></div>
                    <span className="text-body-sm font-medium">Maintenance</span>
                  </div>
                  <span className="text-body-sm font-bold text-on-surface">45%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                    <div className="w-3 h-3 rounded-full bg-secondary"></div>
                    <span className="text-body-sm font-medium">Tolls</span>
                  </div>
                  <span className="text-body-sm font-bold text-on-surface">30%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                    <div className="w-3 h-3 rounded-full bg-tertiary"></div>
                    <span className="text-body-sm font-medium">Insurance</span>
                  </div>
                  <span className="text-body-sm font-bold text-on-surface">25%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md mb-md mt-lg">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]" 
                placeholder="Search fuel logs, vehicles, or stations..." 
                type="text"
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              />
            </div>
          </div>
        </div>

        {/* Recent Logs Table */}
        <div className="bg-white rounded-xl border border-outline-variant shadow-sm overflow-hidden mb-lg flex flex-col min-h-[300px]">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Recent Fuel Activity Logs</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => window.print()} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Print List">
                <span className="material-symbols-outlined text-[20px]">print</span>
              </button>
              <button onClick={() => downloadCSV(filteredRecords, 'fuel_logs_export.csv')} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
                <span className="material-symbols-outlined text-[20px]">download</span>
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-surface-container-lowest border-b border-outline-variant">
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Date</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Vehicle</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Details</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold text-right">Amount</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(3)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-40"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-16 ml-auto"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-12 mx-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedRecords.map(record => (
                  <tr key={record.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-3 md:px-lg py-4 text-data-tabular whitespace-nowrap">
                      {formatDate(record.refuel_date)}
                    </td>
                    <td className="px-3 md:px-lg py-4">
                      <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                        <span className="material-symbols-outlined text-outline">local_shipping</span>
                        <span className="font-medium text-body-md truncate max-w-[150px]">{record.vehicle?.registration_number}</span>
                      </div>
                    </td>
                    <td className="px-3 md:px-lg py-4">
                      <span className="flex items-center gap-xs">
                        <span className="material-symbols-outlined text-primary text-[18px]">local_gas_station</span>
                        {record.fuel_type} Fill-up ({record.quantity_liters}L) 
                        {record.station_name ? ` at ${record.station_name}` : ''}
                      </span>
                    </td>
                    <td className="px-3 md:px-lg py-4 text-right font-bold text-data-tabular">
                      ₹{parseFloat(record.total_cost).toFixed(2)}
                    </td>
                    <td className="px-3 md:px-lg py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button onClick={() => openModal(record)} className="p-1 hover:bg-surface-variant rounded transition-colors text-outline" title="Edit">
                          <span className="material-symbols-outlined">edit</span>
                        </button>
                        <button onClick={() => openDeleteDialog(record)} className="p-1 hover:bg-error-container/30 text-error rounded transition-colors" title="Delete">
                          <span className="material-symbols-outlined">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedRecords.length === 0 && !loading && (
                  <tr>
                    <td colSpan="5" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">local_gas_station</span>
                      <p>No fuel logs found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="px-lg py-3 border-t border-outline-variant bg-surface-container-low flex items-center justify-between mt-auto">
            <span className="text-body-sm text-outline">Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} records</span>
            <div className="flex gap-xs">
              <button 
                onClick={() => handlePageChange('prev')} disabled={currentPage === 1}
                className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[18px]">chevron_left</span>
              </button>
              <button className="w-8 h-8 flex items-center justify-center rounded bg-primary text-on-primary font-bold text-xs">{currentPage}</button>
              <button 
                onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0}
                className="w-8 h-8 flex items-center justify-center rounded border border-outline-variant hover:bg-surface-container transition-colors disabled:opacity-50"
              >
                <span className="material-symbols-outlined text-[18px]">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <FuelModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRecord}
        fuelRecord={editingRecord}
        isSaving={isSaving}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteRecord}
        title="Delete Fuel Record"
        message={`Are you sure you want to permanently delete this fuel record?`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default Fuel;
