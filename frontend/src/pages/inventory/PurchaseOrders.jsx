import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';
import PurchaseOrderDetailModal from './PurchaseOrderDetailModal';
import PurchaseOrderTrackingModal from './PurchaseOrderTrackingModal';
import PurchaseOrderStatusModal from './PurchaseOrderStatusModal';

const PurchaseOrders = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Pagination
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedPO, setSelectedPO] = useState(null);
  const [trackingPO, setTrackingPO] = useState(null);
  const [statusPO, setStatusPO] = useState(null);

  const fetchPOData = useCallback(async () => {
    const [summaryRes, poRes] = await Promise.all([
      api.get('/purchase-orders/summary'),
      api.get('/purchase-orders?page_size=100') // fetch all for client side pagination/filter
    ]);
    return {
      summary: summaryRes.data.data,
      purchase_orders: poRes.data.data || []
    };
  }, []);

  const { data, loading, isSyncing, refresh } = useDataSync(
    fetchPOData,
    [],
    'medium'
  );

  const summary = data?.summary || {};
  const purchaseOrders = data?.purchase_orders || [];

  // Filter & Search
  const filteredPOs = useMemo(() => {
    return purchaseOrders.filter(po => {
      const matchesStatus = statusFilter === 'All' || po.shipment_status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = po.po_number?.toLowerCase().includes(searchLower) ||
                            po.vendor_name?.toLowerCase().includes(searchLower) ||
                            po.tracking_number?.toLowerCase().includes(searchLower);
      return matchesStatus && matchesSearch;
    });
  }, [purchaseOrders, searchTerm, statusFilter]);

  const totalItems = filteredPOs.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedPOs = filteredPOs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'Processing': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">PROCESSING</span>;
      case 'Ordered': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/50 text-secondary border border-secondary/30 uppercase">ORDERED</span>;
      case 'Packed': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/50 text-secondary border border-secondary/30 uppercase">PACKED</span>;
      case 'Dispatched': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/20 text-primary border border-primary/20 uppercase">DISPATCHED</span>;
      case 'In Transit': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/20 text-primary border border-primary/20 uppercase">IN TRANSIT</span>;
      case 'Delivered': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#eaddff]/30 text-[#4f378b] border border-[#eaddff] uppercase">DELIVERED</span>;
      case 'Delayed': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">DELAYED</span>;
      default: return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{status}</span>;
    }
  };

  const poColumns = [
    { key: 'po_number', label: 'PO Number' },
    { key: 'vendor_name', label: 'Vendor Name' },
    { key: 'procurement_request_id', label: 'Request ID', format: (val) => val?.substring(0, 8) || '--' },
    { key: 'cost', label: 'Total Cost', format: (val) => val ? `₹${Number(val).toFixed(2)}` : '₹0.00' },
    { key: 'order_date', label: 'Order Date', format: (val) => val ? new Date(val).toLocaleDateString() : '--' },
    { key: 'delivery_date', label: 'Est. Delivery Date', format: (val) => val ? new Date(val).toLocaleDateString() : '--' },
    { key: 'tracking_id', label: 'Tracking ID', format: (val) => val || '--' },
    { key: 'shipment_status', label: 'Shipment Status' }
  ];

  const handleExport = (type) => {
    if (type === 'csv') downloadCSV(filteredPOs, 'purchase_orders.csv', poColumns);
    else if (type === 'pdf') downloadPDF(filteredPOs, 'purchase_orders.pdf', 'Purchase Orders Log', poColumns);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <div className="p-3 md:p-lg space-y-lg flex-1 overflow-y-auto custom-scrollbar min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Purchase Orders</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Track ordered parts and vendor shipments</p>
          </div>
          <div className="flex items-center gap-md">
            <button onClick={refresh} disabled={loading || isSyncing} className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50">
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
          </div>
        </div>

        {/* Workflow UI */}
        <div className="bg-surface-container-lowest p-md rounded-lg border border-outline-variant flex flex-wrap items-center justify-between text-body-sm font-bold text-on-surface-variant overflow-x-auto gap-2">
          <div className="flex items-center gap-2 text-primary"><span className="material-symbols-outlined text-[18px]">receipt_long</span> PO Generated</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-secondary"><span className="material-symbols-outlined text-[18px]">inventory</span> Processing</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-tertiary"><span className="material-symbols-outlined text-[18px]">local_shipping</span> Dispatched</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-[#4f378b]"><span className="material-symbols-outlined text-[18px]">where_to_vote</span> Delivered</div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-xs md:gap-md">
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Total POs</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{summary.total_orders ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Processing</p>
            <h3 className="font-display-sm text-display-sm text-secondary">{summary.processing ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Ordered</p>
            <h3 className="font-display-sm text-display-sm text-primary">{summary.ordered ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">In Transit</p>
            <h3 className="font-display-sm text-display-sm text-tertiary">{summary.in_transit ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Delivered</p>
            <h3 className="font-display-sm text-display-sm text-[#4f378b]">{summary.delivered ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Delayed</p>
            <h3 className="font-display-sm text-display-sm text-error">{summary.delayed ?? '--'}</h3>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-sm w-full md:w-auto">
            <div className="relative flex-1">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all" 
                placeholder="Search PO number, vendor..." 
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
                <option value="Processing">Processing</option>
                <option value="Ordered">Ordered</option>
                <option value="Dispatched">Dispatched</option>
                <option value="In Transit">In Transit</option>
                <option value="Delivered">Delivered</option>
                <option value="Delayed">Delayed</option>
              </select>
            </div>
          </div>
        </div>

        {/* PO Table */}
        <div className="bg-surface rounded-lg border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Purchase Orders Ledger</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => handleExport('csv')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export CSV"><span className="material-symbols-outlined text-[20px]">csv</span></button>
              <button onClick={() => handleExport('pdf')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export PDF"><span className="material-symbols-outlined text-[20px]">picture_as_pdf</span></button>
            </div>
          </div>
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="bg-surface-container-lowest text-on-surface-variant text-label-caps border-b border-outline-variant">
                  <th className="px-md py-3 font-bold">PO Number</th>
                  <th className="px-md py-3 font-bold">Vendor Name</th>
                  <th className="px-md py-3 font-bold">Req ID</th>
                  <th className="px-md py-3 font-bold">Cost</th>
                  <th className="px-md py-3 font-bold">Order / Delivery</th>
                  <th className="px-md py-3 font-bold">Tracking ID</th>
                  <th className="px-md py-3 font-bold">Status</th>
                  <th className="px-md py-3 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan="8" className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-full"></div></td>
                    </tr>
                  ))
                ) : paginatedPOs.map(po => (
                  <tr key={po.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-md py-3 font-data-tabular font-bold">{po.po_number}</td>
                    <td className="px-md py-3 text-body-sm">{po.vendor_name || '--'}</td>
                    <td className="px-md py-3 text-[12px] text-outline truncate max-w-[100px]">{po.procurement_request_id}</td>
                    <td className="px-md py-3 font-data-tabular">₹{po.cost !== undefined && po.cost !== null ? Number(po.cost).toFixed(2) : '0.00'}</td>
                    <td className="px-md py-3 text-[12px]">
                      {po.order_date ? new Date(po.order_date).toLocaleDateString() : '--'} <br/>
                      <span className="text-on-surface-variant">{po.delivery_date ? new Date(po.delivery_date).toLocaleDateString() : '--'}</span>
                    </td>
                    <td className="px-md py-3 font-data-tabular text-[12px]">{po.tracking_id || '--'}</td>
                    <td className="px-md py-3">{getStatusChip(po.shipment_status)}</td>
                    <td className="px-md py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => setStatusPO(po)} className="text-on-surface-variant hover:text-tertiary hover:bg-tertiary-container/30 p-1 rounded" title="Update Status">
                          <span className="material-symbols-outlined text-[18px]">edit_square</span>
                        </button>
                        <button onClick={() => setSelectedPO(po)} className="text-on-surface-variant hover:text-primary hover:bg-primary-container/30 p-1 rounded" title="View PO & Invoice">
                          <span className="material-symbols-outlined text-[18px]">visibility</span>
                        </button>
                        <button onClick={() => setTrackingPO(po)} className="text-on-surface-variant hover:text-secondary hover:bg-secondary-container/30 p-1 rounded" title="Track Shipment">
                          <span className="material-symbols-outlined text-[18px]">local_shipping</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedPOs.length === 0 && !loading && (
                  <tr>
                    <td colSpan="8" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">receipt_long</span>
                      <p>No purchase orders found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-md bg-surface-container border-t border-outline-variant flex flex-wrap items-center justify-between text-body-sm text-on-surface-variant gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <span>Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} orders</span>
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

      <PurchaseOrderDetailModal 
        isOpen={!!selectedPO} 
        onClose={() => setSelectedPO(null)} 
        po={selectedPO} 
      />
      
      <PurchaseOrderTrackingModal 
        isOpen={!!trackingPO} 
        onClose={() => setTrackingPO(null)} 
        po={trackingPO} 
      />

      <PurchaseOrderStatusModal 
        isOpen={!!statusPO}
        onClose={() => setStatusPO(null)}
        po={statusPO}
        onSuccess={refresh}
      />
    </div>
  );
};

export default PurchaseOrders;
