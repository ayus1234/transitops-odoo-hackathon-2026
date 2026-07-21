import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadCSV } from '../utils/exportUtils';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import ExpenseModal from './expenses/ExpenseModal';
import ConfirmDeleteDialog from '../components/ui/ConfirmDeleteDialog';
import { useToast } from '../contexts/ToastContext';

const Expenses = () => {
  const location = useLocation();
  const { showToast } = useToast();

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Modals and Dialogs
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const [isActionDialogOpen, setIsActionDialogOpen] = useState(false);
  const [actionRecord, setActionRecord] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [actionType, setActionType] = useState(''); // 'Approve', 'Reject'
  const [isProcessing, setIsProcessing] = useState(false);

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Pagination state
  const [itemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchData = useCallback(async () => {
    const res = await api.get('/expenses?page_size=100');
    return res.data.data || [];
  }, []);

  const { data: recordsData, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchData,
    [],
    'low'
  );

  const records = recordsData || [];

  useEffect(() => {
    if (location.state?.openModal) {
      openModal();
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Compute KPIs from local data
  const kpis = useMemo(() => {
    const totalCost = records.reduce((sum, r) => sum + parseFloat(r.amount || 0), 0);
    const approvedCost = records.filter(r => r.status === 'Approved').reduce((sum, r) => sum + parseFloat(r.amount || 0), 0);
    const pendingCount = records.filter(r => r.status === 'Pending').length;

    return { 
      totalCost: totalCost.toLocaleString('en-IN', { style: 'currency', currency: 'INR' }), 
      approvedCost: approvedCost.toLocaleString('en-IN', { style: 'currency', currency: 'INR' }),
      pendingCount
    };
  }, [records]);

  // Generate Line Chart Data (Trailing 30 Days)
  const lineChartData = useMemo(() => {
    if (records.length === 0) return null;
    
    const sorted = [...records].sort((a,b) => new Date(a.expense_date) - new Date(b.expense_date));
    
    const grouped = {};
    sorted.forEach(r => {
      const d = new Date(r.expense_date).toISOString().split('T')[0];
      if (!grouped[d]) grouped[d] = 0;
      grouped[d] += parseFloat(r.amount);
    });

    const entries = Object.entries(grouped);
    if (entries.length === 0) return null;

    const maxCost = Math.max(...entries.map(e => e[1]), 100); 
    
    const points = entries.map((entry, idx) => {
      const x = entries.length > 1 ? (idx / (entries.length - 1)) * 1000 : 500;
      const y = 240 - ((entry[1] / maxCost) * 200);
      return { x, y, date: entry[0], cost: entry[1] };
    });

    const polylineStr = points.map(p => `${p.x},${p.y}`).join(' ');
    const fillStr = `0,240 ${polylineStr} 1000,240`;

    return { points, polylineStr, fillStr };
  }, [records]);

  // Generate Doughnut Chart Data (Expense Breakdown)
  const doughnutData = useMemo(() => {
    const total = records.reduce((sum, r) => sum + parseFloat(r.amount || 0), 0);
    if (total === 0) return null;

    const breakdown = {};
    records.forEach(r => {
      if (!breakdown[r.expense_type]) breakdown[r.expense_type] = 0;
      breakdown[r.expense_type] += parseFloat(r.amount);
    });

    // We have a 251.2 circumference circle (r=40). 
    // We will render SVG strokes by offsetting the dasharray.
    const colors = {
      'Maintenance': '#0040a1', // primary
      'Toll': '#1b6d24',        // secondary
      'Repair': '#773300',      // tertiary
      'Miscellaneous': '#e1e3e4', // surface-variant
      'Fuel': '#88d982'         // secondary-fixed-dim
    };

    let currentOffset = 0;
    const segments = Object.entries(breakdown).map(([type, amount]) => {
      const pct = amount / total;
      const dash = pct * 251.2;
      const offset = 251.2 - currentOffset;
      currentOffset += dash;
      return {
        type,
        amount,
        pct: (pct * 100).toFixed(1),
        dash,
        offset,
        color: colors[type] || '#c3c6d6'
      };
    }).sort((a,b) => b.amount - a.amount);

    return { total, segments };
  }, [records]);


  // Search and Filter logic
  const filteredRecords = useMemo(() => {
    return records.filter(r => {
      const matchesStatus = statusFilter === 'All' || r.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      
      const vId = (r.vehicle?.registration_number || '').toLowerCase();
      const desc = (r.description || '').toLowerCase();
      const vendor = (r.vendor_name || '').toLowerCase();
      const type = (r.expense_type || '').toLowerCase();
      
      const matchesSearch = vId.includes(searchLower) || 
                            desc.includes(searchLower) || 
                            vendor.includes(searchLower) ||
                            type.includes(searchLower);
                            
      return matchesStatus && matchesSearch;
    }).sort((a, b) => new Date(b.expense_date) - new Date(a.expense_date));
  }, [records, searchTerm, statusFilter]);

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
        const response = await api.get(`/expenses/${record.id}`);
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
        await api.put(`/expenses/${editingRecord.id}`, payload);
      } else {
        await api.post('/expenses', payload);
      }
      setIsModalOpen(false);
      silentRefresh();
    } finally {
      setIsSaving(false);
    }
  };

  const openActionDialog = (record, type) => {
    setActionRecord(record);
    setActionType(type);
    setRejectReason('');
    setIsActionDialogOpen(true);
  };

  const handleActionConfirm = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      const status = actionType === 'Approve' ? 'Approved' : 'Rejected';
      await api.patch(`/expenses/${actionRecord.id}/status`, { 
        status, 
        reason: actionType === 'Reject' ? rejectReason : null 
      });
      setIsActionDialogOpen(false);
      silentRefresh();
    } catch {
      alert(`Failed to ${actionType.toLowerCase()} expense.`);
    } finally {
      setIsProcessing(false);
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
      await api.delete(`/expenses/${recordToDelete.id}`);
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

  const getStatusChip = (status) => {
    switch(status) {
      case 'Pending':
        return <span className="px-2 py-1 rounded-full text-[11px] font-bold bg-primary-container/10 text-primary border border-primary/20">Pending</span>;
      case 'Approved':
        return <span className="px-2 py-1 rounded-full text-[11px] font-bold bg-secondary-container/20 text-secondary border border-secondary/20">Approved</span>;
      case 'Rejected':
        return <span className="px-2 py-1 rounded-full text-[11px] font-bold bg-error-container/20 text-error border border-error/20">Rejected</span>;
      default:
        return <span className="px-2 py-1 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant">{status}</span>;
    }
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'Fuel': return 'local_gas_station';
      case 'Maintenance': return 'build';
      case 'Toll': return 'toll';
      case 'Repair': return 'handyman';
      default: return 'receipt_long';
    }
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
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Financial Operations</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Monitoring all fleet-related expenses</p>
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
          {/* KPI Card 1: Total Cost */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-on-primary transition-colors">
                <span className="material-symbols-outlined">account_balance_wallet</span>
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Total Expenses (All Time)</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">{kpis.totalCost}</h3>
            <div className="mt-4 flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
              <div className="flex-1 h-1 bg-surface-variant rounded-full overflow-hidden">
                <div className="h-full bg-primary w-[100%]"></div>
              </div>
            </div>
          </div>

          {/* KPI Card 2: Approved Cost */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-secondary-container/20 text-secondary group-hover:bg-secondary group-hover:text-on-secondary transition-colors">
                <span className="material-symbols-outlined">check_circle</span>
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Total Approved</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">{kpis.approvedCost}</h3>
            <p className="text-body-sm text-on-surface-variant mt-2">Cleared for accounting</p>
          </div>

          {/* KPI Card 3: Pending Count */}
          <div className="bg-white p-lg rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-md">
              <div className="p-3 rounded-lg bg-tertiary-fixed/20 text-tertiary group-hover:bg-tertiary group-hover:text-on-tertiary transition-colors">
                <span className="material-symbols-outlined">pending_actions</span>
              </div>
            </div>
            <p className="text-label-caps text-outline uppercase mb-1">Pending Approvals</p>
            <h3 className="font-display-lg text-display-lg text-on-surface">{kpis.pendingCount}</h3>
            <p className="text-body-sm text-on-surface-variant mt-2">Awaiting manager review</p>
          </div>
        </div>

        {/* Charts Section: Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-md mb-lg">
          
          {/* Trends Line Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-outline-variant p-lg shadow-sm">
            <div className="flex justify-between items-center mb-xl">
              <div>
                <h4 className="font-title-sm text-title-sm">Expense Spending Trends</h4>
                <p className="text-body-sm text-on-surface-variant">Daily expenditure overview</p>
              </div>
            </div>
            <div className="h-[240px] w-full relative flex flex-col justify-end">
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
                <div className="border-b border-outline"></div>
              </div>
              
              {lineChartData ? (
                <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 1000 240">
                  <defs>
                    <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#0040a1" stopOpacity="0.2"></stop>
                      <stop offset="100%" stopColor="#0040a1" stopOpacity="0"></stop>
                    </linearGradient>
                  </defs>
                  <polygon points={lineChartData.fillStr} fill="url(#chartFill)"></polygon>
                  <polyline points={lineChartData.polylineStr} fill="none" stroke="#0040a1" strokeWidth="3"></polyline>
                  {lineChartData.points.map((p, i) => (
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

          {/* Expense Breakdown Doughnut Chart */}
          <div className="bg-white rounded-xl border border-outline-variant p-lg shadow-sm flex flex-col">
            <h4 className="font-title-sm text-title-sm mb-1">Expense Breakdown</h4>
            <p className="text-body-sm text-on-surface-variant mb-xl">Allocation of total costs</p>
            <div className="flex-1 flex flex-col items-center justify-center">
              
              {doughnutData ? (
                <>
                  <div className="relative w-48 h-48 mb-lg">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" fill="none" r="40" stroke="#f1f3f5" strokeWidth="12"></circle>
                      {doughnutData.segments.map(s => (
                        <circle 
                          key={s.type}
                          cx="50" cy="50" 
                          fill="none" r="40" 
                          stroke={s.color} 
                          strokeDasharray={`${s.dash} ${251.2 - s.dash}`} 
                          strokeDashoffset={s.offset} 
                          strokeWidth="12"
                        ></circle>
                      ))}
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-label-caps text-outline">TOTAL</span>
                      <span className="font-title-sm text-center">
                        {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(doughnutData.total)}
                      </span>
                    </div>
                  </div>
                  <div className="w-full space-y-3">
                    {doughnutData.segments.slice(0, 3).map(s => (
                      <div key={s.type} className="flex items-center justify-between">
                        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                          <div className="w-3 h-3 rounded-full" style={{backgroundColor: s.color}}></div>
                          <span className="text-body-sm font-medium truncate max-w-[100px]" title={s.type}>{s.type}</span>
                        </div>
                        <span className="text-body-sm font-bold text-on-surface">{s.pct}%</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-on-surface-variant"><p>No expense data</p></div>
              )}
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
                placeholder="Search expenses..." 
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
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Recent Logs Table */}
        <div className="bg-white rounded-xl border border-outline-variant shadow-sm overflow-hidden mb-lg flex flex-col min-h-[300px]">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Recent Expense Logs</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => window.print()} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Print List">
                <span className="material-symbols-outlined text-[20px]">print</span>
              </button>
              <button onClick={() => downloadCSV(records, 'expenses_export.csv')} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
                <span className="material-symbols-outlined text-[20px]">download</span>
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-surface-container-lowest border-b border-outline-variant">
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Date</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Details</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Type</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold text-right">Amount</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold">Status</th>
                  <th className="px-3 md:px-lg py-3 text-label-caps text-outline uppercase font-bold text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(3)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-40"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-16 ml-auto"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-3 md:px-lg py-4"><div className="h-4 bg-slate-200 rounded w-12 mx-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedRecords.map(record => (
                  <tr key={record.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-3 md:px-lg py-4 text-data-tabular whitespace-nowrap">
                      {formatDate(record.expense_date)}
                    </td>
                    <td className="px-3 md:px-lg py-4">
                      <div className="flex flex-col">
                        <span className="font-medium text-body-md truncate max-w-[200px]" title={record.description}>{record.description}</span>
                        {record.vendor_name && <span className="text-[11px] text-outline">{record.vendor_name}</span>}
                      </div>
                    </td>
                    <td className="px-3 md:px-lg py-4">
                      <span className="flex items-center gap-xs whitespace-nowrap">
                        <span className={`material-symbols-outlined text-[18px] text-outline`}>{getTypeIcon(record.expense_type)}</span>
                        {record.expense_type}
                      </span>
                    </td>
                    <td className="px-3 md:px-lg py-4 text-right font-bold text-data-tabular">
                      ₹{parseFloat(record.amount).toFixed(2)}
                    </td>
                    <td className="px-3 md:px-lg py-4">
                      {getStatusChip(record.status)}
                    </td>
                    <td className="px-lg py-4 text-center">
                      <div className="flex items-center justify-center gap-1">
                        <button onClick={() => openModal(record)} className="p-1 hover:bg-surface-variant rounded transition-colors text-outline" title="Edit">
                          <span className="material-symbols-outlined text-[18px]">edit</span>
                        </button>
                        {record.status === 'Pending' && (
                          <>
                            <button onClick={() => openActionDialog(record, 'Approve')} className="p-1 hover:bg-secondary-container/30 text-secondary rounded transition-colors" title="Approve">
                              <span className="material-symbols-outlined text-[18px]">check</span>
                            </button>
                            <button onClick={() => openActionDialog(record, 'Reject')} className="p-1 hover:bg-error-container/30 text-error rounded transition-colors" title="Reject">
                              <span className="material-symbols-outlined text-[18px]">close</span>
                            </button>
                          </>
                        )}
                        <button onClick={() => openDeleteDialog(record)} className="p-1 hover:bg-error-container/30 text-error rounded transition-colors" title="Delete">
                          <span className="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedRecords.length === 0 && !loading && (
                  <tr>
                    <td colSpan="6" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">receipt_long</span>
                      <p>No expense logs found.</p>
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

      {/* Approval/Reject Dialog */}
      {isActionDialogOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50  p-4 sm:p-6">
          <div className="bg-surface rounded-xl shadow-lg overflow-hidden shrink-0" style={{ width: '100%', maxWidth: '448px', minWidth: '320px' }}>
            <div className="px-lg py-md border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
              <h3 className="font-title-sm text-title-sm text-on-surface">{actionType} Expense</h3>
              <button onClick={() => setIsActionDialogOpen(false)} className="text-on-surface-variant hover:bg-surface-variant p-1 rounded transition-colors">
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>
            <form onSubmit={handleActionConfirm} className="p-lg space-y-md">
              <p className="text-body-md text-on-surface">
                Are you sure you want to {actionType.toLowerCase()} this expense for <strong>₹{parseFloat(actionRecord?.amount).toFixed(2)}</strong>?
              </p>
              
              {actionType === 'Reject' && (
                <div className="space-y-xs mt-4">
                  <label className="font-body-sm text-body-sm font-bold text-on-surface">Reason for Rejection *</label>
                  <textarea 
                    className="w-full px-sm py-2 bg-surface-container-lowest border border-outline-variant rounded focus:border-error transition-all font-body-sm outline-none resize-none"
                    rows="3"
                    required
                    value={rejectReason}
                    onChange={(e) => setRejectReason(e.target.value)}
                  ></textarea>
                </div>
              )}

              <div className="flex justify-end gap-md pt-md mt-lg border-t border-outline-variant">
                <button type="button" onClick={() => setIsActionDialogOpen(false)} className="px-4 py-2 rounded text-on-surface-variant font-bold hover:bg-surface-variant transition-colors">
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={isProcessing}
                  className={`px-4 py-2 rounded text-white font-bold transition-opacity disabled:opacity-50 flex items-center gap-2 ${actionType === 'Approve' ? 'bg-secondary' : 'bg-error'}`}
                >
                  {isProcessing ? <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> : null}
                  {actionType === 'Approve' ? 'Confirm Approval' : 'Reject Expense'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ExpenseModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRecord}
        expenseRecord={editingRecord}
        isSaving={isSaving}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteRecord}
        title="Delete Expense Record"
        message={`Are you sure you want to permanently delete this expense?`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default Expenses;
