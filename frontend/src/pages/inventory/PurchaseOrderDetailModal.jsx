import React from 'react';
import Modal from '../../components/ui/Modal';
import { downloadPDF } from '../../utils/exportUtils';

const PurchaseOrderDetailModal = ({ isOpen, onClose, po }) => {
  if (!po) return null;

  const handleDownloadInvoice = () => {
    // Generate a quick PDF invoice representation
    const invoiceData = [
      {
        po_number: po.po_number,
        vendor: po.vendor_name,
        quantity: po.quantity,
        total_cost: po.cost,
        order_date: po.order_date ? new Date(po.order_date).toLocaleDateString() : 'N/A',
        status: po.shipment_status
      }
    ];
    
    const invoiceColumns = [
      { key: 'po_number', label: 'Invoice / PO #' },
      { key: 'vendor', label: 'Vendor' },
      { key: 'quantity', label: 'Total Units' },
      { key: 'total_cost', label: 'Amount Due', format: val => `₹${Number(val).toFixed(2)}` },
      { key: 'order_date', label: 'Date Issued' },
      { key: 'status', label: 'Payment Status', format: val => val === 'Delivered' ? 'PAID' : 'PENDING' }
    ];

    downloadPDF(invoiceData, `Invoice_${po.po_number}.pdf`, `Purchase Order Invoice - ${po.po_number}`, invoiceColumns);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Purchase Order Details">
      <div className="p-md space-y-md">
        
        {/* Header Info */}
        <div className="bg-surface-container-lowest p-md rounded-lg border border-outline-variant flex items-center justify-between">
          <div>
            <p className="text-label-caps text-on-surface-variant">PO Number</p>
            <h3 className="font-title-lg text-title-lg font-bold text-on-surface">{po.po_number}</h3>
          </div>
          <div className="text-right">
            <p className="text-label-caps text-on-surface-variant">Total Cost</p>
            <h3 className="font-display-sm text-display-sm font-bold text-primary">₹{po.cost !== undefined && po.cost !== null ? Number(po.cost).toFixed(2) : '0.00'}</h3>
          </div>
        </div>

        {/* Grid Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-body-md text-on-surface">
          <div>
            <p className="text-label-caps text-on-surface-variant">Vendor Name</p>
            <p className="font-bold">{po.vendor_name || '--'}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Status</p>
            <p className="font-bold uppercase">{po.shipment_status}</p>
          </div>
          
          <div>
            <p className="text-label-caps text-on-surface-variant">Total Quantity</p>
            <p className="font-bold">{po.quantity} Units</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Related Request ID</p>
            <p className="font-bold text-outline">{po.procurement_request_id || '--'}</p>
          </div>

          <div>
            <p className="text-label-caps text-on-surface-variant">Order Date</p>
            <p className="font-bold">{po.order_date ? new Date(po.order_date).toLocaleString() : '--'}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Estimated Delivery</p>
            <p className="font-bold">{po.delivery_date ? new Date(po.delivery_date).toLocaleString() : '--'}</p>
          </div>

          <div className="col-span-2">
            <p className="text-label-caps text-on-surface-variant">Tracking Number</p>
            <p className="font-bold font-data-tabular">{po.tracking_id || 'Pending Assignment'}</p>
          </div>
        </div>
      </div>
      
      <div className="p-md border-t border-outline-variant flex justify-between items-center bg-surface-container-low">
        <button
          onClick={handleDownloadInvoice}
          className="h-10 px-md rounded-lg font-bold text-body-md text-primary hover:bg-primary-container/30 transition-colors flex items-center gap-2"
        >
          <span className="material-symbols-outlined text-[18px]">download</span>
          Download Invoice
        </button>
        <button
          onClick={onClose}
          className="h-10 px-md rounded-lg font-bold text-body-md bg-primary text-on-primary hover:bg-primary-container transition-colors"
        >
          Close
        </button>
      </div>
    </Modal>
  );
};

export default PurchaseOrderDetailModal;
