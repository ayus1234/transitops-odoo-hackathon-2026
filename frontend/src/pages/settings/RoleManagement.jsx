import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import RoleModal from './RoleModal';
import ConfirmDeleteDialog from '../../components/ui/ConfirmDeleteDialog';

const RoleManagement = ({ modalAction, onModalHandled }) => {
  const { addToast } = useToast();
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Modals
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  
  // Delete Dialog
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const res = await api.get('/admin/roles');
      setRoles(res.data || []);
    } catch (err) {
      addToast('Failed to load roles', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const openCreateModal = () => {
    setSelectedRole(null);
    setIsModalOpen(true);
  };

  useEffect(() => {
    if (modalAction === '/settings/roles/new') {
      openCreateModal();
      if (onModalHandled) onModalHandled();
    }
  }, [modalAction, onModalHandled]);

  const openEditModal = (role) => {
    setSelectedRole(role);
    setIsModalOpen(true);
  };

  const openDeleteDialog = (role) => {
    setRoleToDelete(role);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteRole = async () => {
    if (!roleToDelete) return;
    try {
      setIsDeleting(true);
      await api.delete(`/admin/roles/${roleToDelete.id}`);
      addToast('Role deleted successfully', 'success');
      fetchRoles();
      setIsDeleteDialogOpen(false);
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to delete role', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const getPermissionCount = (permissions) => {
    if (!permissions) return 0;
    return Object.values(permissions).reduce((acc, actions) => acc + (actions?.length || 0), 0);
  };

  return (
    <div className="flex flex-col gap-md h-full min-w-0">
      <div className="flex justify-between items-end w-full border-b border-outline-variant pb-4">
        <div>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">Role Management</h2>
          <p className="text-body-sm text-on-surface-variant">Define enterprise roles and policies</p>
        </div>
        <button onClick={openCreateModal} className="bg-primary text-on-primary px-4 py-2 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto shadow-sm">
          <span className="material-symbols-outlined text-[18px]">add</span>
          Create Role
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md mt-2">
        {loading ? (
          [...Array(4)].map((_, i) => (
            <div key={i} className="bg-surface border border-outline-variant rounded-xl p-md h-40 animate-pulse">
              <div className="h-6 bg-slate-200 rounded w-1/2 mb-4"></div>
              <div className="h-4 bg-slate-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-slate-200 rounded w-1/4"></div>
            </div>
          ))
        ) : (
          roles.map((role) => {
            const isSystem = ['Fleet Manager', 'Driver', 'Safety Officer', 'Financial Analyst'].includes(role.name);
            const permCount = getPermissionCount(role.permissions);
            
            return (
              <div key={role.id} className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm flex flex-col hover:border-primary/50 transition-colors group">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-title-md font-bold text-on-surface flex items-center gap-2">
                    {role.name}
                    {isSystem && (
                      <span className="bg-surface-container-high text-outline px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">System</span>
                    )}
                  </h3>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                    <button onClick={() => openEditModal(role)} className="p-1 rounded text-outline hover:bg-primary-container hover:text-primary transition-colors" title="Edit Role">
                      <span className="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    {!isSystem && (
                      <button onClick={() => openDeleteDialog(role)} className="p-1 rounded text-outline hover:bg-error-container hover:text-error transition-colors" title="Delete Role">
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    )}
                  </div>
                </div>
                
                <p className="text-body-sm text-on-surface-variant flex-1">
                  {isSystem 
                    ? "System-defined role with restricted deletion policies." 
                    : "Custom role created for specific organizational needs."}
                </p>
                
                <div className="mt-4 flex items-center justify-between border-t border-outline-variant pt-3">
                  <span className="text-body-sm font-bold text-secondary flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px]">key</span>
                    {permCount} Permissions
                  </span>
                  <span className="text-xs text-outline">
                    ID: {role.id.split('-')[0]}...
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      <RoleModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        role={selectedRole}
        onSave={() => {setIsModalOpen(false); fetchRoles();}}
      />

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteRole}
        title="Delete Role"
        message={`Are you sure you want to delete the role "${roleToDelete?.name}"? This action cannot be undone and will fail if users are assigned to it.`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default RoleManagement;
