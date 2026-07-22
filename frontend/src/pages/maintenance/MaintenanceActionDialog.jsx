import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';

const VALID_STATUSES = ['Pending', 'Approved', 'In Progress', 'Completed', 'Rejected'];

const MaintenanceActionDialog = ({ isOpen, onClose, onConfirm, actionType, maintenance, isProcessing }) => {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setFormData({
        completed_date: new Date().toISOString().split('T')[0],
        status: maintenance?.status || 'Pending'
      });
      setError(null);
    }
  }, [isOpen, maintenance]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);

    let payload = {};

    if (actionType === 'complete') {
      if (!formData.actual_cost || !formData.completed_date) {
        return setError("Actual cost and completion date are required.");
      }
      payload = {
        completed_date: formData.completed_date,
        actual_cost: parseFloat(formData.actual_cost),
        notes: formData.notes || null
      };
    } else if (actionType === 'status') {
      payload = { status: formData.status };
    }

    onConfirm(payload);
  };

  if (!isOpen) return null;

  let title = '';
  let icon = '';
  let color = '';

  if (actionType === 'complete') {
    title = 'Complete Maintenance';
    icon = 'check_circle';
    color = 'text-primary';
  } else if (actionType === 'status') {
    title = 'Update Status';
    icon = 'update';
    color = 'text-secondary';
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} maxWidth="max-w-md">
      {error && (
        <div className="mb-md p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
          <span className="material-symbols-outlined">error</span>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-md">
        <div className="flex items-center gap-3 mb-md">
          <div className={`p-2 rounded-full bg-surface-container-high ${color}`}>
            <span className="material-symbols-outlined">{icon}</span>
          </div>
          <div>
            <p className="font-bold text-on-surface">{maintenance?.maintenance_number}</p>
            <p className="text-xs text-on-surface-variant">{maintenance?.maintenance_type} for {maintenance?.vehicle?.registration_number}</p>
          </div>
        </div>

        {actionType === 'complete' && (
          <>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Completion Date *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none" 
                name="completed_date" 
                type="date"
                required 
                value={formData.completed_date || ''}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Actual Cost (₹) *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none" 
                name="actual_cost" 
                type="number"
                step="0.01"
                min="0"
                required 
                value={formData.actual_cost || ''}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Completion Notes</label>
              <textarea 
                className="w-full px-sm py-2 bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none resize-none" 
                name="notes" 
                rows="2"
                value={formData.notes || ''}
                onChange={handleChange}
              ></textarea>
            </div>
          </>
        )}

        {actionType === 'status' && (
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">New Status *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none" 
              name="status" 
              required
              value={formData.status || ''}
              onChange={handleChange}
            >
              {VALID_STATUSES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}

        <div className="flex justify-end gap-md pt-sm border-t border-outline-variant mt-lg">
          <button 
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit"
            disabled={isProcessing}
            className={`px-4 py-2 text-white font-bold rounded transition-opacity flex items-center gap-2 disabled:opacity-50 ${actionType === 'complete' ? 'bg-primary hover:bg-primary/90' : 'bg-secondary hover:bg-secondary/90'}`}
          >
            {isProcessing ? (
              <><span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> Processing...</>
            ) : (
              'Confirm'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default MaintenanceActionDialog;
