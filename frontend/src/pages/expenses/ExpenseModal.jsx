import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';

const VALID_EXPENSE_TYPES = ['Fuel', 'Maintenance', 'Toll', 'Repair', 'Miscellaneous'];

const ExpenseModal = ({ isOpen, onClose, onSave, expenseRecord, isSaving }) => {
  const [vehicles, setVehicles] = useState([]);
  const [trips, setTrips] = useState([]);
  const [maintenances, setMaintenances] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);
  
  const [formData, setFormData] = useState({
    expense_type: 'Miscellaneous',
    amount: '',
    expense_date: '',
    description: '',
    vehicle_id: '',
    trip_id: '',
    maintenance_id: '',
    receipt_number: '',
    vendor_name: ''
  });
  
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchResources();
      if (expenseRecord) {
        setFormData({
          expense_type: expenseRecord.expense_type || 'Miscellaneous',
          amount: expenseRecord.amount ? String(expenseRecord.amount) : '',
          expense_date: expenseRecord.expense_date || '',
          description: expenseRecord.description || '',
          vehicle_id: expenseRecord.vehicle?.id || '',
          trip_id: expenseRecord.trip?.id || '',
          maintenance_id: expenseRecord.maintenance?.id || '',
          receipt_number: expenseRecord.receipt_number || '',
          vendor_name: expenseRecord.vendor_name || ''
        });
      } else {
        const today = new Date().toISOString().split('T')[0];
        setFormData({
          expense_type: 'Miscellaneous',
          amount: '',
          expense_date: today,
          description: '',
          vehicle_id: '',
          trip_id: '',
          maintenance_id: '',
          receipt_number: '',
          vendor_name: ''
        });
      }
      setError(null);
    }
  }, [isOpen, expenseRecord]);

  const fetchResources = async () => {
    setLoadingResources(true);
    try {
      const [vRes, tRes, mRes] = await Promise.all([
        api.get('/vehicles'),
        api.get('/trips'),
        api.get('/maintenance')
      ]);
      setVehicles(vRes.data.data || []);
      setTrips(tRes.data.data || []);
      setMaintenances(mRes.data.data || []);
    } catch {
      setError("Failed to fetch relational records (vehicles/trips/maintenance).");
    } finally {
      setLoadingResources(false);
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
        expense_type: formData.expense_type,
        amount: parseFloat(formData.amount),
        expense_date: formData.expense_date,
        description: formData.description
      };

      if (formData.vehicle_id) payload.vehicle_id = formData.vehicle_id;
      if (formData.trip_id) payload.trip_id = formData.trip_id;
      if (formData.maintenance_id) payload.maintenance_id = formData.maintenance_id;
      if (formData.receipt_number) payload.receipt_number = formData.receipt_number;
      if (formData.vendor_name) payload.vendor_name = formData.vendor_name;

      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={expenseRecord ? "Edit Expense Log" : "Log New Expense"} maxWidth="max-w-3xl">
      {error && (
        <div className="mb-md p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
          <span className="material-symbols-outlined">error</span>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
          
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Expense Type *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="expense_type"
              value={formData.expense_type}
              onChange={handleChange}
              required
            >
              {VALID_EXPENSE_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Date *</label>
            <input 
              type="date"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="expense_date"
              value={formData.expense_date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs md:col-span-2">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Description *</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="description"
              placeholder="Detailed description of the expense"
              value={formData.description}
              onChange={handleChange}
              required
              minLength={1}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Amount (₹) *</label>
            <input 
              type="number"
              step="0.01"
              min="0.01"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Vendor Name</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="vendor_name"
              placeholder="E.g. AutoZone, Exxon"
              value={formData.vendor_name}
              onChange={handleChange}
              maxLength={255}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Receipt / Invoice Number</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="receipt_number"
              value={formData.receipt_number}
              onChange={handleChange}
              maxLength={100}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Related Vehicle</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none disabled:opacity-50"
              name="vehicle_id"
              value={formData.vehicle_id}
              onChange={handleChange}
              disabled={loadingResources} 
            >
              <option value="">None / General</option>
              {vehicles.map(v => (
                <option key={v.id} value={v.id}>{v.registration_number}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Related Trip</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none disabled:opacity-50"
              name="trip_id"
              value={formData.trip_id}
              onChange={handleChange}
              disabled={loadingResources}
            >
              <option value="">None / General</option>
              {trips.map(t => (
                <option key={t.id} value={t.id}>{t.trip_number}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Related Maintenance</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none disabled:opacity-50"
              name="maintenance_id"
              value={formData.maintenance_id}
              onChange={handleChange}
              disabled={loadingResources}
            >
              <option value="">None / General</option>
              {maintenances.map(m => (
                <option key={m.id} value={m.id}>{m.maintenance_number} - {m.description.substring(0, 15)}...</option>
              ))}
            </select>
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
              'Save Expense'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ExpenseModal;
