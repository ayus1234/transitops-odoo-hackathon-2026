import React, { useState, useEffect } from 'react';
import Modal from '../../components/ui/Modal';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const RoleModal = ({ isOpen, onClose, role, onSave }) => {
  const { addToast } = useToast();
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    permissions: {}
  });

  useEffect(() => {
    if (isOpen) {
      if (role) {
        setFormData({
          name: role.name || '',
          permissions: role.permissions || {}
        });
      } else {
        setFormData({
          name: '',
          permissions: {}
        });
      }
    }
  }, [isOpen, role]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name) return;
    
    try {
      setSaving(true);
      if (role) {
        await api.put(`/admin/roles/${role.id}`, formData);
        addToast('Role updated successfully', 'success');
      } else {
        await api.post('/admin/roles', formData);
        addToast('Role created successfully', 'success');
      }
      onSave();
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to save role', 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={role ? "Edit Role" : "Create New Role"}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-md">
        <div className="flex flex-col gap-xs">
          <label className="text-label-md font-bold text-on-surface">Role Name *</label>
          <input 
            type="text" 
            name="name" 
            value={formData.name} 
            onChange={handleChange} 
            required
            placeholder="e.g. Dispatcher"
            className="h-11 px-4 bg-surface-container-lowest border border-outline-variant rounded-lg text-body-md focus:ring-2 focus:ring-primary outline-none transition-all w-full"
          />
        </div>
        
        {role && (
          <div className="bg-surface-container-low p-3 rounded border border-outline-variant mt-2">
            <p className="text-body-sm text-on-surface-variant flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">info</span>
              Permissions for this role can be managed in the Permissions matrix tab.
            </p>
          </div>
        )}

        <div className="flex justify-end gap-2 mt-4 pt-4 border-t border-outline-variant">
          <button type="button" onClick={onClose} disabled={saving} className="px-4 py-2 text-on-surface hover:bg-surface-container rounded transition-colors font-bold text-body-sm">
            Cancel
          </button>
          <button type="submit" disabled={saving || !formData.name} className="px-4 py-2 bg-primary text-on-primary rounded font-bold text-body-sm hover:opacity-90 disabled:opacity-50 transition-colors flex items-center gap-2">
            {saving ? <span className="material-symbols-outlined text-[16px] animate-spin">sync</span> : null}
            {role ? 'Save Changes' : 'Create Role'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default RoleModal;
