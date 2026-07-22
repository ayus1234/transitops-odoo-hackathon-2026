import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';

const VehicleModal = ({ isOpen, onClose, onSave, vehicle, isSaving }) => {
  const [formData, setFormData] = useState({
    registration_number: '',
    vehicle_name: '',
    vehicle_type: 'Truck',
    manufacturer: '',
    model: '',
    year: '',
    capacity_kg: '',
    fuel_type: 'Diesel',
    current_odometer_km: '0',
    acquisition_cost: '',
    status: 'Available'
  });

  const [error, setError] = useState(null);

  useEffect(() => {
    if (vehicle) {
      setFormData({
        registration_number: vehicle.registration_number || '',
        vehicle_name: vehicle.vehicle_name || '',
        vehicle_type: vehicle.vehicle_type || 'Truck',
        manufacturer: vehicle.manufacturer || '',
        model: vehicle.model || '',
        year: vehicle.year || '',
        capacity_kg: vehicle.capacity_kg || '',
        fuel_type: vehicle.fuel_type || 'Diesel',
        current_odometer_km: vehicle.current_odometer_km || '0',
        acquisition_cost: vehicle.acquisition_cost || '',
        status: vehicle.status || 'Available'
      });
    } else {
      setFormData({
        registration_number: '',
        vehicle_name: '',
        vehicle_type: 'Truck',
        manufacturer: '',
        model: '',
        year: '',
        capacity_kg: '',
        fuel_type: 'Diesel',
        current_odometer_km: '0',
        acquisition_cost: '',
        status: 'Available'
      });
    }
    setError(null);
  }, [vehicle, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Basic validation
    if (!formData.registration_number || !formData.vehicle_name || !formData.capacity_kg) {
      setError("Registration, Name, and Capacity are required.");
      return;
    }

    try {
      // Cast numeric fields
      const payload = {
        ...formData,
        year: formData.year ? parseInt(formData.year) : null,
        capacity_kg: parseFloat(formData.capacity_kg),
        current_odometer_km: parseFloat(formData.current_odometer_km) || 0,
        acquisition_cost: formData.acquisition_cost ? parseFloat(formData.acquisition_cost) : null
      };
      
      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving the vehicle.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={vehicle ? "Edit Vehicle" : "Register New Vehicle"} maxWidth="max-w-2xl">
      {error && (
        <div className="mb-md p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
          <span className="material-symbols-outlined">error</span>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
          {/* Registration Number */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Registration Number *</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="registration_number" 
              placeholder="e.g. TX-7822-LK" 
              required 
              value={formData.registration_number}
              onChange={handleChange}
            />
          </div>

          {/* Vehicle Name/Model string */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Display Name *</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="vehicle_name" 
              placeholder="e.g. Volvo FH16 (2023)" 
              required 
              value={formData.vehicle_name}
              onChange={handleChange}
            />
          </div>

          {/* Vehicle Type */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Vehicle Type</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none"
              name="vehicle_type"
              value={formData.vehicle_type}
              onChange={handleChange}
            >
              <option value="Truck">Truck / HGV</option>
              <option value="Van">Van / LCV</option>
              <option value="Pickup">Pickup</option>
              <option value="Trailer">Trailer</option>
              <option value="Bus">Bus</option>
              <option value="Car">Car</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Fuel Type */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Fuel Type</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none"
              name="fuel_type"
              value={formData.fuel_type}
              onChange={handleChange}
            >
              <option value="Diesel">Diesel</option>
              <option value="Petrol">Petrol</option>
              <option value="CNG">CNG</option>
              <option value="Electric">Electric</option>
              <option value="Hybrid">Hybrid</option>
            </select>
          </div>

          {/* Capacity */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Capacity (kg) *</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="capacity_kg" 
              type="number"
              step="0.01"
              placeholder="44000" 
              required 
              value={formData.capacity_kg}
              onChange={handleChange}
            />
          </div>

          {/* Odometer */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Odometer (km)</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="current_odometer_km" 
              type="number"
              step="0.01"
              value={formData.current_odometer_km}
              onChange={handleChange}
            />
          </div>

          {/* Manufacturer */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Manufacturer</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="manufacturer" 
              placeholder="e.g. Volvo" 
              value={formData.manufacturer}
              onChange={handleChange}
            />
          </div>

          {/* Year */}
          <div className="space-y-xs">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Manufacturing Year</label>
            <input 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
              name="year" 
              type="number"
              min="1900"
              max="2100"
              placeholder="2023" 
              value={formData.year}
              onChange={handleChange}
            />
          </div>
          
          {/* Status (Only available in Edit mode practically, but good to have) */}
          <div className="space-y-xs md:col-span-2">
            <label className="font-body-sm text-body-sm font-bold text-on-surface">Operational Status</label>
            <select 
              className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none"
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="Available">Available</option>
              <option value="On Trip">On Trip</option>
              <option value="In Shop">In Shop</option>
              <option value="Retired">Retired</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-md pt-md border-t border-outline-variant mt-xl">
          <button 
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit"
            disabled={isSaving}
            className="px-4 py-2 bg-primary text-on-primary font-bold rounded hover:opacity-90 transition-opacity flex items-center gap-2 disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
                Saving...
              </>
            ) : (
              'Save Vehicle'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default VehicleModal;
