import React, { useState } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const PurchaseOrderStatusModal = ({ isOpen, onClose, po, onSuccess }) => {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Processing');
  
  React.useEffect(() => {
    if (isOpen && po) {
      setStatus(po.shipment_status || 'Processing');
    }
  }, [isOpen, po]);

  if (!isOpen || !po) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (status === po.shipment_status) {
      onClose();
      return;
    }

    try {
      setLoading(true);
      await api.post(`/purchase-orders/${po.id}/update-status?status=${encodeURIComponent(status)}`);
      showToast('Status updated successfully!', 'success');
      onSuccess();
      onClose();
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to update status', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-surface min-w-[300px] md:min-w-[384px] w-full max-w-[384px] shrink-0 rounded-xl shadow-lg border border-outline-variant overflow-hidden">
        <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
          <h2 className="font-title-lg font-bold text-on-surface">Update PO Status</h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface hover:bg-surface-variant p-1 rounded-full transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-lg space-y-md">
          <div className="mb-4">
            <p className="text-body-sm text-on-surface-variant">Updating status for:</p>
            <p className="font-bold text-on-surface text-body-lg">{po.po_number}</p>
            <p className="text-body-sm text-on-surface-variant mt-1">Vendor: {po.vendor_name}</p>
          </div>

          <div className="space-y-1">
            <label className="text-label-md font-bold text-on-surface">New Status *</label>
            <select 
              value={status} 
              onChange={(e) => setStatus(e.target.value)}
              className="w-full h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none"
            >
              <option value="Processing">Processing</option>
              <option value="Ordered">Ordered</option>
              <option value="Packed">Packed</option>
              <option value="Dispatched">Dispatched</option>
              <option value="In Transit">In Transit</option>
              <option value="Delivered">Delivered</option>
              <option value="Delayed">Delayed</option>
            </select>
          </div>
          
          <div className="pt-4 flex justify-end gap-2 border-t border-outline-variant mt-4">
            <button 
              type="button" 
              onClick={onClose} 
              className="px-4 py-2 text-on-surface-variant font-bold rounded-lg hover:bg-surface-variant transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={loading}
              className="px-4 py-2 bg-primary text-on-primary font-bold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <span className="material-symbols-outlined animate-spin text-[18px]">sync</span> : null}
              Confirm
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PurchaseOrderStatusModal;
