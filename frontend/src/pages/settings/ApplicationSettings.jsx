import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const ApplicationSettings = () => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    app_name: '',
    maintenance_alert_days: 7,
    license_expiry_alert_days: 30,
    max_trip_duration_hours: 24,
    auto_approve_expenses_below: 0.0,
  });

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/settings');
      if (response.data) {
        setFormData({
          app_name: response.data.app_name || '',
          maintenance_alert_days: response.data.maintenance_alert_days || 7,
          license_expiry_alert_days: response.data.license_expiry_alert_days || 30,
          max_trip_duration_hours: response.data.max_trip_duration_hours || 24,
          auto_approve_expenses_below: response.data.auto_approve_expenses_below || 0,
        });
      }
    } catch (err) {
      console.error("Error fetching application settings:", err);
      addToast('Failed to load application settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      await api.put('/admin/settings', formData);
      addToast('Application settings updated successfully', 'success');
    } catch (err) {
      console.error("Error updating application settings:", err);
      addToast(err.response?.data?.error?.message || 'Failed to update settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-4 animate-pulse p-4 max-w-3xl">
        <div className="h-8 bg-surface-container-high rounded w-1/4 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-12 bg-surface-container rounded"></div>
          <div className="h-12 bg-surface-container rounded"></div>
          <div className="h-12 bg-surface-container rounded"></div>
          <div className="h-12 bg-surface-container rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm w-full">
      <h2 className="font-title-lg text-title-lg font-bold text-on-surface mb-6 border-b border-outline-variant pb-3">
        Application Settings
      </h2>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-md">
        
        <div className="flex flex-col gap-xs">
          <label className="text-label-md font-bold text-on-surface">Application Name</label>
          <input 
            type="text" 
            name="app_name" 
            value={formData.app_name} 
            onChange={handleChange}
            required
            className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all w-full"
            placeholder="TransitOps ERP"
          />
          <p className="text-body-sm text-on-surface-variant">This name is displayed in the navigation bar and emails.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-md mt-2">
          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">Maintenance Alert Days</label>
            <input 
              type="number" 
              name="maintenance_alert_days" 
              value={formData.maintenance_alert_days} 
              onChange={handleChange}
              min="1"
              required
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all w-full"
            />
            <p className="text-body-sm text-on-surface-variant">Days before maintenance is due to trigger alerts.</p>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">License Expiry Alert Days</label>
            <input 
              type="number" 
              name="license_expiry_alert_days" 
              value={formData.license_expiry_alert_days} 
              onChange={handleChange}
              min="1"
              required
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all w-full"
            />
            <p className="text-body-sm text-on-surface-variant">Days before document expiry to trigger alerts.</p>
          </div>

          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">Max Trip Duration (Hours)</label>
            <input 
              type="number" 
              name="max_trip_duration_hours" 
              value={formData.max_trip_duration_hours} 
              onChange={handleChange}
              min="1"
              required
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all w-full"
            />
          </div>

          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">Auto-Approve Expenses Below</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-outline">$</span>
              <input 
                type="number" 
                step="0.01"
                name="auto_approve_expenses_below" 
                value={formData.auto_approve_expenses_below} 
                onChange={handleChange}
                min="0"
                required
                className="h-11 pl-8 pr-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all w-full"
              />
            </div>
            <p className="text-body-sm text-on-surface-variant">Expenses below this amount bypass manual approval.</p>
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6 border-t border-outline-variant pt-4">
          <button 
            type="button" 
            onClick={fetchSettings}
            disabled={saving}
            className="px-5 py-2.5 rounded text-on-surface hover:bg-surface-container transition-colors font-bold text-body-sm"
          >
            Reset
          </button>
          <button 
            type="submit" 
            disabled={saving}
            className="bg-primary text-on-primary px-6 py-2.5 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex items-center gap-2 shadow-sm disabled:opacity-50"
          >
            {saving && <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>}
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
};

export default ApplicationSettings;
