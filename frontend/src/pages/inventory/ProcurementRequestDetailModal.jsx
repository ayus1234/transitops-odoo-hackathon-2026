import React from 'react';
import Modal from '../../components/ui/Modal';

const ProcurementRequestDetailModal = ({ isOpen, onClose, request }) => {
  if (!request) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Procurement Request Details">
      <div className="p-md space-y-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-body-md text-on-surface">
          <div>
            <p className="text-label-caps text-on-surface-variant">Request ID</p>
            <p className="font-bold">{request.procurement_id || request.id}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Status</p>
            <p className="font-bold uppercase">{request.status}</p>
          </div>
          
          <div className="col-span-2">
            <p className="text-label-caps text-on-surface-variant">Part Details</p>
            <p className="font-bold text-lg">{request.part?.name || 'Unknown Part'}</p>
            <p className="text-on-surface-variant text-sm">Part Number: {request.part?.part_number}</p>
          </div>

          <div>
            <p className="text-label-caps text-on-surface-variant">Required Quantity</p>
            <p className="font-bold">{request.required_quantity}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Suggested Quantity</p>
            <p className="font-bold">{request.suggested_quantity || '--'}</p>
          </div>

          <div>
            <p className="text-label-caps text-on-surface-variant">Vendor</p>
            <p className="font-bold">{request.vendor || '--'}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Estimated Cost</p>
            <p className="font-bold font-data-tabular">₹{request.estimated_cost !== undefined && request.estimated_cost !== null ? Number(request.estimated_cost).toFixed(2) : '0.00'}</p>
          </div>

          <div>
            <p className="text-label-caps text-on-surface-variant">Priority</p>
            <p className="font-bold uppercase">{request.priority}</p>
          </div>
          <div>
            <p className="text-label-caps text-on-surface-variant">Created At</p>
            <p className="font-bold">{new Date(request.created_at).toLocaleString()}</p>
          </div>
        </div>
      </div>
      
      <div className="p-md border-t border-outline-variant flex justify-end">
        <button
          onClick={onClose}
          className="h-10 px-md rounded-lg font-bold text-body-md border border-outline hover:bg-surface-container-low transition-colors"
        >
          Close
        </button>
      </div>
    </Modal>
  );
};

export default ProcurementRequestDetailModal;
