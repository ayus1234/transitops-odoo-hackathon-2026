import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';

const VALID_FUEL_TYPES = ['Diesel', 'Petrol', 'CNG', 'Electric'];

const FuelModal = ({ isOpen, onClose, onSave, fuelRecord, isSaving }) => {
  const [vehicles, setVehicles] = useState([]);
  const [trips, setTrips] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);
  
  const [formData, setFormData] = useState({
    vehicle_id: '',
    trip_id: '',
    fuel_type: 'Diesel',
    quantity_liters: '',
    cost_per_liter: '',
    odometer_reading: '',
    refuel_date: '',
    station_name: '',
    location: '',
    receipt_number: ''
  });
  
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchResources();
      if (fuelRecord) {
        // Date formatting for input type="datetime-local" or "date". We'll use datetime-local if refuel_date is datetime.
        // The schema expects datetime. "YYYY-MM-DDThh:mm"
        let formattedDate = '';
        if (fuelRecord.refuel_date) {
          const d = new Date(fuelRecord.refuel_date);
          const tzoffset = (new Date()).getTimezoneOffset() * 60000; 
          formattedDate = (new Date(d - tzoffset)).toISOString().slice(0,16);
        }

        setFormData({
          vehicle_id: fuelRecord.vehicle?.id || '',
          trip_id: fuelRecord.trip?.id || '',
          fuel_type: fuelRecord.fuel_type || 'Diesel',
          quantity_liters: fuelRecord.quantity_liters ? String(fuelRecord.quantity_liters) : '',
          cost_per_liter: fuelRecord.cost_per_liter ? String(fuelRecord.cost_per_liter) : '',
          odometer_reading: fuelRecord.odometer_reading ? String(fuelRecord.odometer_reading) : '',
          refuel_date: formattedDate,
          station_name: fuelRecord.station_name || '',
          location: fuelRecord.location || '',
          receipt_number: fuelRecord.receipt_number || ''
        });
      } else {
        const tzoffset = (new Date()).getTimezoneOffset() * 60000; 
        const now = (new Date(Date.now() - tzoffset)).toISOString().slice(0,16);
        
        setFormData({
          vehicle_id: '',
          trip_id: '',
          fuel_type: 'Diesel',
          quantity_liters: '',
          cost_per_liter: '',
          odometer_reading: '',
          refuel_date: now,
          station_name: '',
          location: '',
          receipt_number: ''
        });
      }
      setError(null);
    }
  }, [isOpen, fuelRecord]);

  const fetchResources = async () => {
    setLoadingResources(true);
    try {
      const [vRes, tRes] = await Promise.all([
        api.get('/vehicles'),
        api.get('/trips')
      ]);
      setVehicles(vRes.data.data || []);
      setTrips(tRes.data.data || []);
    } catch {
      setError("Failed to fetch vehicles and trips.");
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
        vehicle_id: formData.vehicle_id,
        fuel_type: formData.fuel_type,
        quantity_liters: parseFloat(formData.quantity_liters),
        cost_per_liter: parseFloat(formData.cost_per_liter),
        odometer_reading: parseFloat(formData.odometer_reading),
      };

      if (formData.trip_id) payload.trip_id = formData.trip_id;
      if (formData.refuel_date) payload.refuel_date = new Date(formData.refuel_date).toISOString();
      if (formData.station_name) payload.station_name = formData.station_name;
      if (formData.location) payload.location = formData.location;
      if (formData.receipt_number) payload.receipt_number = formData.receipt_number;

      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={fuelRecord ? "Edit Fuel Log" : "Log New Fuel Expense"} maxWidth="max-w-3xl">
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
              disabled={loadingResources || !!fuelRecord} 
            >
              <option value="">Select Vehicle...</option>
              {vehicles.map(v => (
                <option key={v.id} value={v.id}>{v.registration_number} ({v.make} {v.model})</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Associated Trip</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none disabled:opacity-50"
              name="trip_id"
              value={formData.trip_id}
              onChange={handleChange}
              disabled={loadingResources}
            >
              <option value="">None / General</option>
              {trips.map(t => (
                <option key={t.id} value={t.id}>{t.trip_number} ({t.origin} to {t.destination})</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Fuel Type *</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="fuel_type"
              value={formData.fuel_type}
              onChange={handleChange}
              required
            >
              {VALID_FUEL_TYPES.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Refuel Date & Time *</label>
            <input 
              type="datetime-local"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="refuel_date"
              value={formData.refuel_date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Quantity (Liters) *</label>
            <input 
              type="number"
              step="0.01"
              min="0.01"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="quantity_liters"
              value={formData.quantity_liters}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Cost Per Liter (₹) *</label>
            <input 
              type="number"
              step="0.001"
              min="0.001"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="cost_per_liter"
              value={formData.cost_per_liter}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Odometer Reading (km) *</label>
            <input 
              type="number"
              step="0.1"
              min="0"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="odometer_reading"
              value={formData.odometer_reading}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Receipt Number</label>
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
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Station Name</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="station_name"
              value={formData.station_name}
              onChange={handleChange}
              maxLength={255}
            />
          </div>

          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Location / City</label>
            <input 
              type="text"
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm outline-none"
              name="location"
              value={formData.location}
              onChange={handleChange}
              maxLength={255}
            />
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
              'Save Log'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default FuelModal;
