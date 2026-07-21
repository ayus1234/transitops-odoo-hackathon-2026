import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const TripModal = ({ isOpen, onClose, onSave, trip, isSaving }) => {
  const [step, setStep] = useState(1);
  const [error, setError] = useState(null);
  
  // Lists for Step 2
  const [availableVehicles, setAvailableVehicles] = useState([]);
  const [availableDrivers, setAvailableDrivers] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);

  // Form Data matching TripCreate / TripUpdate
  const [formData, setFormData] = useState({
    source: '',
    destination: '',
    cargo_weight_kg: '',
    planned_distance_km: '',
    planned_departure: '',
    planned_arrival: '',
    notes: '',
    vehicle_id: '',
    driver_id: ''
  });

  useEffect(() => {
    if (isOpen) {
      if (trip) {
        // Editing existing trip
        setFormData({
          source: trip.source || '',
          destination: trip.destination || '',
          cargo_weight_kg: trip.cargo_weight_kg ? String(trip.cargo_weight_kg) : '',
          planned_distance_km: trip.planned_distance_km ? String(trip.planned_distance_km) : '',
          planned_departure: trip.planned_departure ? new Date(trip.planned_departure).toISOString().slice(0, 16) : '',
          planned_arrival: trip.planned_arrival ? new Date(trip.planned_arrival).toISOString().slice(0, 16) : '',
          notes: trip.notes || '',
          vehicle_id: trip.vehicle?.id || '',
          driver_id: trip.driver?.id || ''
        });
      } else {
        // New Trip
        setFormData({
          source: '',
          destination: '',
          cargo_weight_kg: '',
          planned_distance_km: '',
          planned_departure: '',
          planned_arrival: '',
          notes: '',
          vehicle_id: '',
          driver_id: ''
        });
      }
      setStep(1);
      setError(null);
    }
  }, [isOpen, trip]);

  // Fetch available resources when entering Step 2
  useEffect(() => {
    if (step === 2 && isOpen) {
      const fetchResources = async () => {
        setLoadingResources(true);
        try {
          // We can fetch all and filter client side for simplicity, or just fetch all available.
          // Since the mock might just return all, let's fetch all and filter by status === 'Available'
          const [vehRes, drvRes] = await Promise.all([
            api.get('/vehicles'),
            api.get('/drivers')
          ]);
          
          let vList = vehRes.data.data || [];
          let dList = drvRes.data.data || [];

          // If editing, make sure the currently assigned vehicle/driver is in the list even if they are 'On Trip' now
          if (trip) {
            setAvailableVehicles(vList);
            setAvailableDrivers(dList);
          } else {
            setAvailableVehicles(vList.filter(v => v.status === 'Available'));
            setAvailableDrivers(dList.filter(d => d.status === 'Available'));
          }
        } catch {
          setError("Failed to load available vehicles and drivers.");
        } finally {
          setLoadingResources(false);
        }
      };
      fetchResources();
    }
  }, [step, isOpen, trip]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleNext = () => {
    setError(null);
    if (step === 1) {
      if (!formData.source || !formData.destination || !formData.planned_departure || !formData.planned_arrival || !formData.planned_distance_km || !formData.cargo_weight_kg) {
        setError("Please fill in all routing and details before proceeding.");
        return;
      }
      if (new Date(formData.planned_arrival) <= new Date(formData.planned_departure)) {
        setError("Planned arrival must be after planned departure.");
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (!formData.vehicle_id || !formData.driver_id) {
        setError("Please select both a vehicle and a driver.");
        return;
      }
      setStep(3);
    }
  };

  const handleBack = () => {
    setError(null);
    if (step > 1) setStep(step - 1);
  };

  const handleSubmit = async () => {
    setError(null);
    try {
      const payload = {
        vehicle_id: formData.vehicle_id,
        driver_id: formData.driver_id,
        source: formData.source,
        destination: formData.destination,
        cargo_weight_kg: parseFloat(formData.cargo_weight_kg),
        planned_distance_km: parseFloat(formData.planned_distance_km),
        planned_departure: new Date(formData.planned_departure).toISOString(),
        planned_arrival: new Date(formData.planned_arrival).toISOString(),
        notes: formData.notes || null
      };
      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving the trip.");
    }
  };

  // Helper to get names for the Confirm step
  const selectedVehicleName = availableVehicles.find(v => v.id === formData.vehicle_id)?.registration_number || (trip?.vehicle?.registration_number) || 'Unknown';
  const selectedDriverName = availableDrivers.find(d => d.id === formData.driver_id)?.user?.full_name || (trip?.driver?.license_number) || 'Unknown';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm transition-opacity duration-300">
      <div className="bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col min-w-0 max-h-[90vh]" style={{ width: '100%', maxWidth: '896px' }}>
        
        {/* Wizard Header */}
        <div className="px-lg py-md bg-surface border-b border-outline-variant flex justify-between items-center shrink-0">
          <div>
            <h3 className="font-headline-md text-headline-md text-primary">{trip ? "Edit Trip Planning" : "New Trip Planning"}</h3>
            <p className="text-body-sm text-on-surface-variant">Step {step} of 3: {step === 1 ? 'Details & Routing' : step === 2 ? 'Allocation' : 'Confirmation'}</p>
          </div>
          <button className="p-2 hover:bg-surface-container-high rounded-full transition-all" onClick={onClose}>
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="px-lg py-sm bg-error-container text-on-error-container border-b border-error/20 flex items-center gap-2 text-sm">
            <span className="material-symbols-outlined text-[18px]">error</span>
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </div>
        )}

        {/* Wizard Stepper */}
        <div className="px-lg py-sm bg-surface-container-low flex items-center gap-md shrink-0">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'opacity-100' : 'opacity-50'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${step >= 1 ? 'bg-primary text-on-primary' : 'bg-outline-variant text-on-surface-variant'}`}>1</div>
            <span className="text-body-sm font-bold">Routing</span>
          </div>
          <div className="flex-1 h-[1px] bg-outline-variant"></div>
          <div className={`flex items-center gap-2 ${step >= 2 ? 'opacity-100' : 'opacity-50'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${step >= 2 ? 'bg-primary text-on-primary' : 'bg-outline-variant text-on-surface-variant'}`}>2</div>
            <span className="text-body-sm font-bold">Allocation</span>
          </div>
          <div className="flex-1 h-[1px] bg-outline-variant"></div>
          <div className={`flex items-center gap-2 ${step === 3 ? 'opacity-100' : 'opacity-50'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${step === 3 ? 'bg-primary text-on-primary' : 'bg-outline-variant text-on-surface-variant'}`}>3</div>
            <span className="text-body-sm font-bold">Confirm</span>
          </div>
        </div>

        {/* Wizard Content */}
        <div className="flex-1 overflow-y-auto p-lg">
          
          {step === 1 && (
            <div className="grid grid-cols-1 md:grid-cols-12 gap-lg h-full">
              {/* Trip Info Section */}
              <div className="md:col-span-7 space-y-md">
                <div className="space-y-sm">
                  <label className="block text-body-sm font-bold text-on-surface">Source Location *</label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">location_on</span>
                    <input 
                      className="w-full pl-10 pr-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                      name="source"
                      placeholder="e.g. Mumbai Hub (MH)"
                      value={formData.source}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-sm">
                  <label className="block text-body-sm font-bold text-on-surface">Destination Location *</label>
                  <div className="relative">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">flag</span>
                    <input 
                      className="w-full pl-10 pr-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                      name="destination"
                      placeholder="e.g. Delhi DC (DL)"
                      value={formData.destination}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
                  <div className="space-y-sm">
                    <label className="block text-body-sm font-bold text-on-surface">Planned Departure *</label>
                    <input 
                      className="w-full px-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none" 
                      type="datetime-local"
                      name="planned_departure"
                      value={formData.planned_departure}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="space-y-sm">
                    <label className="block text-body-sm font-bold text-on-surface">Planned Arrival *</label>
                    <input 
                      className="w-full px-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none" 
                      type="datetime-local"
                      name="planned_arrival"
                      value={formData.planned_arrival}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
                  <div className="space-y-sm">
                    <label className="block text-body-sm font-bold text-on-surface">Distance (km) *</label>
                    <input 
                      className="w-full px-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none" 
                      type="number"
                      step="0.1"
                      min="0.1"
                      name="planned_distance_km"
                      value={formData.planned_distance_km}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  <div className="space-y-sm">
                    <label className="block text-body-sm font-bold text-on-surface">Cargo Weight (kg) *</label>
                    <input 
                      className="w-full px-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none" 
                      type="number"
                      step="0.1"
                      min="0.1"
                      name="cargo_weight_kg"
                      value={formData.cargo_weight_kg}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-sm">
                  <label className="block text-body-sm font-bold text-on-surface">Cargo Notes</label>
                  <textarea 
                    className="w-full px-4 py-2 border border-outline rounded text-body-md focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none" 
                    placeholder="Additional delivery instructions..." 
                    rows="2"
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                  ></textarea>
                </div>
              </div>
              
              {/* Preview Sidebar */}
              <div className="md:col-span-5 bg-surface-container-low p-md rounded-lg border border-outline-variant space-y-md h-fit">
                <h4 className="text-label-caps text-on-surface-variant">Route Summary</h4>
                <div className="bg-white p-3 rounded border border-outline-variant">
                  <div className="flex items-start gap-3">
                    <div className="flex flex-col items-center gap-1 mt-1">
                      <div className="w-2 h-2 rounded-full bg-primary"></div>
                      <div className="w-[1px] h-8 border-l border-dashed border-outline"></div>
                      <div className="w-2 h-2 border-2 border-primary rounded-full"></div>
                    </div>
                    <div className="flex-1 space-y-4">
                      <div>
                        <p className="text-[10px] text-on-surface-variant font-bold">START</p>
                        <p className="text-body-sm font-medium">{formData.source || 'Please set source'}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-on-surface-variant font-bold">END</p>
                        <p className="text-body-sm font-medium">{formData.destination || 'Please set destination'}</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center text-body-sm">
                  <span className="text-on-surface-variant">Estimated Distance</span>
                  <span className="font-data-tabular">{formData.planned_distance_km || '--'} km</span>
                </div>
                <div className="flex justify-between items-center text-body-sm">
                  <span className="text-on-surface-variant">Cargo Weight</span>
                  <span className="font-data-tabular">{formData.cargo_weight_kg || '--'} kg</span>
                </div>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="h-full flex flex-col items-center justify-center mx-auto space-y-xl py-lg" style={{ width: '100%', maxWidth: '672px' }}>
              {loadingResources ? (
                <div className="flex flex-col items-center opacity-50">
                  <span className="material-symbols-outlined animate-spin text-4xl mb-4">progress_activity</span>
                  <p>Loading available resources...</p>
                </div>
              ) : (
                <>
                  <div className="w-full space-y-sm">
                    <label className="block text-body-md font-bold text-on-surface flex items-center gap-2">
                      <span className="material-symbols-outlined text-secondary">local_shipping</span>
                      Assign Vehicle *
                    </label>
                    <select 
                      className="w-full px-4 py-3 border border-outline rounded-lg text-body-md focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
                      name="vehicle_id"
                      value={formData.vehicle_id}
                      onChange={handleChange}
                    >
                      <option value="">Select a vehicle...</option>
                      {availableVehicles.map(v => (
                        <option key={v.id} value={v.id}>
                          {v.registration_number} - {v.make} {v.model} ({v.status})
                        </option>
                      ))}
                    </select>
                    {availableVehicles.length === 0 && <p className="text-xs text-error">No available vehicles found.</p>}
                  </div>

                  <div className="w-full space-y-sm">
                    <label className="block text-body-md font-bold text-on-surface flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary">person_pin</span>
                      Assign Driver *
                    </label>
                    <select 
                      className="w-full px-4 py-3 border border-outline rounded-lg text-body-md focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
                      name="driver_id"
                      value={formData.driver_id}
                      onChange={handleChange}
                    >
                      <option value="">Select a driver...</option>
                      {availableDrivers.map(d => (
                        <option key={d.id} value={d.id}>
                          {d.user?.full_name} - {d.license_category} ({d.status})
                        </option>
                      ))}
                    </select>
                    {availableDrivers.length === 0 && <p className="text-xs text-error">No available drivers found.</p>}
                  </div>
                </>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="mx-auto space-y-lg py-md" style={{ width: '100%', maxWidth: '768px' }}>
              <div className="text-center mb-lg">
                <span className="material-symbols-outlined text-[48px] text-secondary mb-4">check_circle</span>
                <h4 className="text-headline-md font-bold text-on-surface">Ready to Save Trip</h4>
                <p className="text-on-surface-variant">Please review the details before confirming.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-md bg-surface-container-lowest p-md rounded-lg border border-outline-variant">
                <div>
                  <p className="text-xs text-on-surface-variant font-bold uppercase mb-1">Route</p>
                  <p className="font-bold text-on-surface">{formData.source}</p>
                  <span className="material-symbols-outlined text-[16px] text-outline my-1">arrow_downward</span>
                  <p className="font-bold text-on-surface">{formData.destination}</p>
                </div>
                <div>
                  <p className="text-xs text-on-surface-variant font-bold uppercase mb-1">Allocation</p>
                  <p className="text-body-sm mb-1"><span className="font-bold">Vehicle:</span> {selectedVehicleName}</p>
                  <p className="text-body-sm"><span className="font-bold">Driver:</span> {selectedDriverName}</p>
                </div>
              </div>
            </div>
          )}
          
        </div>

        {/* Wizard Footer */}
        <div className="px-lg py-md bg-surface border-t border-outline-variant flex justify-between items-center shrink-0">
          <button 
            className="px-lg py-2 border border-outline-variant rounded-lg text-body-md font-bold hover:bg-surface-container transition-all" 
            onClick={step === 1 ? onClose : handleBack}
          >
            {step === 1 ? 'Cancel' : 'Back'}
          </button>
          
          <div className="flex gap-md">
            {step < 3 ? (
              <button 
                className="px-lg py-2 bg-primary text-on-primary rounded-lg text-body-md font-bold hover:opacity-90 transition-all flex items-center gap-2"
                onClick={handleNext}
              >
                Next: {step === 1 ? 'Fleet Allocation' : 'Review'}
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </button>
            ) : (
              <button 
                className="px-lg py-2 bg-secondary text-on-secondary rounded-lg text-body-md font-bold hover:opacity-90 transition-all flex items-center gap-2 disabled:opacity-50"
                onClick={handleSubmit}
                disabled={isSaving}
              >
                {isSaving ? (
                  <><span className="material-symbols-outlined animate-spin text-sm">progress_activity</span> Saving...</>
                ) : (
                  <><span className="material-symbols-outlined text-sm">save</span> {trip ? "Save Changes" : "Create Trip"}</>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TripModal;
