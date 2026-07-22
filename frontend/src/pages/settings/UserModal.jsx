import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const UserModal = ({ isOpen, onClose, user, onSave }) => {
  const { addToast } = useToast();
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    role_id: ''
  });
  
  const [roles, setRoles] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);

  // New password state
  const [newPassword, setNewPassword] = useState('');
  const [resettingPwd, setResettingPwd] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (user) {
        setFormData({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          phone_number: user.phone_number || '',
          role_id: user.role_id || ''
        });
        setNewPassword('');
      }
      fetchRoles();
    }
  }, [isOpen, user]);

  const fetchRoles = async () => {
    try {
      setLoadingRoles(true);
      const res = await api.get('/admin/roles');
      setRoles(res.data || []);
    } catch (err) {
      addToast('Failed to load roles', 'error');
    } finally {
      setLoadingRoles(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return; // Currently only editing exists, user creation wasn't in backend spec
    try {
      setSaving(true);
      await api.put(`/admin/users/${user.id}`, formData);
      addToast('User updated successfully', 'success');
      onSave();
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to update user', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!newPassword || newPassword.length < 8) {
      addToast('Password must be at least 8 characters long', 'error');
      return;
    }
    
    try {
      setResettingPwd(true);
      await api.post(`/admin/users/${user.id}/reset-password`, { new_password: newPassword });
      addToast('Password reset successfully', 'success');
      setNewPassword('');
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to reset password', 'error');
    } finally {
      setResettingPwd(false);
    }
  };

  if (!user) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit User Account">
      <div className="flex flex-col gap-6">
        {/* Profile Edit Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-md">
          <div className="bg-surface-container-low p-4 rounded-lg mb-2 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-lg">
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <div>
              <p className="font-bold text-on-surface text-body-lg">{user.email}</p>
              <p className="text-body-sm text-on-surface-variant">
                Account created: {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">First Name *</label>
              <input 
                type="text" name="first_name" value={formData.first_name} onChange={handleChange} required
                className="h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Last Name *</label>
              <input 
                type="text" name="last_name" value={formData.last_name} onChange={handleChange} required
                className="h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Phone Number</label>
              <input 
                type="tel" name="phone_number" value={formData.phone_number} onChange={handleChange}
                className="h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              />
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-md font-bold text-on-surface">Role *</label>
              <select 
                name="role_id" value={formData.role_id} onChange={handleChange} required disabled={loadingRoles}
                className="h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
              >
                <option value="" disabled>Select Role</option>
                {roles.map(r => (
                  <option key={r.id} value={r.id}>{r.name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-outline-variant">
            <button type="button" onClick={onClose} disabled={saving} className="px-4 py-2 text-on-surface hover:bg-surface-container rounded transition-colors font-bold text-body-sm">Cancel</button>
            <button type="submit" disabled={saving} className="px-4 py-2 bg-primary text-on-primary rounded font-bold text-body-sm hover:opacity-90 disabled:opacity-50 transition-colors flex items-center gap-2">
              {saving ? <span className="material-symbols-outlined text-[16px] animate-spin">sync</span> : null}
              Save Profile
            </button>
          </div>
        </form>

        {/* Password Reset Section */}
        <div className="border-t border-outline-variant pt-6">
          <h3 className="font-title-sm text-title-sm font-bold text-error mb-2">Administrative Password Reset</h3>
          <p className="text-body-sm text-on-surface-variant mb-4">Set a new password for this user. They will be logged out of all active sessions.</p>
          <div className="flex gap-2">
            <input 
              type="password" 
              placeholder="New Password (min 8 chars)" 
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="h-10 px-3 flex-1 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-error outline-none transition-all"
            />
            <button 
              type="button" 
              onClick={handlePasswordReset}
              disabled={resettingPwd || newPassword.length < 8}
              className="px-4 py-2 bg-error text-on-error rounded font-bold text-body-sm hover:bg-error/90 disabled:opacity-50 transition-colors flex items-center gap-2 whitespace-nowrap"
            >
              {resettingPwd ? <span className="material-symbols-outlined text-[16px] animate-spin">sync</span> : null}
              Reset Password
            </button>
          </div>
        </div>

      </div>
    </Modal>
  );
};

export default UserModal;
