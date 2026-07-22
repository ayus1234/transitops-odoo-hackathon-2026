import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const OrganizationSettings = () => {
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    legal_name: '',
    email: '',
    phone: '',
    website: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    country: '',
    postal_code: '',
    tax_id: '',
    registration_number: '',
  });

  const [appSettingsData, setAppSettingsData] = useState({
    timezone: 'UTC',
    currency: 'USD',
    language: 'en',
    date_format: 'YYYY-MM-DD'
  });

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const [orgRes, appRes] = await Promise.all([
        api.get('/admin/organization'),
        api.get('/admin/settings')
      ]);
      
      if (orgRes.data) {
        const d = orgRes.data;
        setFormData({
          name: d.name || '',
          legal_name: d.legal_name || '',
          email: d.email || '',
          phone: d.phone || '',
          website: d.website || '',
          address_line1: d.address_line1 || '',
          address_line2: d.address_line2 || '',
          city: d.city || '',
          state: d.state || '',
          country: d.country || '',
          postal_code: d.postal_code || '',
          tax_id: d.tax_id || '',
          registration_number: d.registration_number || '',
        });
      }

      if (appRes.data) {
        const a = appRes.data;
        setAppSettingsData({
          timezone: a.timezone || 'UTC',
          currency: a.currency || 'USD',
          language: a.language || 'en',
          date_format: a.date_format || 'YYYY-MM-DD'
        });
      }

    } catch (err) {
      console.error("Error fetching organization settings:", err);
      addToast('Failed to load organization settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleOrgChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAppChange = (e) => {
    const { name, value } = e.target;
    setAppSettingsData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSaving(true);
      // Save both org details and app localisation details
      await Promise.all([
        api.put('/admin/organization', formData),
        api.put('/admin/settings', appSettingsData)
      ]);
      addToast('Organization settings updated successfully', 'success');
    } catch (err) {
      console.error("Error updating organization settings:", err);
      addToast(err.response?.data?.error?.message || 'Failed to update organization settings', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-4 animate-pulse p-4 max-w-3xl">
        <div className="h-8 bg-surface-container-high rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-surface-container rounded w-full"></div>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm max-w-5xl w-full">
      <h2 className="font-title-lg text-title-lg font-bold text-on-surface mb-6 border-b border-outline-variant pb-3">
        Organization Profile
      </h2>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-xl">
        
        {/* Company Info Section */}
        <section>
          <h3 className="font-title-md text-title-md font-bold text-on-surface mb-4">Company Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Organization Name *</label>
              <input 
                type="text" 
                name="name" 
                value={formData.name} 
                onChange={handleOrgChange}
                required
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Legal Name</label>
              <input 
                type="text" 
                name="legal_name" 
                value={formData.legal_name} 
                onChange={handleOrgChange}
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>

            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Contact Email *</label>
              <input 
                type="email" 
                name="email" 
                value={formData.email} 
                onChange={handleOrgChange}
                required
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>

            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Phone Number</label>
              <input 
                type="tel" 
                name="phone" 
                value={formData.phone} 
                onChange={handleOrgChange}
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            
            <div className="flex flex-col gap-xs md:col-span-2">
              <label className="text-label-md font-bold text-on-surface">Website</label>
              <input 
                type="url" 
                name="website" 
                value={formData.website} 
                onChange={handleOrgChange}
                placeholder="https://"
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
          </div>
        </section>

        {/* Address & Registration */}
        <section>
          <h3 className="font-title-md text-title-md font-bold text-on-surface mb-4">Address & Registration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="flex flex-col gap-xs md:col-span-2">
              <label className="text-label-md font-bold text-on-surface">Address Line 1</label>
              <input 
                type="text" 
                name="address_line1" 
                value={formData.address_line1} 
                onChange={handleOrgChange}
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            <div className="flex flex-col gap-xs md:col-span-2">
              <label className="text-label-md font-bold text-on-surface">Address Line 2</label>
              <input 
                type="text" 
                name="address_line2" 
                value={formData.address_line2} 
                onChange={handleOrgChange}
                className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">City</label>
              <input type="text" name="city" value={formData.city} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">State/Province</label>
              <input type="text" name="state" value={formData.state} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Country</label>
              <input type="text" name="country" value={formData.country} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Postal Code</label>
              <input type="text" name="postal_code" value={formData.postal_code} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Tax ID / EIN</label>
              <input type="text" name="tax_id" value={formData.tax_id} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Registration Number</label>
              <input type="text" name="registration_number" value={formData.registration_number} onChange={handleOrgChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"/>
            </div>
          </div>
        </section>

        {/* Localization */}
        <section>
          <h3 className="font-title-md text-title-md font-bold text-on-surface mb-4">Localization</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Timezone</label>
              <select name="timezone" value={appSettingsData.timezone} onChange={handleAppChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full cursor-pointer">
                <option value="UTC">UTC</option>
                <option value="US/Eastern">US/Eastern</option>
                <option value="US/Central">US/Central</option>
                <option value="US/Pacific">US/Pacific</option>
                <option value="Europe/London">Europe/London</option>
                <option value="Asia/Kolkata">Asia/Kolkata</option>
                <option value="Australia/Sydney">Australia/Sydney</option>
              </select>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Currency</label>
              <select name="currency" value={appSettingsData.currency} onChange={handleAppChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full cursor-pointer">
                <option value="USD">USD (₹)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="INR">INR (₹)</option>
                <option value="CAD">CAD (₹)</option>
                <option value="AUD">AUD (₹)</option>
              </select>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Language</label>
              <select name="language" value={appSettingsData.language} onChange={handleAppChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full cursor-pointer">
                <option value="en">English</option>
                <option value="hi">Hindi</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Date Format</label>
              <select name="date_format" value={appSettingsData.date_format} onChange={handleAppChange} className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full cursor-pointer">
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="DD-MM-YYYY">DD-MM-YYYY</option>
              </select>
            </div>
          </div>
        </section>

        <div className="flex justify-end gap-3 mt-4 border-t border-outline-variant pt-4">
          <button type="button" onClick={fetchSettings} disabled={saving} className="px-5 py-2.5 rounded text-on-surface hover:bg-surface-container transition-colors font-bold text-body-sm">
            Reset
          </button>
          <button type="submit" disabled={saving} className="bg-primary text-on-primary px-6 py-2.5 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex items-center gap-2 shadow-sm disabled:opacity-50">
            {saving && <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>}
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
};

export default OrganizationSettings;
