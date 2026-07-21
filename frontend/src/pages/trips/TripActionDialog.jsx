import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';

const TripActionDialog = ({ isOpen, onClose, onConfirm, actionType, trip, isProcessing }) => {
  const [formData, setFormData] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setFormData({});
      setError(null);
    }
  }, [isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError(null);

    let payload = {};

    if (actionType === 'dispatch') {
      if (!formData.start_odometer_km) return setError("Start odometer is required.");
      payload = { start_odometer_km: parseFloat(formData.start_odometer_km) };
    } 
    else if (actionType === 'complete') {
      if (!formData.end_odometer_km || !formData.actual_distance_km) {
        return setError("End odometer and actual distance are required.");
      }
      payload = {
        end_odometer_km: parseFloat(formData.end_odometer_km),
        actual_distance_km: parseFloat(formData.actual_distance_km),
        fuel_consumed_liters: formData.fuel_consumed_liters ? parseFloat(formData.fuel_consumed_liters) : null,
        notes: formData.notes || null
      };
    } 
    else if (actionType === 'cancel') {
      if (!formData.reason) return setError("Cancellation reason is required.");
      payload = { reason: formData.reason };
    }

    onConfirm(payload);
  };

  if (!isOpen) return null;

  let title = '';
  let icon = '';
  let color = '';

  if (actionType === 'dispatch') {
    title = 'Dispatch Trip';
    icon = 'local_shipping';
    color = 'text-secondary';
  } else if (actionType === 'complete') {
    title = 'Complete Trip';
    icon = 'flag';
    color = 'text-primary';
  } else if (actionType === 'cancel') {
    title = 'Cancel Trip';
    icon = 'cancel';
    color = 'text-error';
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
            <p className="font-bold text-on-surface">Trip {trip?.trip_number}</p>
            <p className="text-xs text-on-surface-variant">{trip?.source} to {trip?.destination}</p>
          </div>
        </div>

        {actionType === 'dispatch' && (
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Start Odometer (km) *</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="start_odometer_km" 
              type="number"
              step="0.1"
              required 
              value={formData.start_odometer_km || ''}
              onChange={handleChange}
            />
          </div>
        )}

        {actionType === 'complete' && (
          <>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">End Odometer (km) *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="end_odometer_km" 
                type="number"
                step="0.1"
                required 
                value={formData.end_odometer_km || ''}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Actual Distance (km) *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="actual_distance_km" 
                type="number"
                step="0.1"
                required 
                value={formData.actual_distance_km || ''}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Fuel Consumed (Liters)</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="fuel_consumed_liters" 
                type="number"
                step="0.1"
                value={formData.fuel_consumed_liters || ''}
                onChange={handleChange}
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Completion Notes</label>
              <textarea 
                className="w-full px-sm py-2 bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none resize-none" 
                name="notes" 
                rows="2"
                value={formData.notes || ''}
                onChange={handleChange}
              ></textarea>
            </div>
          </>
        )}

        {actionType === 'cancel' && (
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Reason for Cancellation *</label>
            <textarea 
              className="w-full px-sm py-2 bg-surface border border-outline-variant rounded focus:border-error transition-all font-body-sm focus:ring-2 focus:ring-error/20 outline-none resize-none" 
              name="reason" 
              rows="3"
              required
              value={formData.reason || ''}
              onChange={handleChange}
            ></textarea>
          </div>
        )}

        <div className="flex justify-end gap-md pt-sm border-t border-outline-variant mt-lg">
          <button 
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors"
          >
            Go Back
          </button>
          <button 
            type="submit"
            disabled={isProcessing}
            className={`px-4 py-2 text-white font-bold rounded transition-opacity flex items-center gap-2 disabled:opacity-50 ${actionType === 'cancel' ? 'bg-error hover:bg-error/90' : actionType === 'dispatch' ? 'bg-secondary hover:bg-secondary/90' : 'bg-primary hover:bg-primary/90'}`}
          >
            {isProcessing ? (
              <>
                <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
                Processing...
              </>
            ) : (
              'Confirm'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default TripActionDialog;
