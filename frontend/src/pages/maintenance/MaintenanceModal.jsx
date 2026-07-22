import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';

const VALID_MAINTENANCE_TYPES = [
  'Oil Change', 'Tire Replacement', 'Engine Repair',
  'Brake Service', 'Battery Replacement', 'Transmission Service',
  'AC Service', 'General Inspection', 'Body Repair', 'Other'
];

const VALID_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'];

const MaintenanceModal = ({ isOpen, onClose, onSave, maintenance, isSaving }) => {
  const [vehicles, setVehicles] = useState([]);
  const [loadingVehicles, setLoadingVehicles] = useState(false);
  
  const [formData, setFormData] = useState({
    vehicle_id: '',
    maintenance_type: 'General Inspection',
    description: '',
    priority: 'Medium',
    assigned_technician: '',
    scheduled_date: '',
    estimated_cost: '',
    odometer_at_maintenance: '',
    notes: ''
  });
  
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchVehicles();
      if (maintenance) {
        setFormData({
          vehicle_id: maintenance.vehicle?.id || '',
          maintenance_type: maintenance.maintenance_type || 'General Inspection',
          description: maintenance.description || '',
          priority: maintenance.priority || 'Medium',
          assigned_technician: maintenance.assigned_technician || '',
          scheduled_date: maintenance.scheduled_date || '',
          estimated_cost: maintenance.estimated_cost ? String(maintenance.estimated_cost) : '',
          odometer_at_maintenance: maintenance.odometer_at_maintenance ? String(maintenance.odometer_at_maintenance) : '',
          notes: maintenance.notes || ''
        });
      } else {
        setFormData({
          vehicle_id: '',
          maintenance_type: 'General Inspection',
          description: '',
          priority: 'Medium',
          assigned_technician: '',
          scheduled_date: new Date().toISOString().split('T')[0],
          estimated_cost: '',
          odometer_at_maintenance: '',
          notes: ''
        });
      }
      setError(null);
    }
  }, [isOpen, maintenance]);

  const fetchVehicles = async () => {
    setLoadingVehicles(true);
    try {
      const response = await api.get('/vehicles');
      setVehicles(response.data.data || []);
    } catch {
      setError("Failed to fetch vehicles for assignment.");
    } finally {
      setLoadingVehicles(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      const payload = {
        vehicle_id: formData.vehicle_id,
        maintenance_type: formData.maintenance_type,
        description: formData.description,
        priority: formData.priority,
        scheduled_date: formData.scheduled_date,
      };

      if (formData.assigned_technician) payload.assigned_technician = formData.assigned_technician;
      if (formData.estimated_cost) payload.estimated_cost = parseFloat(formData.estimated_cost);
      if (formData.odometer_at_maintenance) payload.odometer_at_maintenance = parseFloat(formData.odometer_at_maintenance);
      if (formData.notes) payload.notes = formData.notes;

      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={maintenance ? "Edit Service Record" : "New Service Record"} maxWidth="max-w-2xl">
      {error && (
        <div className="mb-md p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
          <span className="material-symbols-outlined">error</span>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
          
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Vehicle *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none disabled:opacity-50"
              name="vehicle_id"
              value={formData.vehicle_id}
              onChange={handleChange}
              required
              disabled={loadingVehicles || !!maintenance} // Cannot change vehicle if editing (per typical rule, though schema might allow if pending)
            >
              <option value="">Select Vehicle...</option>
              {vehicles.map(v => (
                <option key={v.id} value={v.id}>{v.registration_number} ({v.make} {v.model})</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Maintenance Type *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="maintenance_type"
              value={formData.maintenance_type}
              onChange={handleChange}
              required
            >
              {VALID_MAINTENANCE_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs md:col-span-2">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Issue Description *</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="description"
              placeholder="E.g., Brake pad replacement and alignment"
              value={formData.description}
              onChange={handleChange}
              required
              minLength={1}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Priority *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              required
            >
              {VALID_PRIORITIES.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Scheduled Date *</label>
            <input 
              type="date"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="scheduled_date"
              value={formData.scheduled_date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Assigned Technician</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="assigned_technician"
              placeholder="Technician name"
              value={formData.assigned_technician}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Estimated Cost (₹)</label>
            <input 
              type="number"
              step="0.01"
              min="0"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="estimated_cost"
              value={formData.estimated_cost}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Odometer at Maintenance (km)</label>
            <input 
              type="number"
              step="0.1"
              min="0"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="odometer_at_maintenance"
              value={formData.odometer_at_maintenance}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-xs md:col-span-2">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Additional Notes</label>
            <textarea 
              className="w-full px-sm py-2 bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none resize-none"
              name="notes"
              rows="2"
              value={formData.notes}
              onChange={handleChange}
            ></textarea>
          </div>

        </div>

        <div className="flex justify-end gap-md pt-md border-t border-outline-variant">
          <button 
            type="button" 
            onClick={onClose}
            className="px-lg py-2 rounded text-on-surface-variant font-bold hover:bg-surface-variant transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            disabled={isSaving}
            className="px-lg py-2 rounded bg-primary text-on-primary font-bold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
          >
            {isSaving ? (
              <><span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span> Saving...</>
            ) : (
              'Save Record'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default MaintenanceModal;
