import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';

const InventoryHistory = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Pagination
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchHistoryData = useCallback(async () => {
    const res = await api.get('/inventory/history?page_size=100'); // fetch all for client side filtering
    return res.data.data || [];
  }, []);

  const { data, loading, isSyncing, refresh } = useDataSync(
    fetchHistoryData,
    [],
    'medium'
  );

  const historyLogs = data || [];

  // Compute mock KPIs based on logs since there isn't a dedicated /history/summary endpoint
  const kpis = useMemo(() => {
    const totalRestocks = historyLogs.filter(l => l.type === 'Restock').length;
    const inventoryUpdates = historyLogs.filter(l => l.type === 'Adjustment').length;
    const vehiclesReleased = historyLogs.filter(l => l.type === 'Release').length;
    return {
      totalRestocks,
      inventoryUpdates,
      vehiclesReleased,
      procurementCompleted: totalRestocks, // Approximation for UI
      deliveredOrders: totalRestocks
    };
  }, [historyLogs]);

  // Filter & Search
  const filteredLogs = useMemo(() => {
    return historyLogs.filter(log => {
      const matchesStatus = statusFilter === 'All' || log.type === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = log.part?.name?.toLowerCase().includes(searchLower) ||
                            log.part?.part_number?.toLowerCase().includes(searchLower) ||
                            log.reference_id?.toLowerCase().includes(searchLower) ||
                            (log.notes && log.notes.toLowerCase().includes(searchLower));
      return matchesStatus && matchesSearch;
    });
  }, [historyLogs, searchTerm, statusFilter]);

  const totalItems = filteredLogs.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedLogs = filteredLogs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getActionChip = (action) => {
    switch (action) {
      case 'Restock': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/20 text-primary border border-primary/20 uppercase">RESTOCK</span>;
      case 'Release': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/50 text-secondary border border-secondary/30 uppercase">RELEASE</span>;
      case 'Reserved': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">RESERVED</span>;
      case 'Adjustment': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">ADJUST</span>;
      default: return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{action}</span>;
    }
  };

  const logColumns = [
    { key: 'created_at', label: 'Date', format: (val) => new Date(val).toLocaleDateString() },
    { key: 'type', label: 'Action' },
    { key: 'part', label: 'Part Name', format: (val) => val?.name || '--' },
    { key: 'quantity_changed', label: 'Qty Change', format: (val) => val > 0 ? `+${val}` : val },
    { key: 'new_quantity', label: 'New Total' },
    { key: 'reference_id', label: 'Ref ID / Vehicle', format: (val) => val || '--' },
    { key: 'user', label: 'User', format: (val) => val ? `${val.first_name} ${val.last_name}` : 'System' },
  ];

  const handleExport = (type) => {
    if (type === 'csv') downloadCSV(filteredLogs, 'inventory_history.csv', logColumns);
    else if (type === 'pdf') downloadPDF(filteredLogs, 'inventory_history.pdf', 'Inventory Audit Ledger', logColumns);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <div className="p-3 md:p-lg space-y-lg flex-1 overflow-y-auto custom-scrollbar min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Inventory History</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Audit log of all stock movements, restocks, and deductions</p>
          </div>
          <div className="flex items-center gap-md">
            <button onClick={refresh} disabled={loading || isSyncing} className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50">
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-5 gap-md">
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Total Restocks</p>
            <h3 className="font-display-sm text-display-sm text-primary">{kpis.totalRestocks}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Inventory Updates</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{kpis.inventoryUpdates}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Vehicles Released</p>
            <h3 className="font-display-sm text-display-sm text-secondary">{kpis.vehiclesReleased}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Procurement Completed</p>
            <h3 className="font-display-sm text-display-sm text-tertiary">{kpis.procurementCompleted}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Delivered Orders</p>
            <h3 className="font-display-sm text-display-sm text-[#4f378b]">{kpis.deliveredOrders}</h3>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <div className="relative">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all" 
                placeholder="Search history..." 
                type="text"
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              />
            </div>
            <div className="flex items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant h-10">
              <span className="material-symbols-outlined text-[18px] text-outline">filter_list</span>
              <select 
                value={statusFilter}
                onChange={(e) => {setStatusFilter(e.target.value); setCurrentPage(1);}}
                className="bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
              >
                <option value="All">All Actions</option>
                <option value="Restock">RESTOCK</option>
                <option value="Release">RELEASE</option>
                <option value="Reserved">RESERVED</option>
                <option value="Adjustment">ADJUST</option>
              </select>
            </div>
          </div>
        </div>

        {/* History Table */}
        <div className="bg-surface rounded-lg border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Audit Ledger</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => handleExport('csv')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export CSV"><span className="material-symbols-outlined text-[20px]">csv</span></button>
              <button onClick={() => handleExport('pdf')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export PDF"><span className="material-symbols-outlined text-[20px]">picture_as_pdf</span></button>
            </div>
          </div>
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="bg-surface-container-lowest text-on-surface-variant text-label-caps border-b border-outline-variant">
                  <th className="px-md py-3 font-bold">Date & Time</th>
                  <th className="px-md py-3 font-bold">Action</th>
                  <th className="px-md py-3 font-bold">Part Name</th>
                  <th className="px-md py-3 font-bold">Qty Change</th>
                  <th className="px-md py-3 font-bold">New Total</th>
                  <th className="px-md py-3 font-bold">Reference Type</th>
                  <th className="px-md py-3 font-bold">Ref ID / Vehicle</th>
                  <th className="px-md py-3 font-bold">User</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan="8" className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-full"></div></td>
                    </tr>
                  ))
                ) : paginatedLogs.map(log => (
                  <tr key={log.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-md py-3 text-[12px] font-data-tabular">
                      {new Date(log.created_at).toLocaleDateString()} <br/>
                      <span className="text-on-surface-variant">{new Date(log.created_at).toLocaleTimeString()}</span>
                    </td>
                    <td className="px-md py-3">{getActionChip(log.type)}</td>
                    <td className="px-md py-3 text-body-sm font-bold">{log.part?.name}</td>
                    <td className={`px-md py-3 font-data-tabular font-bold ${log.quantity_changed > 0 ? 'text-primary' : log.quantity_changed < 0 ? 'text-error' : 'text-on-surface-variant'}`}>
                      {log.quantity_changed > 0 ? '+' : ''}{log.quantity_changed}
                    </td>
                    <td className="px-md py-3 font-data-tabular font-bold">{log.new_quantity}</td>
                    <td className="px-md py-3 text-[12px]">
                      {log.reference_id?.startsWith('PO') ? 'Procurement' : 
                       log.reference_id?.startsWith('MAINT') ? 'Maintenance' : 
                       log.reference_id?.startsWith('REF') ? 'System Update' : 
                       log.type === 'Restock' ? 'Restock' : 'Manual'}
                    </td>
                    <td className="px-md py-3 text-[12px] font-data-tabular truncate max-w-[120px]" title={log.reference_id}>
                      {log.reference_id || '--'}
                    </td>
                    <td className="px-md py-3 flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold bg-outline-variant text-on-surface-variant">
                        {log.user ? (log.user.first_name?.[0] + log.user.last_name?.[0]).toUpperCase() : 'SY'}
                      </div>
                      <span className="text-body-sm">{log.user ? `${log.user.first_name} ${log.user.last_name}` : 'System'}</span>
                    </td>
                  </tr>
                ))}
                {paginatedLogs.length === 0 && !loading && (
                  <tr>
                    <td colSpan="8" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">history</span>
                      <p>No inventory history found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-md bg-surface-container border-t border-outline-variant flex flex-wrap items-center justify-between text-body-sm text-on-surface-variant gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <span>Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} logs</span>
              <div className="flex items-center gap-2 border-l border-outline-variant pl-4">
                <span>Rows per page:</span>
                <select 
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="bg-surface border border-outline-variant rounded px-2 py-1 outline-none focus:border-primary cursor-pointer"
                >
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button onClick={() => handlePageChange('prev')} disabled={currentPage === 1} className="p-1 px-2 border border-outline-variant rounded hover:bg-surface disabled:opacity-50 transition-colors"><span className="material-symbols-outlined text-[18px]">chevron_left</span></button>
              <button className="p-1 px-3 border border-outline-variant bg-primary text-on-primary rounded font-bold">{currentPage}</button>
              <button onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0} className="p-1 px-2 border border-outline-variant rounded hover:bg-surface disabled:opacity-50 transition-colors"><span className="material-symbols-outlined text-[18px]">chevron_right</span></button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryHistory;
