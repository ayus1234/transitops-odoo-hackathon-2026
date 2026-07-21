import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadCSV } from '../utils/exportUtils';
import api from '../services/api';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import VehicleModal from './vehicles/VehicleModal';
import ConfirmDeleteDialog from '../components/ui/ConfirmDeleteDialog';
import { useToast } from '../contexts/ToastContext';

const Vehicles = () => {
  const location = useLocation();
  
  // Search & Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Delete Dialog states
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [vehicleToDelete, setVehicleToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isFetchingDetails, setIsFetchingDetails] = useState(false);

  // Pagination state
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchVehicles = useCallback(async () => {
    const response = await api.get('/vehicles');
    return response.data.data || [];
  }, []);

  const { data: vehiclesData, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchVehicles,
    [],
    'medium'
  );
  
  const vehicles = vehiclesData || [];

  useEffect(() => {
    if (location.state?.openModal) {
      openCreateModal();
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // Compute KPIs from local data
  const kpis = useMemo(() => {
    const total = vehicles.length;
    const available = vehicles.filter(v => v.status === 'Available').length;
    const onTrip = vehicles.filter(v => v.status === 'On Trip').length;
    const inShop = vehicles.filter(v => v.status === 'In Shop').length;
    return { total, available, onTrip, inShop };
  }, [vehicles]);

  // Search and Filter logic
  const filteredVehicles = useMemo(() => {
    return vehicles.filter(v => {
      const matchesStatus = statusFilter === 'All' || v.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        v.registration_number.toLowerCase().includes(searchLower) ||
        v.vehicle_name.toLowerCase().includes(searchLower) ||
        v.vehicle_type.toLowerCase().includes(searchLower);
      
      return matchesStatus && matchesSearch;
    });
  }, [vehicles, searchTerm, statusFilter]);

  // Pagination logic
  const totalItems = filteredVehicles.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedVehicles = filteredVehicles.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const openCreateModal = () => {
    setEditingVehicle(null);
    setIsModalOpen(true);
  };

  const openEditModal = async (vehicleId) => {
    try {
      setIsFetchingDetails(true);
      // Fetch full details before editing
      const response = await api.get(`/vehicles/${vehicleId}`);
      // VehicleResponse is returned directly, not wrapped in data
      setEditingVehicle(response.data);
      setIsModalOpen(true);
    } catch (err) {
      console.error('Error fetching vehicle details:', err);
      alert("Failed to fetch vehicle details.");
    } finally {
      setIsFetchingDetails(false);
    }
  };

  const handleSaveVehicle = async (payload) => {
    setIsSaving(true);
    try {
      if (editingVehicle) {
        await api.put(`/vehicles/${editingVehicle.id}`, payload);
      } else {
        await api.post('/vehicles', payload);
      }
      setIsModalOpen(false);
      silentRefresh();
    } finally {
      setIsSaving(false);
    }
  };

  const openDeleteDialog = (vehicle) => {
    setVehicleToDelete(vehicle);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteVehicle = async () => {
    if (!vehicleToDelete) return;
    setIsDeleting(true);
    try {
      await api.delete(`/vehicles/${vehicleToDelete.id}`);
      setIsDeleteDialogOpen(false);
      setVehicleToDelete(null);
      silentRefresh();
    } catch {
      alert("Failed to delete vehicle.");
    } finally {
      setIsDeleting(false);
    }
  };

  // Helper for Status Chips mapping exact HTML styling
  const getStatusChip = (status) => {
    switch(status) {
      case 'Available':
        return (
          <span className="bg-secondary-container/30 text-secondary px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span> Available
          </span>
        );
      case 'On Trip':
        return (
          <span className="bg-primary-container/20 text-primary px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-primary"></span> On Trip
          </span>
        );
      case 'In Shop':
        return (
          <span className="bg-tertiary-fixed/30 text-tertiary px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span> In Shop
          </span>
        );
      default:
        return (
          <span className="bg-surface-container-high text-outline px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-outline"></span> {status}
          </span>
        );
    }
  };

  return (
    <div className="p-3 md:p-gutter flex flex-col gap-gutter flex-1 min-w-0">
      {/* Top Header/Toolbar extracted from the HTML that I removed from GenericList */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full px-md mt-4 gap-4">
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Vehicle Registry</h1>
        <div className="flex items-center gap-md">
          <button 
            onClick={refresh} 
            disabled={loading || isSyncing}
            className="p-2 rounded-full hover:bg-surface-container-high transition-all text-on-surface-variant flex items-center justify-center disabled:opacity-50"
            title="Refresh"
          >
            <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
          </button>
          <button 
            onClick={openCreateModal}
            className="bg-primary text-on-primary px-4 py-2 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto shadow-sm"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Add Vehicle
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

      {/* KPI Row exactly matching HTML */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-xs md:gap-md mx-md">
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-sm">
            <p className="text-label-caps text-outline font-bold">TOTAL FLEET</p>
            <span className="material-symbols-outlined text-primary">local_shipping</span>
          </div>
          <h2 className="text-display-lg font-display-lg text-on-surface">{kpis.total}</h2>
          <p className="text-body-sm text-secondary font-medium mt-xs">Active Registry</p>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-sm">
            <p className="text-label-caps text-outline font-bold">AVAILABLE</p>
            <div className="w-2 h-2 rounded-full bg-secondary"></div>
          </div>
          <h2 className="text-display-lg font-display-lg text-on-surface">{kpis.available}</h2>
          <p className="text-body-sm text-outline font-medium mt-xs">{kpis.total > 0 ? Math.round((kpis.available/kpis.total)*100) : 0}% of fleet</p>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-sm">
            <p className="text-label-caps text-outline font-bold">ON TRIP</p>
            <div className="w-2 h-2 rounded-full bg-primary"></div>
          </div>
          <h2 className="text-display-lg font-display-lg text-on-surface">{kpis.onTrip}</h2>
          <p className="text-body-sm text-primary font-medium mt-xs">Currently dispatched</p>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)]">
          <div className="flex justify-between items-start mb-sm">
            <p className="text-label-caps text-outline font-bold">IN SHOP</p>
            <div className="w-2 h-2 rounded-full bg-tertiary"></div>
          </div>
          <h2 className="text-display-lg font-display-lg text-on-surface">{kpis.inShop}</h2>
          <p className="text-body-sm text-tertiary font-medium mt-xs">Maintenance required</p>
        </div>
      </div>

      {/* Action & Filter Bar */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-md mx-md">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-sm w-full md:w-auto">
          <div className="relative flex-1">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
            <input 
              type="text" 
              placeholder="Search vehicles..." 
              value={searchTerm}
              onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all focus:scale-[1.01]"
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
            <option value="In Shop">In Shop</option>
          </select>
          </div>
          <div className="hidden md:block h-6 w-[1px] bg-outline-variant mx-2"></div>
          <p className="hidden md:block text-body-sm text-outline">
            Showing <span className="font-bold text-on-surface">{totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)}</span> of {totalItems}
          </p>
        </div>
      </div>

      {/* Enterprise Data Table */}
      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col mx-1 md:mx-md mb-md min-w-0">
        <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
          <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Vehicles Directory</h2>
          <div className="flex items-center gap-2">
            <button onClick={() => window.print()} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Print List">
              <span className="material-symbols-outlined text-[20px]">print</span>
            </button>
            <button onClick={() => downloadCSV(vehicles, 'vehicles_export.csv')} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface-container text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                <th className="px-md py-3.5">Reg. Number</th>
                <th className="px-md py-3.5">Vehicle Model</th>
                <th className="px-md py-3.5">Type</th>
                <th className="px-md py-3.5">Capacity (kg)</th>
                <th className="px-md py-3.5">Odometer (km)</th>
                <th className="px-md py-3.5">Status</th>
                <th className="px-md py-3.5 text-right w-24">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                // Skeletons
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-outline-variant animate-pulse">
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-6 bg-slate-200 rounded-full w-24"></div></td>
                    <td className="px-md py-3.5 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                  </tr>
                ))
              ) : paginatedVehicles.map(vehicle => (
                <tr key={vehicle.id} className="border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                  <td className="px-md py-3.5 font-bold text-primary font-data-tabular">{vehicle.registration_number}</td>
                  <td className="px-md py-3.5">
                    <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
                      <div className="w-8 h-8 rounded bg-surface-container-highest flex items-center justify-center text-outline font-bold text-xs shrink-0">
                        {vehicle.vehicle_name.substring(0,2).toUpperCase()}
                      </div>
                      <span className="truncate max-w-[200px]">{vehicle.vehicle_name}</span>
                    </div>
                  </td>
                  <td className="px-md py-3.5">{vehicle.vehicle_type}</td>
                  <td className="px-md py-3.5 font-data-tabular">{Number(vehicle.capacity_kg).toLocaleString()}</td>
                  <td className="px-md py-3.5 font-data-tabular">{Number(vehicle.current_odometer_km).toLocaleString()}</td>
                  <td className="px-md py-3.5">
                    {getStatusChip(vehicle.status)}
                  </td>
                  <td className="px-md py-3.5 text-right relative">
                    <div className="flex justify-end gap-1">
                      <button 
                        onClick={() => openEditModal(vehicle.id)}
                        className="p-1.5 rounded hover:bg-primary-container text-outline hover:text-primary transition-all"
                        title="Edit Vehicle"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                      <button 
                        onClick={() => openDeleteDialog(vehicle)}
                        className="p-1.5 rounded hover:bg-error-container text-outline hover:text-error transition-all"
                        title="Delete Vehicle"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {paginatedVehicles.length === 0 && !loading && (
                <tr>
                  <td colSpan="8" className="text-center py-12 text-on-surface-variant flex flex-col items-center">
                    <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">local_shipping</span>
                    <p>No vehicles found matching your criteria.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Footer / Pagination */}
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
              <button 
                onClick={() => handlePageChange('prev')}
                disabled={currentPage === 1}
                className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button 
                onClick={() => handlePageChange('next')}
                disabled={currentPage === totalPages || totalPages === 0}
                className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <VehicleModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveVehicle}
        vehicle={editingVehicle}
        isSaving={isSaving}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteVehicle}
        title="Delete Vehicle"
        message={`Are you sure you want to delete ${vehicleToDelete?.registration_number}? This action cannot be undone and will affect associated trips.`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default Vehicles;
