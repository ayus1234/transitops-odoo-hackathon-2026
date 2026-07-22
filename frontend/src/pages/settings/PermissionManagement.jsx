import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const PermissionManagement = () => {
  const { addToast } = useToast();
  const [permissions, setPermissions] = useState([]);
  const [roles, setRoles] = useState([]);
  const [selectedRoleId, setSelectedRoleId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [permRes, roleRes] = await Promise.all([
        api.get('/admin/permissions'),
        api.get('/admin/roles')
      ]);
      setPermissions(permRes.data || []);
      setRoles(roleRes.data || []);
      
      // Auto-select first role if none selected
      if (roleRes.data?.length > 0 && !selectedRoleId) {
        setSelectedRoleId(roleRes.data[0].id);
      }
    } catch (err) {
      console.error("Error fetching permissions:", err);
      addToast('Failed to load permission matrix', 'error');
    } finally {
      setLoading(false);
    }
  };

  const selectedRole = roles.find(r => r.id === selectedRoleId);

  // Group permissions by resource for easier display
  const groupedPermissions = permissions.reduce((acc, perm) => {
    if (!acc[perm.resource]) acc[perm.resource] = [];
    acc[perm.resource].push(perm);
    return acc;
  }, {});

  const hasPermission = (resource, action) => {
    if (!selectedRole || !selectedRole.permissions) return false;
    // Check if the role has "all" permissions (Super Admin case usually hardcoded, but let's check explicit)
    if (selectedRole.permissions['all']?.includes('read') && selectedRole.permissions['all']?.includes('create')) return true;
    
    return selectedRole.permissions[resource]?.includes(action);
  };

  const togglePermission = async (resource, action, currentlyHas) => {
    if (!selectedRoleId || !selectedRole) return;
    
    try {
      setUpdating(true);
      if (currentlyHas) {
        await api.delete('/admin/permissions/remove', { 
          data: { role_id: selectedRoleId, resource, action }
        });
      } else {
        await api.post('/admin/permissions/assign', { 
          role_id: selectedRoleId, resource, action 
        });
      }
      
      // Refresh roles to get updated permissions
      const roleRes = await api.get('/admin/roles');
      setRoles(roleRes.data || []);
      addToast(`Permission ${currentlyHas ? 'removed' : 'assigned'} successfully`, 'success');
      
    } catch (err) {
      addToast(err.response?.data?.error?.message || 'Failed to update permission', 'error');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col gap-4 animate-pulse p-4">
        <div className="h-8 bg-surface-container-high rounded w-1/4 mb-4"></div>
        <div className="h-12 bg-surface-container rounded w-full"></div>
        <div className="h-64 bg-surface-container rounded w-full"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-md h-full min-w-0 max-w-5xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4 border-b border-outline-variant pb-4">
        <div>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">Permission Matrix</h2>
          <p className="text-body-sm text-on-surface-variant">Configure granular access control for roles</p>
        </div>
      </div>

      {/* Role Selector */}
      <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm">
        <label className="text-label-md font-bold text-on-surface block mb-2">Select Role to Manage</label>
        <div className="flex flex-wrap gap-2">
          {roles.map(role => (
            <button
              key={role.id}
              onClick={() => setSelectedRoleId(role.id)}
              className={`px-4 py-2 rounded-full font-bold text-body-sm transition-all border ${
                selectedRoleId === role.id 
                  ? 'bg-primary text-on-primary border-primary shadow-sm' 
                  : 'bg-surface-container-lowest text-on-surface-variant border-outline-variant hover:bg-surface-container-low'
              }`}
            >
              {role.name}
            </button>
          ))}
        </div>
      </div>

      {/* Matrix */}
      {selectedRole && (
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0 mt-2">
          <div className="p-md border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
            <h3 className="font-title-md font-bold text-on-surface">
              Capabilities for {selectedRole.name}
            </h3>
            {updating && <span className="material-symbols-outlined text-[20px] text-primary animate-spin">sync</span>}
          </div>
          
          <div className="divide-y divide-outline-variant">
            {Object.entries(groupedPermissions).map(([resource, perms]) => (
              <div key={resource} className="p-md hover:bg-surface-container-lowest transition-colors flex flex-col md:flex-row gap-4 md:items-center">
                <div className="w-48 shrink-0">
                  <h4 className="font-bold text-on-surface capitalize">{resource}</h4>
                  <p className="text-xs text-on-surface-variant">Manage {resource} access</p>
                </div>
                
                <div className="flex flex-wrap gap-3 flex-1">
                  {perms.map(perm => {
                    const hasPerm = hasPermission(perm.resource, perm.action);
                    return (
                      <button
                        key={perm.id}
                        onClick={() => togglePermission(perm.resource, perm.action, hasPerm)}
                        disabled={updating || selectedRole.name === 'Fleet Manager'} // Usually Fleet Manager is super admin, prevent removing
                        className={`flex items-center gap-2 px-3 py-1.5 rounded border transition-all ${
                          hasPerm 
                            ? 'bg-primary-container text-primary border-primary/30 hover:bg-error-container hover:text-error hover:border-error/30' 
                            : 'bg-surface-container-lowest text-outline border-outline-variant hover:bg-surface-container hover:text-on-surface'
                        } ${selectedRole.name === 'Fleet Manager' ? 'opacity-70 cursor-not-allowed' : ''}`}
                        title={hasPerm ? "Click to remove" : "Click to assign"}
                      >
                        <span className="material-symbols-outlined text-[16px]">
                          {hasPerm ? 'check_box' : 'check_box_outline_blank'}
                        </span>
                        <span className="font-bold text-body-sm capitalize">{perm.action}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          
          {selectedRole.name === 'Fleet Manager' && (
            <div className="p-sm bg-primary-container/30 text-primary text-center text-body-sm font-bold border-t border-primary/20">
              Fleet Manager is a System Super Admin. Permissions cannot be restricted.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PermissionManagement;
