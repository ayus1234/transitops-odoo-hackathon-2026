import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { downloadCSV } from '../utils/exportUtils';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import MaintenanceModal from './maintenance/MaintenanceModal';
import MaintenanceActionDialog from './maintenance/MaintenanceActionDialog';
import ConfirmDeleteDialog from '../components/ui/ConfirmDeleteDialog';
import { useToast } from '../contexts/ToastContext';

const Maintenance = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { showToast } = useToast();

  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [isRestockRequested, setIsRestockRequested] = useState(false);
  const [isTechMenuOpen, setIsTechMenuOpen] = useState(false);
  
  // Modals and Dialogs
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const [isActionDialogOpen, setIsActionDialogOpen] = useState(false);
  const [actionType, setActionType] = useState(null); // 'complete', 'status'
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [recordToDelete, setRecordToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Pagination state
  const [itemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchRecords = useCallback(async () => {
    const response = await api.get('/maintenance?page_size=100');
    return response.data.data || [];
  }, []);

  const [criticalPart, setCriticalPart] = useState(null);

  useEffect(() => {
    const fetchCriticalPart = async () => {
      try {
        const res = await api.get('/inventory/parts?page_size=100');
        const parts = res.data.data || [];
        const critical = parts.find(p => p.quantity_available <= p.critical_stock_level);
        setCriticalPart(critical);
      } catch (err) {
        console.error("Failed to fetch inventory parts", err);
      }
    };
    fetchCriticalPart();
  }, []);

  const { data: recordsData, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchRecords,
    [],
    'medium'
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
    const pending = records.filter(r => r.status === 'Pending' || r.status === 'Approved').length;
    const inProgress = records.filter(r => r.status === 'In Progress').length;
    
    // Simulate shop capacity based on active jobs (assume max capacity is 12 jobs at once)
    const activeJobs = pending + inProgress;
    const shopCapacity = Math.min(Math.round((activeJobs / 12) * 100), 100);
    
    // Average downtime (just mock derived for visual parity since we don't track exact hour differences in basic schema)
    // We'll show a static 14.2h if there are records, else 0h
    const avgDowntime = records.length > 0 ? '14.2h' : '0.0h';

    return { pending, inProgress, shopCapacity, avgDowntime };
  }, [records]);

  // Derive technician workload
  const technicianWorkload = useMemo(() => {
    const activeRecords = records.filter(r => (r.status === 'Pending' || r.status === 'Approved' || r.status === 'In Progress') && r.assigned_technician);
    const workloadMap = {};
    activeRecords.forEach(r => {
      const tech = r.assigned_technician;
      if (!workloadMap[tech]) workloadMap[tech] = 0;
      workloadMap[tech]++;
    });
    
    return Object.entries(workloadMap).map(([name, count]) => {
      const maxCapacity = 5;
      const pct = Math.min((count / maxCapacity) * 100, 100);
      let colorClass = 'bg-primary';
      if (pct >= 100) colorClass = 'bg-error';
      else if (pct >= 80) colorClass = 'bg-tertiary';
      else if (pct <= 40) colorClass = 'bg-secondary';
      return { name, count, maxCapacity, pct, colorClass };
    }).sort((a,b) => b.count - a.count).slice(0, 3); // top 3 for the card
  }, [records]);

  // Derive upcoming scheduled service for timeline
  const scheduledTimeline = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const upcoming = records
      .filter(r => {
        const schedDate = new Date(r.scheduled_date);
        return (r.status === 'Pending' || r.status === 'Approved') && schedDate >= today;
      })
      .sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date))
      .slice(0, 3); // Show next 3
    
    const getDayLabel = (d) => {
      const today = new Date();
      today.setHours(0,0,0,0);
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const check = new Date(d);
      check.setHours(0,0,0,0);
      if (check.getTime() === today.getTime()) return "Today";
      if (check.getTime() === tomorrow.getTime()) return "Tomorrow";
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      return days[d.getDay()];
    };

    return upcoming.map(r => {
      const d = new Date(r.scheduled_date);
      const month = d.toLocaleString('default', { month: 'short' });
      const day = d.getDate();
      const dayLabel = getDayLabel(d);
      const timeLabel = d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
      return { ...r, month, day, dayLabel, timeLabel };
    });
  }, [records]);

  // Search and Filter logic
  const filteredRecords = useMemo(() => {
    return records.filter(r => {
      const matchesStatus = statusFilter === 'All' || r.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      
      const vId = (r.vehicle?.registration_number || '').toLowerCase();
      const desc = (r.description || '').toLowerCase();
      const tech = (r.assigned_technician || '').toLowerCase();
      const type = (r.maintenance_type || '').toLowerCase();
      
      const matchesSearch = vId.includes(searchLower) || 
                            desc.includes(searchLower) || 
                            tech.includes(searchLower) || 
                            type.includes(searchLower);
                            
      return matchesStatus && matchesSearch;
    });
  }, [records, searchTerm, statusFilter]);

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
        const response = await api.get(`/maintenance/${record.id}`);
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
        await api.put(`/maintenance/${editingRecord.id}`, payload);
      } else {
        await api.post('/maintenance', payload);
      }
      setIsModalOpen(false);
      silentRefresh();
    } finally {
      setIsSaving(false);
    }
  };

  const openActionDialog = (record, type) => {
    setSelectedRecord(record);
    setActionType(type);
    setIsActionDialogOpen(true);
  };

  const handleActionConfirm = async (payload) => {
    setIsProcessing(true);
    try {
      if (actionType === 'complete') {
        await api.post(`/maintenance/${selectedRecord.id}/complete`, payload);
      } else if (actionType === 'status') {
        await api.patch(`/maintenance/${selectedRecord.id}/status`, payload);
      }
      setIsActionDialogOpen(false);
      silentRefresh();
    } catch {
      alert(`Failed to update maintenance.`);
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
      await api.delete(`/maintenance/${recordToDelete.id}`);
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

  const getPriorityChip = (priority) => {
    switch(priority) {
      case 'Critical':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error text-on-error border border-error/20 uppercase">CRITICAL</span>;
      case 'High':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">HIGH</span>;
      case 'Medium':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-tertiary-fixed text-on-tertiary-fixed border border-tertiary/20 uppercase">MEDIUM</span>;
      case 'Low':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/20 text-on-secondary-container border border-secondary/20 uppercase">LOW</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{priority}</span>;
    }
  };

  const getStatusChip = (status) => {
    switch(status) {
      case 'Pending':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/10 text-primary border border-primary/20 uppercase">PENDING</span>;
      case 'Approved':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/30 text-primary border border-primary/40 uppercase">SCHEDULED</span>;
      case 'In Progress':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/30 text-secondary border border-secondary/20 uppercase">IN PROGRESS</span>;
      case 'Completed':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container text-on-secondary-container uppercase">COMPLETED</span>;
      case 'Rejected':
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">REJECTED</span>;
      default:
        return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{status}</span>;
    }
  };

  const getInitials = (name) => {
    if (!name) return '--';
    const parts = name.trim().split(' ');
    if (parts.length > 1) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      
      {/* Dashboard Content */}
      <div className="p-3 md:p-lg space-y-lg flex-1 overflow-y-auto custom-scrollbar min-w-0">
        
        {/* Top Header/Toolbar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Maintenance Operations</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage and monitor vehicle servicing</p>
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
            <button 
              onClick={() => openModal()}
              className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm whitespace-nowrap"
            >
              <span className="material-symbols-outlined">add</span>
              <span className="font-body-md text-body-md">New Service Record</span>
            </button>
          </div>
        </div>

        {/* KPI Header Row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-xs md:gap-md">
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm flex items-center justify-between">
            <div>
              <p className="text-label-caps text-on-surface-variant mb-1 uppercase">Pending Repairs</p>
              <h3 className="font-display-lg text-display-lg text-primary">{kpis.pending}</h3>
            </div>
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <span className="material-symbols-outlined text-[28px]">pending_actions</span>
            </div>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm flex items-center justify-between">
            <div>
              <p className="text-label-caps text-on-surface-variant mb-1 uppercase">In Progress</p>
              <h3 className="font-display-lg text-display-lg text-secondary">{kpis.inProgress}</h3>
            </div>
            <div className="w-12 h-12 rounded-full bg-secondary/10 flex items-center justify-center text-secondary">
              <span className="material-symbols-outlined text-[28px]">handyman</span>
            </div>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm flex items-center justify-between">
            <div>
              <p className="text-label-caps text-on-surface-variant mb-1 uppercase">Avg. Downtime</p>
              <h3 className="font-display-lg text-display-lg text-on-tertiary-fixed-variant">{kpis.avgDowntime}</h3>
            </div>
            <div className="w-12 h-12 rounded-full bg-tertiary/10 flex items-center justify-center text-tertiary">
              <span className="material-symbols-outlined text-[28px]">timer</span>
            </div>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm flex items-center justify-between relative overflow-hidden">
            <div className="relative z-10 w-full pr-4">
              <p className="text-label-caps text-on-surface-variant mb-1 uppercase">Shop Capacity</p>
              <h3 className="font-display-lg text-display-lg">{kpis.shopCapacity}%</h3>
              <div className="w-full bg-outline-variant h-1.5 rounded-full mt-2 overflow-hidden">
                <div className={`${kpis.shopCapacity > 80 ? 'bg-error' : 'bg-primary'} h-full rounded-full`} style={{width: `${kpis.shopCapacity}%`}}></div>
              </div>
            </div>
            <div className="w-12 h-12 rounded-full bg-surface-variant flex items-center justify-center text-on-surface-variant relative z-10 shrink-0">
              <span className="material-symbols-outlined text-[28px]">garage</span>
            </div>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-sm w-full md:w-auto">
            <div className="relative flex-1">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]" 
                placeholder="Search maintenance logs..." 
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
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Main Layout Grid: Full Width Table */}
        <div className="space-y-md mb-md">
            <div className="bg-surface rounded-lg border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0 h-full">
              <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
                <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Current Maintenance Records</h2>
                <div className="flex items-center gap-2">
                  <button onClick={() => window.print()} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Print List">
                    <span className="material-symbols-outlined text-[20px]">print</span>
                  </button>
                  <button onClick={() => downloadCSV(records, 'maintenance_export.csv')} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
                    <span className="material-symbols-outlined text-[20px]">download</span>
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto min-h-[300px]">
                <table className="w-full text-left border-collapse min-w-[700px]">
                  <thead>
                    <tr className="bg-surface-container-lowest text-on-surface-variant text-label-caps border-b border-outline-variant">
                      <th className="px-md py-3 font-bold">Vehicle ID</th>
                      <th className="px-md py-3 font-bold">Issue Description</th>
                      <th className="px-md py-3 font-bold">Priority</th>
                      <th className="px-md py-3 font-bold">Technician</th>
                      <th className="px-md py-3 font-bold">Status</th>
                      <th className="px-md py-3 font-bold text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    {loading ? (
                      [...Array(4)].map((_, i) => (
                        <tr key={i} className="animate-pulse">
                          <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                          <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-48"></div></td>
                          <td className="px-md py-3"><div className="h-5 bg-slate-200 rounded-full w-16"></div></td>
                          <td className="px-md py-3"><div className="flex items-center gap-2"><div className="w-6 h-6 rounded-full bg-slate-200"></div><div className="h-4 bg-slate-200 rounded w-20"></div></div></td>
                          <td className="px-md py-3"><div className="h-5 bg-slate-200 rounded-full w-20"></div></td>
                          <td className="px-md py-3 text-right"><div className="h-4 bg-slate-200 rounded w-12 ml-auto"></div></td>
                        </tr>
                      ))
                    ) : paginatedRecords.map(record => (
                      <tr key={record.id} className="hover:bg-surface-container-low transition-colors group">
                        <td className="px-md py-3 font-data-tabular">
                          {record.vehicle?.registration_number || '--'}
                        </td>
                        <td className="px-md py-3 text-body-sm truncate max-w-[200px]" title={record.description}>
                          {record.description}
                        </td>
                        <td className="px-md py-3">
                          {getPriorityChip(record.priority)}
                        </td>
                        <td className="px-md py-3">
                          {record.assigned_technician ? (
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold bg-primary-container text-primary shrink-0">
                                {getInitials(record.assigned_technician)}
                              </div>
                              <div className="flex flex-col min-w-0">
                                <span className="text-body-sm font-bold text-on-surface truncate">{record.assigned_technician}</span>
                                {(() => {
                                  const t = technicianWorkload.find(w => w.name === record.assigned_technician);
                                  const count = t ? t.count : 0;
                                  return (
                                    <span className="text-[11px] text-on-surface-variant">{count}/5 Tasks</span>
                                  );
                                })()}
                              </div>
                            </div>
                          ) : (
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold bg-surface-variant text-on-surface-variant shrink-0">
                                --
                              </div>
                              <div className="flex flex-col min-w-0">
                                <span className="text-body-sm text-on-surface-variant italic">Unassigned</span>
                                <span className="text-[11px] text-on-surface-variant">Awaiting Assignment</span>
                              </div>
                            </div>
                          )}
                        </td>
                        <td className="px-md py-3">
                          {getStatusChip(record.status)}
                        </td>
                        <td className="px-md py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button onClick={() => openModal(record)} className="text-primary hover:bg-primary-container/30 p-1 rounded" title="Edit">
                              <span className="material-symbols-outlined text-[18px]">edit</span>
                            </button>
                            {(record.status === 'Pending' || record.status === 'Approved' || record.status === 'In Progress') && (
                              <button onClick={() => openActionDialog(record, 'status')} className="text-secondary hover:bg-secondary-container/30 p-1 rounded" title="Update Status">
                                <span className="material-symbols-outlined text-[18px]">update</span>
                              </button>
                            )}
                            {record.status === 'In Progress' && (
                              <button onClick={() => openActionDialog(record, 'complete')} className="text-tertiary hover:bg-tertiary-container/30 p-1 rounded" title="Complete">
                                <span className="material-symbols-outlined text-[18px]">check_circle</span>
                              </button>
                            )}
                            <button onClick={() => openDeleteDialog(record)} className="text-error hover:bg-error-container/30 p-1 rounded" title="Delete">
                              <span className="material-symbols-outlined text-[18px]">delete</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {paginatedRecords.length === 0 && !loading && (
                      <tr>
                        <td colSpan="6" className="text-center py-12 text-on-surface-variant">
                          <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">build</span>
                          <p>No maintenance records found.</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div className="p-md bg-surface-container border-t border-outline-variant flex items-center justify-between text-body-sm text-on-surface-variant mt-auto">
                <span>Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} records</span>
                <div className="flex gap-1">
                  <button 
                    onClick={() => handlePageChange('prev')} disabled={currentPage === 1}
                    className="p-1 px-2 border border-outline-variant rounded hover:bg-surface disabled:opacity-50 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px]">chevron_left</span>
                  </button>
                  <button className="p-1 px-3 border border-outline-variant bg-primary text-on-primary rounded font-bold">{currentPage}</button>
                  <button 
                    onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0}
                    className="p-1 px-2 border border-outline-variant rounded hover:bg-surface disabled:opacity-50 transition-colors"
                  >
                    <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                  </button>
                </div>
              </div>
            </div>
          </div>


        {/* Footer / Secondary Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-md pb-lg">
          
          {/* Left Column (8 cols): Cards */}
          <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-3 gap-md">
          
          {/* Shop Efficiency Card */}
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm col-span-1 min-h-[220px]">
            <div className="flex items-center justify-between mb-md">
              <h3 className="font-title-sm text-title-sm">Technician Workload</h3>
              <div className="relative">
                <button onClick={() => setIsTechMenuOpen(!isTechMenuOpen)} className="p-1 rounded-full hover:bg-surface-container transition-colors focus:outline-none">
                  <span className="material-symbols-outlined text-on-surface-variant text-[20px]">more_vert</span>
                </button>
                {isTechMenuOpen && (
                  <div className="absolute right-0 top-full mt-1 w-48 bg-surface border border-outline-variant rounded-lg shadow-lg py-1 z-20">
                    <button onClick={() => { setIsTechMenuOpen(false); navigate('/maintenance/technicians'); }} className="w-full text-left px-4 py-2 hover:bg-surface-container-low text-body-sm text-on-surface transition-colors">Manage Technicians</button>
                    <button onClick={() => { setIsTechMenuOpen(false); navigate('/maintenance/tasks'); }} className="w-full text-left px-4 py-2 hover:bg-surface-container-low text-body-sm text-on-surface transition-colors">View All Tasks</button>
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-md">
              {technicianWorkload.length > 0 ? (
                technicianWorkload.map(tech => (
                  <div key={tech.name} className="space-y-2">
                    <div className="flex justify-between items-center text-body-sm font-bold">
                      <div className="flex flex-col">
                        <span className="text-on-surface">{tech.name}</span>
                        <span className="text-[11px] font-normal text-on-surface-variant">{tech.count}/{tech.maxCapacity} Tasks</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-primary">{Math.round(tech.pct)}%</span>
                        <span className={`text-[11px] font-bold ${tech.pct >= 100 ? 'text-error' : tech.pct >= 80 ? 'text-tertiary' : 'text-secondary'}`}>
                          {tech.pct >= 100 ? 'Busy' : 'Available'}
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                      <div className={`${tech.colorClass} h-full transition-all duration-500`} style={{width: `${tech.pct}%`}}></div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-body-sm text-on-surface-variant">No active tasks assigned.</p>
              )}
            </div>
          </div>

          {/* Inventory Alert Card */}
          <div className="bg-tertiary-container/10 p-md rounded-lg border border-tertiary/20 shadow-sm col-span-1 flex flex-col justify-between min-h-[220px]">
            <div>
              <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mb-sm">
                <span className="material-symbols-outlined text-tertiary" style={{fontVariationSettings: "'FILL' 1"}}>inventory_2</span>
                <h3 className="font-title-sm text-title-sm text-on-tertiary-fixed">Parts Alert</h3>
              </div>
              {criticalPart ? (
                <p className="text-body-sm text-on-tertiary-fixed-variant">Critical shortage detected for <span className="font-bold">{criticalPart.name} (Ref: {criticalPart.part_number})</span>. {criticalPart.quantity_reserved} units reserved.</p>
              ) : (
                <p className="text-body-sm text-on-tertiary-fixed-variant">No critical parts shortage at the moment. All stock levels are sufficient.</p>
              )}
            </div>
            <button 
              onClick={() => navigate('/inventory/restock')}
              className="mt-md w-full py-2 rounded-lg font-bold text-body-sm transition-all flex items-center justify-center gap-2 bg-tertiary text-on-tertiary hover:opacity-90"
            >
              <span className="material-symbols-outlined text-[18px]">inventory_2</span>
              Restock Inventory
            </button>
          </div>

          {/* Visual Quick Insight */}
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm col-span-1 relative overflow-hidden flex flex-col min-w-0 items-center justify-center text-center min-h-[220px]">
            <div className="relative w-32 h-32 mb-sm">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-surface-container" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" strokeWidth="12"></circle>
                <circle className="text-primary" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" strokeDasharray="364.4" strokeDashoffset="91.1" strokeWidth="12"></circle>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-display-lg font-display-lg leading-none">75%</span>
                <span className="text-[10px] uppercase font-bold text-on-surface-variant">Up-time</span>
              </div>
            </div>
            <h4 className="text-body-md font-bold">Fleet Health Score</h4>
            <p className="text-[12px] text-on-surface-variant">Optimized for operational scale</p>
          </div>

        </div>

          {/* Right Column (4 cols): Timeline */}
          <div className="lg:col-span-4 space-y-md">
            <div className="bg-surface rounded-lg border border-outline-variant shadow-sm h-full flex flex-col">
              <div className="p-md border-b border-outline-variant bg-surface-container-low flex items-center justify-between">
                <h2 className="font-title-sm text-title-sm">Scheduled Service</h2>
                <Link to="/maintenance/scheduler" className="text-body-sm text-primary font-bold cursor-pointer hover:underline">View Calendar</Link>
              </div>
              <div className="p-md flex-1 relative overflow-hidden">
                <div className="absolute left-[39px] top-md bottom-md w-0.5 bg-outline-variant"></div>
                
                <div className="space-y-xl relative">
                  {scheduledTimeline.length > 0 ? (
                    scheduledTimeline.map((item, idx) => (
                      <div key={item.id} className="flex gap-md">
                        <div className="relative z-10 w-12 flex flex-col items-center">
                          <div className={`w-3 h-3 rounded-full mt-1 ${idx === 0 ? 'bg-primary ring-4 ring-primary/20' : 'bg-outline-variant ring-4 ring-surface-variant'}`}></div>
                        </div>
                        <div className="flex-1 pb-4">
                          <p className="text-[12px] font-bold text-primary mb-1 uppercase tracking-wide">{item.dayLabel}</p>
                          <h4 className="font-data-tabular text-body-md font-bold text-on-surface">{item.vehicle?.registration_number}</h4>
                          <p className="text-body-sm text-on-surface-variant">{item.maintenance_type}</p>
                          <div className="flex items-center gap-1 mt-1 text-on-surface-variant">
                            <span className="material-symbols-outlined text-[14px]">schedule</span>
                            <span className="text-[12px] font-bold">{item.timeLabel}</span>
                          </div>
                          {item.priority === 'Critical' && (
                            <div className="mt-2 bg-error-container/30 p-2 rounded border border-error/10 flex items-center gap-2 w-max">
                              <span className="material-symbols-outlined text-error text-[18px]">warning</span>
                              <span className="text-[11px] font-medium text-error">High Priority Flag</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-on-surface-variant">
                      <p>No upcoming schedules.</p>
                    </div>
                  )}
                </div>

              </div>
            </div>
          </div>
          
        </div>
      </div>

      {/* Modals & Dialogs */}
      <MaintenanceModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRecord}
        maintenance={editingRecord}
        isSaving={isSaving}
      />

      <MaintenanceActionDialog
        isOpen={isActionDialogOpen}
        onClose={() => setIsActionDialogOpen(false)}
        onConfirm={handleActionConfirm}
        actionType={actionType}
        maintenance={selectedRecord}
        isProcessing={isProcessing}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteRecord}
        title="Delete Record"
        message={`Are you sure you want to permanently delete maintenance record ${recordToDelete?.maintenance_number}?`}
        isDeleting={isDeleting}
      />

    </div>
  );
};

export default Maintenance;
