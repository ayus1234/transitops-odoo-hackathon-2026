import React, { useState, useEffect } from 'react';
import Modal from '../../../components/ui/Modal';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';

const UserRoleModal = ({ isOpen, onClose, user, onSave }) => {
  const { addToast } = useToast();
  const [saving, setSaving] = useState(false);
  const [roles, setRoles] = useState([]);
  const [loadingRoles, setLoadingRoles] = useState(false);
  
  const [formData, setFormData] = useState({
    primary_role_id: '',
    additional_role_ids: []
  });

  useEffect(() => {
    if (isOpen) {
      if (user) {
        setFormData({
          primary_role_id: user.role_id || '',
          additional_role_ids: user.additional_roles?.map(r => r.id) || []
        });
      }
      fetchRoles();
    }
  }, [isOpen, user]);

  const fetchRoles = async () => {
    try {
      setLoadingRoles(true);
      const res = await api.get('/settings/roles');
      setRoles(res.data || []);
    } catch (err) {
      addToast('Failed to load roles', 'error');
    } finally {
      setLoadingRoles(false);
    }
  };

  const handlePrimaryRoleChange = (e) => {
    setFormData(prev => ({ ...prev, primary_role_id: e.target.value }));
  };

  const handleAdditionalRoleToggle = (roleId) => {
    setFormData(prev => {
      const exists = prev.additional_role_ids.includes(roleId);
      return {
        ...prev,
        additional_role_ids: exists 
          ? prev.additional_role_ids.filter(id => id !== roleId)
          : [...prev.additional_role_ids, roleId]
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return;
    
    try {
      setSaving(true);
      await api.post('/settings/user-roles', {
        user_id: user.id,
        primary_role_id: formData.primary_role_id,
        additional_role_ids: formData.additional_role_ids
      });
      addToast('Roles assigned successfully', 'success');
      onSave();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to assign roles', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign User Roles">
      <div className="flex flex-col gap-6">
        <div className="bg-surface-container-low p-4 rounded-lg flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-lg">
            {user.first_name[0]}{user.last_name[0]}
          </div>
          <div>
            <p className="font-bold text-on-surface text-body-lg">{user.full_name}</p>
            <p className="text-body-sm text-on-surface-variant">{user.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-md">
          <div className="flex flex-col gap-xs">
            <label className="text-label-md font-bold text-on-surface">Primary Role *</label>
            <select 
              value={formData.primary_role_id} 
              onChange={handlePrimaryRoleChange} 
              required 
              disabled={loadingRoles}
              className="h-10 px-3 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
            >
              <option value="" disabled>Select Primary Role</option>
              {roles.map(r => (
                <option key={r.id} value={r.id}>{r.name}</option>
              ))}
            </select>
            <p className="text-xs text-on-surface-variant">This role dictates primary UI layout and access.</p>
          </div>

          <div className="flex flex-col gap-xs mt-4">
            <label className="text-label-md font-bold text-on-surface">Additional Roles</label>
            <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-3 max-h-60 overflow-y-auto custom-scrollbar flex flex-col gap-2">
              {roles.filter(r => r.id !== formData.primary_role_id).map(r => (
                <label key={r.id} className="flex items-center gap-2 p-2 hover:bg-surface-container-low rounded cursor-pointer transition-colors">
                  <input 
                    type="checkbox"
                    checked={formData.additional_role_ids.includes(r.id)}
                    onChange={() => handleAdditionalRoleToggle(r.id)}
                    className="w-4 h-4 text-primary bg-surface border-outline-variant rounded focus:ring-primary focus:ring-2"
                  />
                  <span className="text-body-sm font-bold text-on-surface flex-1">{r.name}</span>
                  {r.is_custom ? (
                     <span className="bg-tertiary-container/30 text-tertiary px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">Custom</span>
                  ) : (
                     <span className="bg-surface-variant text-outline px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">System</span>
                  )}
                </label>
              ))}
            </div>
            <p className="text-xs text-on-surface-variant">Additional roles augment primary permissions additively.</p>
          </div>

          <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-outline-variant">
            <button type="button" onClick={onClose} disabled={saving} className="px-4 py-2 text-on-surface hover:bg-surface-container rounded transition-colors font-bold text-body-sm">Cancel</button>
            <button type="submit" disabled={saving} className="px-4 py-2 bg-primary text-on-primary rounded font-bold text-body-sm hover:opacity-90 disabled:opacity-50 transition-colors flex items-center gap-2">
              {saving ? <span className="material-symbols-outlined text-[16px] animate-spin">sync</span> : null}
              Save Assignments
            </button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default UserRoleModal;
