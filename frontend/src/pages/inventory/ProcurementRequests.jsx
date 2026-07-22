import React, { useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';
import { useAuth } from '../../contexts/AuthContext';
import ProcurementRequestModal from './ProcurementRequestModal';
import ProcurementRequestDetailModal from './ProcurementRequestDetailModal';

const ProcurementRequests = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { user } = useAuth();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  
  // Pagination
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);

  const fetchProcurementData = useCallback(async () => {
    const [summaryRes, reqsRes] = await Promise.all([
      api.get('/procurement/summary'),
      api.get('/procurement/requests?page_size=100') // fetch all for client side pagination/filter
    ]);
    return {
      summary: summaryRes.data.data,
      requests: reqsRes.data.data || []
    };
  }, []);

  const { data, loading, isSyncing, refresh } = useDataSync(
    fetchProcurementData,
    [],
    'medium'
  );

  const summary = data?.summary || {};
  const requests = data?.requests || [];

  // Filter & Search
  const filteredRequests = useMemo(() => {
    return requests.filter(r => {
      const matchesStatus = statusFilter === 'All' || r.status === statusFilter;
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = r.part?.name?.toLowerCase().includes(searchLower) ||
                            r.id?.toLowerCase().includes(searchLower) ||
                            r.vendor_name?.toLowerCase().includes(searchLower);
      return matchesStatus && matchesSearch;
    });
  }, [requests, searchTerm, statusFilter]);

  const totalItems = filteredRequests.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedRequests = filteredRequests.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const handleApprove = async (reqId) => {
    try {
      await api.post(`/procurement/approve-request?req_id=${reqId}`);
      showToast('Request approved successfully', 'success');
      refresh();
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to approve request', 'error');
    }
  };

  const handleReject = async (reqId) => {
    if (!window.confirm("Are you sure you want to reject this request?")) return;
    try {
      await api.post(`/procurement/reject-request?req_id=${reqId}`);
      showToast('Request rejected successfully', 'success');
      refresh();
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to reject request', 'error');
    }
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'Draft': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">DRAFT</span>;
      case 'Submitted': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-secondary-container/50 text-secondary border border-secondary/30 uppercase">SUBMITTED</span>;
      case 'Approved': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-primary-container/20 text-primary border border-primary/20 uppercase">APPROVED</span>;
      case 'Rejected': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-error-container text-on-error-container border border-error/20 uppercase">REJECTED</span>;
      case 'Ordered': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-tertiary-container/30 text-tertiary border border-tertiary/30 uppercase">ORDERED</span>;
      case 'Delivered': return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-[#eaddff]/30 text-[#4f378b] border border-[#eaddff] uppercase">DELIVERED</span>;
      default: return <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-surface-variant text-on-surface-variant uppercase">{status}</span>;
    }
  };
  
  const getPriorityChip = (priority) => {
    switch(priority) {
      case 'Critical': return <span className="text-[11px] font-bold text-error uppercase">{priority}</span>;
      case 'High': return <span className="text-[11px] font-bold text-secondary uppercase">{priority}</span>;
      default: return <span className="text-[11px] font-bold text-on-surface-variant uppercase">{priority}</span>;
    }
  };

  const procurementColumns = [
    { key: 'procurement_id', label: 'Request ID', format: (val, row) => val || row.id.substring(0, 8) },
    { key: 'part', label: 'Part Name', format: (val) => val?.name || 'Unknown Part' },
    { key: 'required_quantity', label: 'Required Qty' },
    { key: 'suggested_quantity', label: 'Suggested Qty', format: (val) => val || '--' },
    { key: 'vendor', label: 'Vendor', format: (val) => val || '--' },
    { key: 'estimated_cost', label: 'Est. Cost', format: (val) => val ? `₹${Number(val).toFixed(2)}` : '₹0.00' },
    { key: 'priority', label: 'Priority' },
    { key: 'status', label: 'Status' }
  ];

  const handleExport = (type) => {
    if (type === 'csv') downloadCSV(filteredRequests, 'procurement_requests.csv', procurementColumns);
    else if (type === 'pdf') downloadPDF(filteredRequests, 'procurement_requests.pdf', 'Procurement Requests Log', procurementColumns);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <div className="p-3 md:p-lg space-y-lg flex-1 overflow-y-auto custom-scrollbar min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Procurement Requests</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage, approve, and track parts procurement</p>
          </div>
          <div className="flex items-center gap-md">
            <button onClick={refresh} disabled={loading || isSyncing} className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50">
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
            <button onClick={() => setIsModalOpen(true)} className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm">
              <span className="material-symbols-outlined">add</span>
              <span className="font-body-md text-body-md">New Request</span>
            </button>
          </div>
        </div>

        {/* Workflow UI */}
        <div className="bg-surface-container-lowest p-md rounded-lg border border-outline-variant flex flex-wrap items-center justify-between text-body-sm font-bold text-on-surface-variant overflow-x-auto gap-2">
          <div className="flex items-center gap-2 text-error"><span className="material-symbols-outlined text-[18px]">warning</span> Parts Alert</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-primary"><span className="material-symbols-outlined text-[18px]">add_shopping_cart</span> Create Request</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-secondary"><span className="material-symbols-outlined text-[18px]">fact_check</span> Manager Approval</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-tertiary"><span className="material-symbols-outlined text-[18px]">receipt_long</span> PO Generated</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-on-surface"><span className="material-symbols-outlined text-[18px]">local_shipping</span> Shipment</div>
          <span className="material-symbols-outlined text-[18px] text-outline">arrow_forward</span>
          <div className="flex items-center gap-2 text-primary"><span className="material-symbols-outlined text-[18px]">inventory_2</span> Stock Updated</div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-xs md:gap-md">
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Total</p>
            <h3 className="font-display-sm text-display-sm text-on-surface">{summary.total_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Pending</p>
            <h3 className="font-display-sm text-display-sm text-secondary">{summary.submitted_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Approved</p>
            <h3 className="font-display-sm text-display-sm text-primary">{summary.approved_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Ordered</p>
            <h3 className="font-display-sm text-display-sm text-tertiary">{summary.ordered_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Delivered</p>
            <h3 className="font-display-sm text-display-sm text-[#4f378b]">{summary.delivered_requests ?? '--'}</h3>
          </div>
          <div className="bg-surface p-md rounded-lg border border-outline-variant shadow-sm">
            <p className="text-label-caps text-on-surface-variant mb-1">Rejected</p>
            <h3 className="font-display-sm text-display-sm text-error">{summary.rejected_requests ?? '--'}</h3>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-md">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-sm w-full md:w-auto">
            <div className="relative flex-1">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
              <input 
                className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all" 
                placeholder="Search requests..." 
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
                <option value="Submitted">Submitted</option>
                <option value="Approved">Approved</option>
                <option value="Ordered">Ordered</option>
                <option value="Delivered">Delivered</option>
                <option value="Rejected">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Requests Table */}
        <div className="bg-surface rounded-lg border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0">
          <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
            <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Procurement Log</h2>
            <div className="flex items-center gap-2">
              <button onClick={() => handleExport('csv')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export CSV"><span className="material-symbols-outlined text-[20px]">csv</span></button>
              <button onClick={() => handleExport('pdf')} className="p-1.5 text-on-surface-variant hover:text-primary rounded transition-colors" title="Export PDF"><span className="material-symbols-outlined text-[20px]">picture_as_pdf</span></button>
            </div>
          </div>
          <div className="overflow-x-auto min-h-[300px]">
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="bg-surface-container-lowest text-on-surface-variant text-label-caps border-b border-outline-variant">
                  <th className="px-md py-3 font-bold">Request ID</th>
                  <th className="px-md py-3 font-bold">Part Name</th>
                  <th className="px-md py-3 font-bold">Req/Sugg Qty</th>
                  <th className="px-md py-3 font-bold">Vendor</th>
                  <th className="px-md py-3 font-bold">Est Cost</th>
                  <th className="px-md py-3 font-bold">Priority</th>
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
                ) : paginatedRequests.map(req => (
                  <tr key={req.id} className="hover:bg-surface-container-low transition-colors group">
                    <td className="px-md py-3 font-data-tabular text-[12px] text-outline truncate max-w-[100px]">{req.id}</td>
                    <td className="px-md py-3 text-body-sm font-bold">{req.part?.name || 'Part Details Unavailable'}</td>
                    <td className="px-md py-3 text-body-sm">{req.required_quantity} / {req.suggested_quantity || '--'}</td>
                    <td className="px-md py-3 text-body-sm">{req.vendor || '--'}</td>
                    <td className="px-md py-3 font-data-tabular">₹{req.estimated_cost !== undefined && req.estimated_cost !== null ? Number(req.estimated_cost).toFixed(2) : '0.00'}</td>
                    <td className="px-md py-3">{getPriorityChip(req.priority)}</td>
                    <td className="px-md py-3">{getStatusChip(req.status)}</td>
                    <td className="px-md py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => setSelectedRequest(req)} className="text-on-surface-variant hover:text-primary hover:bg-primary-container/30 p-1 rounded" title="View Details">
                          <span className="material-symbols-outlined text-[18px]">visibility</span>
                        </button>
                        {req.status === 'Submitted' && (user?.role?.name === 'Super Admin' || user?.role?.name === 'Administrator' || user?.role?.name === 'Fleet Manager') && (
                          <>
                            <button onClick={() => handleApprove(req.id)} className="text-primary hover:bg-primary-container/30 p-1 rounded" title="Approve">
                              <span className="material-symbols-outlined text-[18px]">check_circle</span>
                            </button>
                            <button onClick={() => handleReject(req.id)} className="text-error hover:bg-error-container/30 p-1 rounded" title="Reject">
                              <span className="material-symbols-outlined text-[18px]">cancel</span>
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
                {paginatedRequests.length === 0 && !loading && (
                  <tr>
                    <td colSpan="8" className="text-center py-12 text-on-surface-variant">
                      <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">shopping_cart</span>
                      <p>No procurement requests found.</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          <div className="p-md bg-surface-container border-t border-outline-variant flex flex-wrap items-center justify-between text-body-sm text-on-surface-variant gap-4">
            <div className="flex flex-wrap items-center gap-4">
              <span>Showing {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems} requests</span>
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
      <ProcurementRequestModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onCreated={refresh} />
      {selectedRequest && (
        <ProcurementRequestDetailModal
          isOpen={!!selectedRequest}
          onClose={() => setSelectedRequest(null)}
          request={selectedRequest}
        />
      )}
    </div>
  );
};

export default ProcurementRequests;
