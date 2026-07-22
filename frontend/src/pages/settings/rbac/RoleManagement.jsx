import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';
import ConfirmDeleteDialog from '../../../components/ui/ConfirmDeleteDialog';

const RoleManagement = () => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Delete Dialog
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [activeAssignments, setActiveAssignments] = useState('--');

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const [rolesRes, usersRes] = await Promise.all([
        api.get('/settings/roles'),
        api.get('/admin/users?page_size=1')
      ]);
      setRoles(rolesRes.data || []);
      setActiveAssignments(usersRes.data?.pagination?.total_items || '--');
    } catch (err) {
      addToast('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const openDeleteDialog = (role) => {
    setRoleToDelete(role);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteRole = async () => {
    if (!roleToDelete) return;
    try {
      setIsDeleting(true);
      await api.delete(`/settings/roles/${roleToDelete.id}`);
      addToast('Role deleted successfully', 'success');
      fetchRoles();
      setIsDeleteDialogOpen(false);
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to delete role', 'error');
    } finally {
      setIsDeleting(false);
    }
  };

  const getPermissionCount = (permissions) => {
    if (!permissions) return 0;
    return Object.values(permissions).reduce((acc, actions) => acc + (actions?.length || 0), 0);
  };

  const systemRolesCount = roles.filter(r => !r.is_custom).length;
  const customRolesCount = roles.filter(r => r.is_custom).length;

  return (
    <div className="flex flex-col gap-md h-full min-w-0 max-w-7xl">
      <div className="flex justify-between items-end w-full border-b border-outline-variant pb-4">
        <div>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">Role Management</h2>
          <p className="text-body-sm text-on-surface-variant">Define enterprise roles and policies</p>
        </div>
        <button 
          onClick={() => navigate('/settings/custom-roles')} 
          className="bg-primary text-on-primary px-4 py-2 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto shadow-sm"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          Create Custom Role
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-md mt-2">
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-primary-container text-primary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">badge</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Total Roles</p>
            <h3 className="text-headline-md font-bold text-on-surface">{roles.length}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-secondary-container text-secondary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">admin_panel_settings</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">System Roles</p>
            <h3 className="text-headline-md font-bold text-on-surface">{systemRolesCount}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-tertiary-container text-tertiary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">manufacturing</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Custom Roles</p>
            <h3 className="text-headline-md font-bold text-on-surface">{customRolesCount}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-error-container text-error flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">groups</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Active Assignments</p>
            <h3 className="text-headline-md font-bold text-on-surface">{activeAssignments}</h3>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col min-w-0 mt-4 mb-12">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface-container-low text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                <th className="px-md py-3">Role Name</th>
                <th className="px-md py-3">Description</th>
                <th className="px-md py-3">Permissions</th>
                <th className="px-md py-3">Type</th>
                <th className="px-md py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-outline-variant animate-pulse">
                    <td className="px-md py-4"><div className="h-4 bg-surface-container-high rounded w-32"></div></td>
                    <td className="px-md py-4"><div className="h-4 bg-surface-container-high rounded w-48"></div></td>
                    <td className="px-md py-4"><div className="h-4 bg-surface-container-high rounded w-16"></div></td>
                    <td className="px-md py-4"><div className="h-4 bg-surface-container-high rounded w-20"></div></td>
                    <td className="px-md py-4 text-right"><div className="h-8 bg-surface-container-high rounded w-24 ml-auto"></div></td>
                  </tr>
                ))
              ) : roles.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-on-surface-variant">
                    <p>No roles found.</p>
                  </td>
                </tr>
              ) : roles.map(role => (
                <tr key={role.id} className="border-b border-outline-variant hover:bg-surface-container-lowest transition-colors">
                  <td className="px-md py-3 font-bold text-on-surface flex items-center gap-2">
                    {role.name}
                  </td>
                  <td className="px-md py-3 text-on-surface-variant">
                    {role.description || (role.is_custom ? 'Custom user-defined role' : 'System default role')}
                  </td>
                  <td className="px-md py-3">
                    <span className="bg-primary-container/30 text-primary px-2 py-0.5 rounded text-xs font-bold">
                      {getPermissionCount(role.permissions)} Nodes
                    </span>
                  </td>
                  <td className="px-md py-3">
                    {role.is_custom ? (
                      <span className="text-tertiary flex items-center gap-1 font-bold"><span className="material-symbols-outlined text-[16px]">manufacturing</span> Custom</span>
                    ) : (
                      <span className="text-secondary flex items-center gap-1 font-bold"><span className="material-symbols-outlined text-[16px]">verified</span> System</span>
                    )}
                  </td>
                  <td className="px-md py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button 
                        onClick={() => navigate('/settings/permissions')}
                        className="p-1.5 rounded hover:bg-surface-container-high text-outline hover:text-primary transition-colors" title="View Permissions"
                      >
                        <span className="material-symbols-outlined text-[18px]">visibility</span>
                      </button>
                      <button 
                        onClick={() => navigate('/settings/custom-roles', { state: { cloneRoleId: role.id } })}
                        className="p-1.5 rounded hover:bg-surface-container-high text-outline hover:text-primary transition-colors" title="Clone Role"
                      >
                        <span className="material-symbols-outlined text-[18px]">content_copy</span>
                      </button>
                      {role.is_custom && role.name !== 'Super Admin' && (
                        <button 
                          onClick={() => openDeleteDialog(role)}
                          className="p-1.5 rounded hover:bg-error-container text-outline hover:text-error transition-colors" title="Delete Role"
                        >
                          <span className="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <ConfirmDeleteDialog 
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onConfirm={handleDeleteRole}
        title="Delete Custom Role"
        message={`Are you sure you want to delete the role "${roleToDelete?.name}"? This action cannot be undone.`}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default RoleManagement;
