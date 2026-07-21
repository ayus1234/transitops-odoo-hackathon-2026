import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { downloadCSV } from '../utils/exportUtils';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import DriverModal from './drivers/DriverModal';
import ConfirmDeleteDialog from '../components/ui/ConfirmDeleteDialog';

const Drivers = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Delete Dialog states
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [driverToDelete, setDriverToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);

  // Pagination state
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchDrivers = useCallback(async () => {
    const response = await api.get('/drivers?page_size=100');
    return response.data.data || [];
  }, []);

  const { data: driversData, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchDrivers,
    [],
    'medium'
  );

  const drivers = driversData || [];

  useEffect(() => {
    if (location.state?.openModal) {
      openCreateModal();
      window.history.replaceState({}, document.title);
    } else if (location.state?.filter) {
      setSearchTerm(location.state.filter);
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Compute KPIs from local data
  const kpis = useMemo(() => {
    const total = drivers.length;
    const active = drivers.filter(d => d.status === 'On Trip').length;
    
    // Additional metrics for bottom cards
    const expiringSoon = drivers.filter(d => {
      if (!d.license_expiry_date) return false;
      const expiry = new Date(d.license_expiry_date);
      const today = new Date();
      const diffTime = Math.abs(expiry - today);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return expiry > today && diffDays <= 30;
    }).length;

    const complianceRate = total > 0 
      ? Math.round((drivers.filter(d => d.status !== 'Suspended').length / total) * 100) 
      : 100;
      
    const totalScore = drivers.reduce((acc, d) => acc + (Number(d.safety_score) || 0), 0);
    const avgSafetyScore = total > 0 ? Math.round(totalScore / total) : 0;

    return { total, active, expiringSoon, complianceRate, avgSafetyScore };
  }, [drivers]);

  // Search and Filter logic
  const filteredDrivers = useMemo(() => {
    return drivers.filter(d => {
      const matchesStatus = statusFilter === 'All' || d.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      // Search by user full_name, license_number, or emergency_contact
      const name = (d.user?.full_name || '').toLowerCase();
      const license = (d.license_number || '').toLowerCase();
      const phone = (d.emergency_contact || '').toLowerCase();
      
      const matchesSearch = name.includes(searchLower) || license.includes(searchLower) || phone.includes(searchLower);
      
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

  const openCreateModal = () => {
    setEditingDriver(null);
    setIsModalOpen(true);
  };

  const openEditModal = async (driverId) => {
    try {
      setIsFetchingDetails(true);
      const response = await api.get(`/drivers/${driverId}`);
      setEditingDriver(response.data);
      setIsModalOpen(true);
    } catch {
      alert("Failed to fetch driver details.");
    } finally {
      setIsFetchingDetails(false);
    }
  };

  const handleSaveDriver = async (payload) => {
    setIsSaving(true);
    try {
      if (editingDriver) {
        await api.put(`/drivers/${editingDriver.id}`, payload);
      } else {
        await api.post('/drivers', payload);
      }
      setIsModalOpen(false);
      silentRefresh();
    } finally {
      setIsSaving(false);
    }
  };

  const openDeleteDialog = (driver) => {
    setDriverToDelete(driver);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteDriver = async () => {
    if (!driverToDelete) return;
    setIsDeleting(true);
    try {
      await api.delete(`/drivers/${driverToDelete.id}`);
      setIsDeleteDialogOpen(false);
      setDriverToDelete(null);
      silentRefresh();
    } catch {
      alert("Failed to delete driver.");
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusChip = (status) => {
    switch(status) {
      case 'Available':
        return (
          <span className="status-chip bg-secondary-container/30 text-secondary">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary mr-1.5"></span> Available
          </span>
        );
      case 'On Trip':
        return (
          <span className="status-chip bg-primary-container/20 text-primary">
            <span className="w-1.5 h-1.5 rounded-full bg-primary mr-1.5"></span> On Trip
          </span>
        );
      case 'Suspended':
        return (
          <span className="status-chip bg-error-container/50 text-error">
            <span className="w-1.5 h-1.5 rounded-full bg-error mr-1.5"></span> Suspended
          </span>
        );
      case 'Off Duty':
        return (
          <span className="status-chip bg-surface-container-high text-outline">
            <span className="w-1.5 h-1.5 rounded-full bg-outline mr-1.5"></span> Off Duty
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

  const isExpired = (dateStr) => {
    if (!dateStr) return false;
    return new Date(dateStr) < new Date();
  };

  const getScoreColor = (score) => {
    const num = Number(score) || 0;
    if (num >= 85) return 'text-secondary bg-secondary';
    if (num >= 65) return 'text-primary bg-primary';
    return 'text-error bg-error';
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      {/* Dynamic Content Area */}
      <section className="flex-1 overflow-y-auto p-3 md:p-lg space-y-lg custom-scrollbar min-w-0">
        
        {/* Top Header/Toolbar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate(-1)} 
              className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors text-on-surface"
              title="Go Back"
            >
              <span className="material-symbols-outlined text-[24px]">arrow_back</span>
            </button>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Driver Management</h1>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage and monitor your fleet workforce</p>
            </div>
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
              onClick={openCreateModal}
              className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm"
            >
              <span className="material-symbols-outlined">person_add</span>
              <span className="font-body-md text-body-md">Add Driver</span>
            </button>
          </div>
        </div>
          <div className="grid grid-cols-2 gap-xs md:gap-md w-full md:w-auto">
            <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm flex items-center gap-2 md:gap-4 flex-1 md:min-w-[180px]">
              <div className="w-10 h-10 rounded-lg bg-secondary-container/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-secondary">group</span>
              </div>
              <div>
                <p className="text-[11px] font-bold text-outline uppercase tracking-wider">Total Drivers</p>
                <p className="text-xl font-bold">{kpis.total}</p>
              </div>
            </div>
            <div className="bg-surface p-4 rounded-xl border border-outline-variant shadow-sm flex items-center gap-2 md:gap-4 flex-1 md:min-w-[180px]">
              <div className="w-10 h-10 rounded-lg bg-primary-container/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary">local_shipping</span>
              </div>
              <div>
                <p className="text-[11px] font-bold text-outline uppercase tracking-wider">Active Today</p>
                <p className="text-xl font-bold">{kpis.active}</p>
              </div>
            </div>
            </div>

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
            <span className="material-symbols-outlined">error</span>
            <p className="flex-1 font-bold">{error}</p>
            <button onClick={refresh} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
          </div>
        )}

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-sm w-full md:w-auto">
            <div className="relative flex-1">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]" 
                placeholder="Search drivers, license or phone..." 
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
                <option value="Available">Available</option>
                <option value="On Trip">On Trip</option>
                <option value="Suspended">Suspended</option>
                <option value="Off Duty">Off Duty</option>
              </select>
            </div>
          </div>
        </div>

        {/* Main Enterprise Table Container */}
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Drivers Directory</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => window.print()} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Print List">
                <span className="material-symbols-outlined text-[20px]">print</span>
              </button>
              <button onClick={() => downloadCSV(drivers, 'drivers_export.csv')} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
                <span className="material-symbols-outlined text-[20px]">download</span>
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead className="bg-surface-container-low sticky top-0 z-10">
                <tr>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">
                    <div className="flex items-center gap-2">Driver</div>
                  </th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">License Details</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-center">Expiry</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Phone</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-center">Safety Score</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant">Status</th>
                  <th className="px-md py-4 font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider border-b border-outline-variant text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  // Skeletons
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="hover:bg-surface-container-low transition-colors animate-pulse">
                      <td className="px-md py-4"><div className="flex gap-3 items-center"><div className="w-10 h-10 rounded-full bg-slate-200"></div><div className="h-4 bg-slate-200 rounded w-32"></div></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-24 mb-1"></div><div className="h-3 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-4 text-center"><div className="h-4 bg-slate-200 rounded w-20 mx-auto"></div></td>
                      <td className="px-md py-4"><div className="h-4 bg-slate-200 rounded w-28"></div></td>
                      <td className="px-md py-4"><div className="flex flex-col items-center gap-1"><div className="h-4 bg-slate-200 rounded w-6"></div><div className="w-16 h-1.5 bg-slate-200 rounded-full"></div></div></td>
                      <td className="px-md py-4"><div className="h-6 bg-slate-200 rounded-full w-24"></div></td>
                      <td className="px-md py-4 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedDrivers.map(driver => {
                  const scoreColors = getScoreColor(driver.safety_score);
                  const expired = isExpired(driver.license_expiry_date);
                  
                  const getInitials = (name) => {
                    if (!name || name === 'Unknown') return 'DR';
                    const parts = name.trim().split(/\s+/);
                    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
                    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
                  };
                  
                  return (
                    <tr key={driver.id} className="hover:bg-surface-container-lowest bg-white transition-colors group">
                      <td className="px-md py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs bg-primary-fixed text-primary border border-primary/20">
                            {getInitials(driver.user?.full_name)}
                          </div>
                          <div>
                            <p className="font-data-tabular text-data-tabular text-on-surface font-semibold">{driver.user?.full_name || 'Unknown'}</p>
                            <p className="text-[11px] text-outline">ID: {driver.id.split('-')[0].toUpperCase()}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-md py-4">
                        <p className="font-data-tabular text-data-tabular text-on-surface">{driver.license_category}</p>
                        <p className="text-xs text-on-surface-variant">#{driver.license_number}</p>
                      </td>
                      <td className="px-md py-4 text-center">
                        <span className={`font-data-tabular text-data-tabular ${expired ? 'text-error font-bold' : ''}`}>
                          {formatDate(driver.license_expiry_date)}
                        </span>
                      </td>
                      <td className="px-md py-4">
                        <span className="font-data-tabular text-data-tabular">{driver.emergency_contact || 'N/A'}</span>
                      </td>
                      <td className="px-md py-4">
                        <div className="flex flex-col items-center gap-1">
                          <span className={`font-data-tabular text-data-tabular font-bold ${scoreColors.split(' ')[0]}`}>{driver.safety_score || '0'}</span>
                          <div className="w-16 h-1.5 bg-surface-container rounded-full overflow-hidden">
                            <div className={`h-full ${scoreColors.split(' ')[1]}`} style={{ width: `${driver.safety_score || 0}%` }}></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-md py-4">
                        {getStatusChip(driver.status)}
                      </td>
                      <td className="px-md py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => openEditModal(driver.id)}
                            className="p-1 hover:bg-surface-container rounded text-outline hover:text-primary transition-colors"
                            title="Edit Driver"
                          >
                            <span className="material-symbols-outlined text-[20px]">edit</span>
                          </button>
                          <button 
                            onClick={() => openDeleteDialog(driver)}
                            className="p-1 hover:bg-error-container/50 rounded text-outline hover:text-error transition-colors"
                            title="Delete Driver"
                          >
                            <span className="material-symbols-outlined text-[20px]">delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {paginatedDrivers.length === 0 && !loading && (
                  <tr>
                    <td colSpan="7" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">person_off</span>
                      <p>No drivers found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Pagination Footer */}
          <div className="px-md py-3 bg-surface border-t border-outline-variant flex items-center justify-between">
            <div className="flex items-center gap-2">
              <p className="text-xs text-on-surface-variant">
                Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0} to {Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} entries
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

        {/* Contextual Actions / Bottom Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
          <div className="bg-surface-container-low p-md rounded-xl border border-outline-variant flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-error/10 p-2 rounded-lg">
              <span className="material-symbols-outlined text-error">warning</span>
            </div>
            <div>
              <p className="text-sm font-bold text-on-surface">Licences Expiring Soon</p>
              <p className="text-xs text-on-surface-variant">{kpis.expiringSoon} driver(s) need renewal within 30 days.</p>
            </div>
            <button onClick={() => navigate('/drivers/license-compliance')} className="ml-auto text-primary font-bold text-xs hover:underline">View</button>
          </div>
          <div className="bg-surface-container-low p-md rounded-xl border border-outline-variant flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-secondary/10 p-2 rounded-lg">
              <span className="material-symbols-outlined text-secondary">verified</span>
            </div>
            <div>
              <p className="text-sm font-bold text-on-surface">Compliance Rate</p>
              <p className="text-xs text-on-surface-variant">Current fleet compliance is at {kpis.complianceRate}%.</p>
            </div>
            <button onClick={() => navigate('/reports/fleet-compliance')} className="ml-auto text-primary font-bold text-xs hover:underline">Report</button>
          </div>
          <div className="bg-surface-container-low p-md rounded-xl border border-outline-variant flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="bg-primary/10 p-2 rounded-lg">
              <span className="material-symbols-outlined text-primary">psychology</span>
            </div>
            <div>
              <p className="text-sm font-bold text-on-surface">Safety Insights</p>
              <p className="text-xs text-on-surface-variant">Average fleet safety score: {kpis.avgSafetyScore}/100.</p>
            </div>
            <button onClick={() => navigate('/drivers/safety-insights')} className="ml-auto text-primary font-bold text-xs hover:underline">Details</button>
          </div>
        </div>
      </section>

      {/* Modals */}
      <DriverModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveDriver}
        driver={editingDriver}
        isSaving={isSaving}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteDriver}
        title="Suspend / Delete Driver"
        message={`Are you sure you want to permanently remove ${driverToDelete?.user?.full_name}? This action cannot be undone.`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default Drivers;
