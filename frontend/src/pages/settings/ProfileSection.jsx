import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import api from '../../services/api';

const ProfileSection = () => {
  const { user } = useAuth();
  const { addToast } = useToast();
  
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone_number: user?.phone_number || '',
  });

  const [saving, setSaving] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      // Assuming there is a general profile update endpoint or reusing the admin endpoint
      await api.put(`/admin/users/${user.id}`, formData);
      addToast('Profile updated successfully', 'success');
      // In a real app we might want to update the AuthContext user here
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm w-full">
      <h2 className="font-title-lg text-title-lg font-bold text-on-surface mb-6 border-b border-outline-variant pb-3">
        My Profile
      </h2>
      
      <div className="flex items-center gap-6 mb-8 bg-surface-container-low p-6 rounded-xl border border-outline-variant">
        <div className="w-20 h-20 rounded-full bg-primary text-on-primary flex items-center justify-center font-display-sm text-display-sm font-bold shadow-sm">
          {user.first_name?.[0]}{user.last_name?.[0]}
        </div>
        <div>
          <h3 className="font-headline-sm text-headline-sm font-bold text-on-surface">{user.full_name}</h3>
          <p className="text-body-md text-on-surface-variant mb-2">{user.email}</p>
          <span className="bg-secondary-container text-secondary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
            {user.role?.name || user.role}
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-md">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">First Name</label>
            <input 
              type="text" 
              name="first_name" 
              value={formData.first_name} 
              onChange={handleChange}
              required
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
            />
          </div>
          
          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">Last Name</label>
            <input 
              type="text" 
              name="last_name" 
              value={formData.last_name} 
              onChange={handleChange}
              required
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
            />
          </div>

          <div className="flex flex-col gap-xs md:col-span-2">
            <label className="text-label-md font-bold text-on-surface">Phone Number</label>
            <input 
              type="tel" 
              name="phone_number" 
              value={formData.phone_number} 
              onChange={handleChange}
              className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 mt-6 border-t border-outline-variant pt-4">
          <button 
            type="submit" 
            disabled={saving}
            className="bg-primary text-on-primary px-6 py-2.5 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex items-center gap-2 shadow-sm disabled:opacity-50"
          >
            {saving && <span className="material-symbols-outlined text-[18px] animate-spin">sync</span>}
            Save Profile
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProfileSection;
