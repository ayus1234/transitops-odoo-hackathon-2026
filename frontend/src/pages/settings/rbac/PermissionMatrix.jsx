import React, { useState, useEffect } from 'react';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';

const PermissionMatrix = () => {
  const { addToast } = useToast();
  const [matrix, setMatrix] = useState([]);
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
      const [matrixRes, rolesRes] = await Promise.all([
        api.get('/settings/permissions'),
        api.get('/settings/roles')
      ]);
      setMatrix(matrixRes.data || []);
      setRoles(rolesRes.data || []);
      if (rolesRes.data?.length > 0) {
        setSelectedRoleId(rolesRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
      addToast('Failed to load permission matrix', 'error');
    } finally {
      setLoading(false);
    }
  };

  const selectedRole = roles.find(r => r.id === selectedRoleId);

  const hasPermission = (module, action) => {
    if (!selectedRole || !selectedRole.permissions) return false;
    return selectedRole.permissions[module]?.includes(action);
  };

  const togglePermission = async (module, action, currentlyHas) => {
    if (!selectedRole) return;

    try {
      setUpdating(true);
      const newPermissions = { ...selectedRole.permissions };
      
      if (!newPermissions[module]) {
        newPermissions[module] = [];
      }

      if (currentlyHas) {
        newPermissions[module] = newPermissions[module].filter(a => a !== action);
      } else {
        newPermissions[module] = [...newPermissions[module], action];
      }

      await api.put(`/settings/custom-roles/${selectedRole.id}`, {
        permissions: newPermissions
      });
      
      // Update local state without full reload
      const updatedRoles = roles.map(r => 
        r.id === selectedRole.id ? { ...r, permissions: newPermissions } : r
      );
      setRoles(updatedRoles);
      addToast(`Permission updated successfully`, 'success');
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to update permission', 'error');
    } finally {
      setUpdating(false);
    }
  };

  const kpis = [
    { label: 'Total Roles', value: roles.length, icon: 'badge' },
    { label: 'Total Modules', value: matrix.length, icon: 'view_module' },
    { label: 'Custom Roles', value: roles.filter(r => r.is_custom).length, icon: 'manufacturing' },
  ];

  if (loading) {
    return (
      <div className="flex flex-col gap-4 animate-pulse">
        <div className="flex gap-4 mb-4">
          {[1,2,3].map(i => <div key={i} className="h-24 bg-surface-container rounded-xl flex-1"></div>)}
        </div>
        <div className="h-12 bg-surface-container rounded w-full"></div>
        <div className="h-64 bg-surface-container rounded w-full"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-md h-full min-w-0 max-w-7xl">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-md">
        {kpis.map((kpi, i) => (
          <div key={i} className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
            <div className="w-12 h-12 rounded-full bg-primary-container text-primary flex items-center justify-center shrink-0">
              <span className="material-symbols-outlined">{kpi.icon}</span>
            </div>
            <div>
              <p className="text-body-sm text-on-surface-variant font-bold">{kpi.label}</p>
              <h3 className="text-headline-md font-bold text-on-surface">{kpi.value}</h3>
            </div>
          </div>
        ))}
      </div>

      {/* Role Selector */}
      <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="font-title-md font-bold text-on-surface">Role Matrix Configurations</h3>
            <p className="text-body-sm text-on-surface-variant">Select a role to view or modify its permissions</p>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {roles.map(role => (
            <button
              key={role.id}
              onClick={() => setSelectedRoleId(role.id)}
              className={`px-4 py-2 rounded-full font-bold text-body-sm transition-all border flex items-center gap-1 ${
                selectedRoleId === role.id 
                  ? 'bg-primary text-on-primary border-primary shadow-sm' 
                  : 'bg-surface-container-lowest text-on-surface-variant border-outline-variant hover:bg-surface-container-low'
              }`}
            >
              {role.name}
              {role.is_custom && <span className="material-symbols-outlined text-[14px]">manufacturing</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Matrix Table */}
      {selectedRole && (
        <div className="bg-surface border border-outline-variant rounded-xl shadow-sm overflow-hidden flex flex-col min-w-0 mb-12">
          <div className="p-md border-b border-outline-variant bg-surface-container-low flex justify-between items-center">
            <div>
              <h3 className="font-title-md font-bold text-on-surface flex items-center gap-2">
                Permissions for {selectedRole.name}
                {!selectedRole.is_custom && <span className="bg-surface-variant text-on-surface-variant px-2 py-0.5 rounded text-xs">System Default</span>}
              </h3>
            </div>
            {updating && <span className="material-symbols-outlined text-primary animate-spin">sync</span>}
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[800px]">
              <thead>
                <tr className="bg-surface-container-lowest text-label-caps text-on-surface-variant uppercase border-b border-outline-variant">
                  <th className="px-md py-4 font-bold w-48">Module</th>
                  <th className="px-md py-4 font-bold">Configured Permissions</th>
                </tr>
              </thead>
              <tbody className="text-body-sm">
                {matrix.map((row) => (
                  <tr key={row.module} className="border-b border-outline-variant hover:bg-surface-container-lowest transition-colors">
                    <td className="px-md py-4 align-top">
                      <p className="font-bold text-on-surface capitalize">{row.module.replace('_', ' ')}</p>
                    </td>
                    <td className="px-md py-4">
                      <div className="flex flex-wrap gap-3">
                        {row.permissions.map(action => {
                          const hasPerm = hasPermission(row.module, action);
                          
                          return (
                            <button
                              key={action}
                              disabled={updating}
                              onClick={() => togglePermission(row.module, action, hasPerm)}
                              className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-all border ${
                                hasPerm 
                                  ? `bg-primary-container text-primary border-primary/30 hover:bg-error-container hover:text-error hover:border-error/30` 
                                  : `bg-surface-container-lowest text-outline border-outline-variant hover:bg-surface-container hover:text-on-surface`
                              }`}
                            >
                              <span className="material-symbols-outlined text-[16px]">
                                {hasPerm ? 'check_circle' : 'radio_button_unchecked'}
                              </span>
                              <span className="font-bold capitalize">{action}</span>
                            </button>
                          );
                        })}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default PermissionMatrix;
