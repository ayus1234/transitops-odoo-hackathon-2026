import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';

const CustomRoles = () => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const cloneRoleId = location.state?.cloneRoleId;

  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent_role_id: '',
    template: ''
  });

  const [roles, setRoles] = useState([]);
  const [templates, setTemplates] = useState({});
  const [selectedPermissions, setSelectedPermissions] = useState({});
  const [matrix, setMatrix] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [rolesRes, templatesRes, matrixRes] = await Promise.all([
          api.get('/settings/roles'),
          api.get('/settings/permissions/templates'),
          api.get('/settings/permissions')
        ]);
        setRoles(rolesRes.data || []);
        setTemplates(templatesRes.data || {});
        setMatrix(matrixRes.data || []);

        if (cloneRoleId && rolesRes.data) {
          const baseRole = rolesRes.data.find(r => r.id === cloneRoleId);
          if (baseRole) {
            setFormData(prev => ({
              ...prev,
              name: `Copy of ${baseRole.name}`,
              description: baseRole.description,
              parent_role_id: baseRole.id
            }));
            setSelectedPermissions(baseRole.permissions || {});
          }
        }
      } catch (err) {
        addToast('Failed to load dependencies', 'error');
      }
    };
    fetchData();
  }, [cloneRoleId, addToast]);

  const handleTemplateChange = (templateName) => {
    setFormData(prev => ({ ...prev, template: templateName }));
    if (templates[templateName]) {
      // Deep copy the template permissions to avoid mutability issues
      setSelectedPermissions(JSON.parse(JSON.stringify(templates[templateName])));
    }
  };

  const hasPermission = (module, action) => {
    return selectedPermissions[module]?.includes(action);
  };

  const togglePermission = (module, action, currentlyHas) => {
    const newPermissions = { ...selectedPermissions };
    
    if (!newPermissions[module]) {
      newPermissions[module] = [];
    }

    if (currentlyHas) {
      newPermissions[module] = newPermissions[module].filter(a => a !== action);
      if (newPermissions[module].length === 0) {
        delete newPermissions[module];
      }
    } else {
      newPermissions[module] = [...newPermissions[module], action];
    }
    
    setSelectedPermissions(newPermissions);
    // Clear template selection since it's customized now
    setFormData(prev => ({ ...prev, template: '' }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name) {
      addToast('Role name is required', 'error');
      return;
    }

    try {
      setSaving(true);
      const payload = {
        name: formData.name,
        description: formData.description,
        permissions: selectedPermissions,
        parent_role_id: formData.parent_role_id || null,
        is_custom: true
      };

      await api.post('/settings/custom-roles', payload);
      addToast('Custom role created successfully', 'success');
      navigate('/settings/roles');
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to create custom role', 'error');
    } finally {
      setSaving(false);
    }
  };

  const getPermissionCount = () => {
    return Object.values(selectedPermissions).reduce((acc, actions) => acc + (actions?.length || 0), 0);
  };

  return (
    <div className="flex flex-col gap-md h-full min-w-0 max-w-4xl">
      <div className="flex justify-between items-end w-full border-b border-outline-variant pb-4">
        <div>
          <button onClick={() => navigate('/settings/roles')} className="text-primary font-bold text-body-sm flex items-center gap-1 mb-2 hover:underline">
            <span className="material-symbols-outlined text-[16px]">arrow_back</span> Back to Roles
          </button>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">Create Custom Role</h2>
          <p className="text-body-sm text-on-surface-variant">Design a specialized role with granular access controls</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6 mt-2 pb-12">
        <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm">
          <h3 className="font-title-md font-bold text-on-surface mb-4">Role Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-label-md font-bold text-on-surface block mb-1">Role Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData(prev => ({...prev, name: e.target.value}))}
                placeholder="e.g. Regional Fleet Supervisor"
                className="w-full h-10 px-3 bg-surface-container border border-outline-variant rounded text-sm focus:ring-2 focus:ring-primary outline-none transition-all"
              />
            </div>
            <div>
              <label className="text-label-md font-bold text-on-surface block mb-1">Inherit From (Parent Role)</label>
              <select
                value={formData.parent_role_id}
                onChange={(e) => setFormData(prev => ({...prev, parent_role_id: e.target.value}))}
                className="w-full h-10 px-3 bg-surface-container border border-outline-variant rounded text-sm focus:ring-2 focus:ring-primary outline-none transition-all"
              >
                <option value="">No Parent (Standalone)</option>
                {roles.filter(r => !r.is_custom).map(role => (
                  <option key={role.id} value={role.id}>{role.name}</option>
                ))}
              </select>
              <p className="text-xs text-outline mt-1">Inherits base permissions automatically.</p>
            </div>
            <div className="md:col-span-2">
              <label className="text-label-md font-bold text-on-surface block mb-1">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({...prev, description: e.target.value}))}
                placeholder="Brief description of responsibilities..."
                className="w-full h-10 px-3 bg-surface-container border border-outline-variant rounded text-sm focus:ring-2 focus:ring-primary outline-none transition-all"
              />
            </div>
          </div>
        </div>

        <div className="bg-surface border border-outline-variant rounded-xl p-md shadow-sm">
          <div className="flex justify-between items-start mb-4 border-b border-outline-variant pb-4">
            <div>
              <h3 className="font-title-md font-bold text-on-surface">Permission Configuration</h3>
              <p className="text-body-sm text-on-surface-variant">Start from a template or configure manually.</p>
            </div>
            <div className="bg-primary-container text-primary px-3 py-1 rounded font-bold text-body-sm">
              {getPermissionCount()} Nodes Configured
            </div>
          </div>

          <div className="mb-6">
            <label className="text-label-md font-bold text-on-surface block mb-2">Apply Template</label>
            <div className="flex flex-wrap gap-2">
              {Object.keys(templates).map(template => (
                <button
                  key={template}
                  type="button"
                  onClick={() => handleTemplateChange(template)}
                  className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all border ${
                    formData.template === template 
                      ? 'bg-secondary text-on-secondary border-secondary' 
                      : 'bg-surface-container-low text-on-surface border-outline-variant hover:bg-surface-container'
                  }`}
                >
                  {template}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden mt-4">
             <div className="overflow-x-auto">
               <table className="w-full text-left border-collapse min-w-[800px]">
                 <thead>
                   <tr className="bg-surface-container-low text-label-caps text-on-surface-variant uppercase border-b border-outline-variant">
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
                                 type="button"
                                 onClick={() => togglePermission(row.module, action, hasPerm)}
                                 className={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-all border ${
                                   hasPerm 
                                     ? 'bg-primary-container text-primary border-primary/30 hover:bg-error-container hover:text-error hover:border-error/30' 
                                     : 'bg-surface-container-lowest text-outline border-outline-variant hover:bg-surface-container hover:text-on-surface'
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
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-outline-variant">
          <button 
            type="button"
            onClick={() => navigate('/settings/roles')}
            className="px-6 py-2 rounded font-bold text-body-sm border border-outline-variant hover:bg-surface-container transition-colors text-on-surface"
          >
            Cancel
          </button>
          <button 
            type="submit"
            disabled={saving}
            className="px-6 py-2 rounded font-bold text-body-sm bg-primary text-on-primary hover:opacity-90 disabled:opacity-50 transition-colors flex items-center gap-2"
          >
            {saving ? <span className="material-symbols-outlined animate-spin text-[18px]">sync</span> : <span className="material-symbols-outlined text-[18px]">save</span>}
            Save Custom Role
          </button>
        </div>
      </form>
    </div>
  );
};

export default CustomRoles;
