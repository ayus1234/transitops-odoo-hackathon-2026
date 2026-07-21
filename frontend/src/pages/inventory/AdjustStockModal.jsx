import React, { useState } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const AdjustStockModal = ({ isOpen, onClose, part, onSuccess }) => {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [quantityChange, setQuantityChange] = useState('');
  const [type, setType] = useState('Adjustment');
  const [referenceId, setReferenceId] = useState('');
  
  // React to prop changes inside component
  React.useEffect(() => {
    if (isOpen) {
      setQuantityChange('');
      setType('Adjustment');
      setReferenceId('');
    }
  }, [isOpen]);

  if (!isOpen || !part) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const qtyNum = parseInt(quantityChange, 10);
    if (isNaN(qtyNum) || qtyNum === 0) {
      showToast('Please enter a valid non-zero quantity change.', 'error');
      return;
    }

    // Check if consuming more than available
    if (qtyNum < 0 && Math.abs(qtyNum) > part.quantity_available) {
      showToast(`Cannot consume ${Math.abs(qtyNum)}. Only ${part.quantity_available} available.`, 'error');
      return;
    }

    try {
      setLoading(true);
      await api.post(`/inventory/${part.id}/adjust`, {
        quantity_change: qtyNum,
        type: type,
        reference_id: referenceId || undefined
      });
      showToast('Stock adjusted successfully!', 'success');
      onSuccess();
      onClose();
    } catch (err) {
      showToast(err.response?.data?.message || 'Failed to adjust stock', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-surface min-w-[320px] md:min-w-[400px] w-full max-w-[448px] shrink-0 rounded-xl shadow-lg border border-outline-variant overflow-hidden">
        <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
          <h2 className="font-title-lg font-bold text-on-surface">Adjust Stock</h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface hover:bg-surface-variant p-1 rounded-full transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-lg space-y-md">
          <div className="mb-4">
            <p className="text-body-sm text-on-surface-variant">Adjusting stock for:</p>
            <p className="font-bold text-on-surface text-body-lg">{part.name} ({part.part_number})</p>
            <p className="text-body-sm text-primary mt-1">Current Available: {part.quantity_available}</p>
          </div>

          <div className="grid grid-cols-1 gap-md">
            <div className="space-y-1">
              <label className="text-label-md font-bold text-on-surface">Adjustment Type *</label>
              <select 
                value={type} 
                onChange={(e) => setType(e.target.value)}
                className="w-full h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none"
              >
                <option value="Adjustment">Manual Adjustment</option>
                <option value="Release">Release / Consume for Maintenance</option>
                <option value="Restock">Restock</option>
                <option value="Reserved">Reserve Stock</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-label-md font-bold text-on-surface">Quantity Change *</label>
              <input 
                type="number" 
                required 
                placeholder="e.g. -5 to consume, 10 to add"
                value={quantityChange} 
                onChange={(e) => setQuantityChange(e.target.value)}
                className="w-full h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none"
              />
              <p className="text-[11px] text-outline">Use negative values to deduct stock.</p>
            </div>

            <div className="space-y-1">
              <label className="text-label-md font-bold text-on-surface">Reference ID (Optional)</label>
              <input 
                type="text" 
                placeholder="e.g. MNT-2026-0012"
                value={referenceId} 
                onChange={(e) => setReferenceId(e.target.value)}
                className="w-full h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none"
              />
            </div>
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
              Confirm Adjustment
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdjustStockModal;
