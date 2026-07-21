import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';

const DriverModal = ({ isOpen, onClose, onSave, driver, isSaving }) => {
  const [formData, setFormData] = useState({
    // User fields (only for Create)
    full_name: '',
    email: '',
    password: '',
    
    // Driver fields
    license_number: '',
    license_category: 'CDL-CLASS-A',
    license_issue_date: '',
    license_expiry_date: '',
    date_of_birth: '',
    emergency_contact: '',
    
    // Update only
    status: 'Available',
    safety_score: ''
  });

  const [error, setError] = useState(null);

  useEffect(() => {
    if (driver) {
      setFormData({
        full_name: driver.user?.full_name || '',
        email: driver.user?.email || '',
        password: '', // Never populate password on edit
        
        license_number: driver.license_number || '',
        license_category: driver.license_category || 'CDL-CLASS-A',
        license_issue_date: driver.license_issue_date || '',
        license_expiry_date: driver.license_expiry_date || '',
        date_of_birth: driver.date_of_birth || '',
        emergency_contact: driver.emergency_contact || '',
        
        status: driver.status || 'Available',
        safety_score: driver.safety_score !== null && driver.safety_score !== undefined ? String(driver.safety_score) : ''
      });
    } else {
      setFormData({
        full_name: '',
        email: '',
        password: '',
        
        license_number: '',
        license_category: 'CDL-CLASS-A',
        license_issue_date: '',
        license_expiry_date: '',
        date_of_birth: '',
        emergency_contact: '',
        
        status: 'Available',
        safety_score: ''
      });
    }
    setError(null);
  }, [driver, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Basic Validation
    if (!driver && (!formData.full_name || !formData.email || !formData.password)) {
      setError("Name, Email, and Password are required to create a new driver account.");
      return;
    }
    if (!formData.license_number || !formData.license_issue_date || !formData.license_expiry_date || !formData.date_of_birth) {
      setError("Please fill in all required license and personal information.");
      return;
    }

    try {
      let payload;
      if (driver) {
        // Update Payload
        payload = {
          license_number: formData.license_number,
          license_category: formData.license_category,
          license_issue_date: formData.license_issue_date,
          license_expiry_date: formData.license_expiry_date,
          date_of_birth: formData.date_of_birth,
          emergency_contact: formData.emergency_contact || null,
          status: formData.status
        };
        if (formData.safety_score !== '') {
          payload.safety_score = parseFloat(formData.safety_score);
        }
      } else {
        // Create Payload
        payload = {
          user: {
            email: formData.email,
            password: formData.password,
            first_name: formData.full_name.split(' ')[0] || 'Unknown',
            last_name: formData.full_name.split(' ').slice(1).join(' ') || 'Unknown',
            is_active: true
          },
          license_number: formData.license_number,
          license_category: formData.license_category,
          license_issue_date: formData.license_issue_date,
          license_expiry_date: formData.license_expiry_date,
          date_of_birth: formData.date_of_birth,
          emergency_contact: formData.emergency_contact || null
        };
      }
      
      await onSave(payload);
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred while saving the driver.");
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={driver ? "Edit Driver" : "Onboard New Driver"} maxWidth="max-w-3xl">
      {error && (
        <div className="mb-md p-3 bg-error-container text-on-error-container text-sm rounded border border-error/20 flex items-center gap-2">
          <span className="material-symbols-outlined">error</span>
          {typeof error === 'string' ? error : JSON.stringify(error)}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-lg">
        
        {/* User Account Section (Disabled/Hidden fields during edit if API doesn't support nested updates) */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md">
          <h3 className="font-title-sm text-primary mb-md flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px]">account_circle</span>
            Account Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Full Name *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none disabled:opacity-50" 
                name="full_name" 
                placeholder="e.g. Sarah Jenkins" 
                required 
                value={formData.full_name}
                onChange={handleChange}
                disabled={!!driver} // Disable user modification if editing driver
              />
            </div>
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Email Address *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none disabled:opacity-50" 
                name="email" 
                type="email"
                placeholder="sarah.jenkins@transitops.com" 
                required 
                value={formData.email}
                onChange={handleChange}
                disabled={!!driver}
              />
            </div>
            {!driver && (
              <div className="space-y-xs md:col-span-2">
                <label className="font-body-sm text-body-sm font-bold text-on-surface">Temporary Password *</label>
                <input 
                  className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                  name="password" 
                  type="password"
                  placeholder="Minimum 8 characters" 
                  required={!driver}
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>
            )}
          </div>
        </div>

        {/* License & Personal Details */}
        <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md">
          <h3 className="font-title-sm text-primary mb-md flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px]">badge</span>
            Licensing & Personal
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">License Number *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="license_number" 
                placeholder="#44120-TX-11" 
                required 
                value={formData.license_number}
                onChange={handleChange}
              />
            </div>
            
            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">License Category</label>
              <select 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none"
                name="license_category"
                value={formData.license_category}
                onChange={handleChange}
              >
                <option value="CDL-CLASS-A">CDL Class A</option>
                <option value="CDL-CLASS-B">CDL Class B</option>
                <option value="CDL-CLASS-C">CDL Class C</option>
                <option value="Standard">Standard/LMV</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Issue Date *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="license_issue_date" 
                type="date"
                required 
                value={formData.license_issue_date}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Expiry Date *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="license_expiry_date" 
                type="date"
                required 
                value={formData.license_expiry_date}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Date of Birth *</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="date_of_birth" 
                type="date"
                required 
                value={formData.date_of_birth}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-xs">
              <label className="font-body-sm text-body-sm font-bold text-on-surface">Emergency Contact</label>
              <input 
                className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                name="emergency_contact" 
                placeholder="+1 (555) 000-0000" 
                value={formData.emergency_contact}
                onChange={handleChange}
              />
            </div>
          </div>
        </div>

        {/* Operational (Edit Only) */}
        {driver && (
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-md">
            <h3 className="font-title-sm text-primary mb-md flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px]">manage_accounts</span>
              Operational Details
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
              <div className="space-y-xs">
                <label className="font-body-sm text-body-sm font-bold text-on-surface">Status</label>
                <select 
                  className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="Available">Available</option>
                  <option value="On Trip">On Trip</option>
                  <option value="Off Duty">Off Duty</option>
                  <option value="Suspended">Suspended</option>
                </select>
              </div>
              <div className="space-y-xs">
                <label className="font-body-sm text-body-sm font-bold text-on-surface">Safety Score (0-100)</label>
                <input 
                  className="w-full h-[40px] px-sm bg-surface border border-outline-variant rounded focus:border-primary transition-all font-body-sm focus:ring-2 focus:ring-primary/20 outline-none" 
                  name="safety_score" 
                  type="number"
                  min="0"
                  max="100"
                  placeholder="e.g. 98"
                  value={formData.safety_score}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end gap-md pt-sm">
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
              'Save Driver'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default DriverModal;
