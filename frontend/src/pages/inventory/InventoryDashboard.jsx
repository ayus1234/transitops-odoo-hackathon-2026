import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';
import AdjustStockModal from './AdjustStockModal';
import {
  Chart as ChartJS,
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
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

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

const InventoryDashboard = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Pagination
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPartForAdjustment, setSelectedPartForAdjustment] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    const [dashRes, partsRes] = await Promise.all([
      api.get('/inventory/dashboard'),
      api.get('/inventory/parts?page_size=100') // fetch all for client side pagination/filter
    ]);
    return {
      dashboard: dashRes.data.data,
      parts: partsRes.data.data || []
    };
  }, []);

  const { data, loading, isSyncing, refresh, lastUpdated } = useDataSync(
    fetchDashboardData,
    [],
    'medium'
  );

  const kpis = data?.dashboard || {};
  const parts = data?.parts || [];

  // Filter & Search
  const filteredParts = useMemo(() => {
    return parts.filter(p => {
      const matchesStatus = statusFilter === 'All' || p.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = p.name?.toLowerCase()?.includes(searchLower) ||
                            p.part_number?.toLowerCase()?.includes(searchLower) ||
                            p.vendor?.toLowerCase()?.includes(searchLower);
      return matchesStatus && matchesSearch;
    });
  }, [parts, searchTerm, statusFilter]);

  const totalItems = filteredParts.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedParts = filteredParts.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  // Status Chip Generator
  const getStatusChip = (status) => {
    switch (status) {
      case 'In Stock': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/20 text-primary border border-primary/20 uppercase">IN STOCK</span>;
      case 'Low Stock': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/50 text-secondary border border-secondary/30 uppercase">LOW STOCK</span>;
      case 'Critical Stock': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30 uppercase">CRITICAL</span>;
      case 'Out Of Stock': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">OUT OF STOCK</span>;
      case 'Reserved': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">RESERVED</span>;
      case 'Incoming Shipment': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#eaddff]/30 text-[#4f378b] border border-[#eaddff] uppercase">INCOMING</span>;
      default: return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{status}</span>;
    }
  };

  // Chart Data
  const healthData = {
    labels: ['Healthy', 'Low Stock', 'Critical/OOS'],
    datasets: [{
      data: [
        kpis.available_parts || 0,
        kpis.low_stock_parts || 0,
        (kpis.critical_stock_alerts || 0) + (kpis.out_of_stock_parts || 0)
      ],
      backgroundColor: ['#1b6d24', '#b38000', '#ba1a1a'],
      borderWidth: 0,
      hoverOffset: 10
    }]
  };

  const trendData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Inventory Usage',
      data: [12, 19, 15, 25, 22, 10, 8],
      borderColor: '#0040a1',
      backgroundColor: 'rgba(0, 64, 161, 0.05)',
      fill: true,
      tension: 0.4
    }]
  };

  const partColumns = [
    { key: 'part_number', label: 'Part Number' },
    { key: 'name', label: 'Name' },
    { key: 'category', label: 'Category' },
    { key: 'quantity_on_hand', label: 'Qty On Hand' },
    { key: 'minimum_stock_level', label: 'Min Stock Level' },
    { key: 'unit_cost', label: 'Unit Cost', format: (val) => val ? `₹${Number(val).toFixed(2)}` : '₹0.00' },
    { key: 'vendor', label: 'Preferred Vendor', format: (val) => val || '--' },
    { key: 'status', label: 'Status' }
  ];

  const handleExport = (type) => {
    console.log('TRANSITOPS_FIX_V3: EXPORTING INVENTORY');
    if (type === 'csv') downloadCSV(filteredParts, 'inventory_export.csv', partColumns);
    else if (type === 'pdf') downloadPDF(filteredParts, 'inventory_export.pdf', 'Inventory Parts Data', partColumns);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <div className="p-3 md:p-lg space-y-lg flex-1 overflow-y-auto custom-scrollbar min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Inventory Dashboard</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage parts, monitor health, and restock inventory</p>
          </div>
          <div className="flex items-center gap-md">
            <button onClick={refresh} disabled={loading || isSyncing} className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50">
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
            <button onClick={() => navigate('/inventory/procurement')} className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm">
              <span className="material-symbols-outlined">shopping_cart</span>
              <span className="font-body-md text-body-md">Create Request</span>
            </button>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-xs md:gap-md">
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Total Parts</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{kpis.total_parts ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Available Parts</p>
            <h3 className="font-display-sm text-display-sm text-primary">{kpis.available_parts ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Critical / Low</p>
            <h3 className="font-display-sm text-display-sm text-secondary">{kpis.critical_stock_alerts ?? 0} / {kpis.low_stock_parts ?? 0}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Out Of Stock</p>
            <h3 className="font-display-sm text-display-sm text-error">{kpis.out_of_stock_parts ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm relative overflow-hidden">
            <div className="relative z-10">
              <p className="text-label-caps text-on-surface-variant mb-1">Health Score</p>
              <h3 className="font-display-sm text-display-sm text-tertiary">{kpis.inventory_health_score !== undefined ? `${Number(kpis.inventory_health_score).toFixed(1)}%` : '--'}</h3>
            </div>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Vehicles Waiting</p>
            <h3 className="font-display-sm text-display-sm text-error">{kpis.vehicles_waiting ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Pending Requests</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{kpis.pending_procurement_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Pending POs</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{kpis.pending_purchase_orders ?? '--'}</h3>
          </div>
        </div>

        {/* Analytics Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
            <h2 className="font-title-sm text-title-sm text-on-surface mb-lg">Inventory Health Distribution</h2>
            <div className="relative w-full h-[200px]">
              <Doughnut data={healthData} options={{ maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'right' } } }} />
            </div>
          </div>
          <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
            <h2 className="font-title-sm text-title-sm text-on-surface mb-lg">Inventory Usage Trends</h2>
            <div className="relative w-full h-[200px]">
              <Line data={trendData} options={{ maintainAspectRatio: false, plugins: { legend: { display: false } } }} />
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
                placeholder="Search part name, number, vendor..." 
                type="text"
                value={searchTerm}
                onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              />
            </div>
            <div className="flex flex-1 sm:flex-none items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant h-10">
              <span className="material-symbols-outlined text-[18px] text-outline">filter_list</span>
              <select 
                value={statusFilter}
                onChange={(e) => {setStatusFilter(e.target.value); setCurrentPage(1);}}
                className="flex-1 bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
              >
                <option value="All">All Statuses</option>
                <option value="In Stock">In Stock</option>
                <option value="Low Stock">Low Stock</option>
                <option value="Critical Stock">Critical Stock</option>
                <option value="Out Of Stock">Out Of Stock</option>
                <option value="Incoming Shipment">Incoming Shipment</option>
              </select>
            </div>
          </div>
        </div>

        {/* Parts Table */}
        <div className="bg-surface rounded-lg border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Parts Inventory</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => handleExport('csv')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export CSV"><span className="material-symbols-outlined text-[20px]">csv</span></button>
              <button onClick={() => handleExport('pdf')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export PDF"><span className="material-symbols-outlined text-[20px]">picture_as_pdf</span></button>
            </div>
          </div>
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead>
                <tr className="bg-surface-container-lowest text-on-surface-variant text-label-caps border-b border-outline-variant">
                  <th className="px-md py-3 font-bold">Part Number</th>
                  <th className="px-md py-3 font-bold">Part Name</th>
                  <th className="px-md py-3 font-bold">Current Stock</th>
                  <th className="px-md py-3 font-bold">Req/Sugg Qty</th>
                  <th className="px-md py-3 font-bold">Est Cost</th>
                  <th className="px-md py-3 font-bold">Status</th>
                  <th className="px-md py-3 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                      <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-48"></div></td>
                      <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                      <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                      <td className="px-md py-3"><div className="h-5 bg-slate-200 rounded-full w-24"></div></td>
                      <td className="px-md py-3 text-right"><div className="h-4 bg-slate-200 rounded w-8 ml-auto"></div></td>
                    </tr>
                  ))
                ) : paginatedParts.map(part => (
                  <tr key={part.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-md py-3 font-data-tabular">{part.part_number}</td>
                    <td className="px-md py-3 text-body-sm font-bold">{part.name}</td>
                    <td className="px-md py-3 text-body-sm">{part.quantity_available} units</td>
                    <td className="px-md py-3 text-body-sm">{part.minimum_stock_level} / {part.critical_stock_level}</td>
                    <td className="px-md py-3 font-data-tabular">₹{part.unit_cost !== undefined && part.unit_cost !== null ? Number(part.unit_cost).toFixed(2) : '0.00'}</td>
                    <td className="px-md py-3">{getStatusChip(part.status)}</td>
                    <td className="px-md py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => setSelectedPartForAdjustment(part)} className="text-secondary hover:bg-secondary-container/30 p-1 rounded" title="Adjust Stock">
                          <span className="material-symbols-outlined text-[18px]">inventory_2</span>
                        </button>
                        <button onClick={() => navigate('/inventory/procurement')} className="text-primary hover:bg-primary-container/30 p-1 rounded" title="Create Request">
                          <span className="material-symbols-outlined text-[18px]">add_shopping_cart</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedParts.length === 0 && !loading && (
                  <tr>
                    <td colSpan="7" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">inventory_2</span>
                      <p>No inventory parts found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-md bg-surface-container border-t border-outline-variant flex flex-wrap items-center justify-between text-body-sm text-on-surface-variant gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <span>Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} parts</span>
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
      
      <AdjustStockModal 
        isOpen={!!selectedPartForAdjustment}
        onClose={() => setSelectedPartForAdjustment(null)}
        part={selectedPartForAdjustment}
        onSuccess={refresh}
      />
    </div>
  );
};

export default InventoryDashboard;
