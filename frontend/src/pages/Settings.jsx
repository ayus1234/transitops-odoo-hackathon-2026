import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ApplicationSettings from './settings/ApplicationSettings';
import OrganizationSettings from './settings/OrganizationSettings';
import ProfileSection from './settings/ProfileSection';

// RBAC Components
import PermissionMatrix from './settings/rbac/PermissionMatrix';
import RoleManagement from './settings/rbac/RoleManagement';
import CustomRoles from './settings/rbac/CustomRoles';
import UserRoleAssignment from './settings/rbac/UserRoleAssignment';

const Settings = () => {
  const { user } = useAuth();
  
  const navigate = useNavigate();
  const location = useLocation();

  // Navigation Tabs
  const TABS = [
    { id: 'profile', path: '/settings/profile', label: 'My Profile', icon: 'person', component: ProfileSection },
    { id: 'permissions', path: '/settings/permissions', label: 'Permission Matrix', icon: 'grid_view', component: PermissionMatrix, requireAdmin: true },
    { id: 'roles', path: '/settings/roles', label: 'Role Management', icon: 'badge', component: RoleManagement, requireAdmin: true },
    { id: 'custom-roles', path: '/settings/custom-roles', label: 'Custom Roles', icon: 'manufacturing', component: CustomRoles, requireAdmin: true },
    { id: 'user-roles', path: '/settings/user-roles', label: 'User Roles', icon: 'manage_accounts', component: UserRoleAssignment, requireAdmin: true },
    { id: 'app', path: '/settings/app', label: 'Application', icon: 'settings_applications', component: ApplicationSettings, requireAdmin: true },
    { id: 'org', path: '/settings/org', label: 'Organization', icon: 'domain', component: OrganizationSettings, requireAdmin: true },
  ];

  // The backend uses 'Fleet Manager' for admin tasks
  const isAdmin = user?.role?.name === 'Fleet Manager' || user?.role?.name === 'Super Admin' || user?.role === 'Fleet Manager' || user?.role === 'Super Admin';

  const availableTabs = TABS.filter(tab => !tab.requireAdmin || isAdmin);
  
  const activeTabObj = availableTabs.find(tab => location.pathname.startsWith(tab.path)) || availableTabs[0];
  const activeTab = activeTabObj?.id || 'profile';
  const [modalAction, setModalAction] = useState(null);

  useEffect(() => {
    if (location.state?.action) {
      if (location.state.action.includes('users')) navigate('/settings/user-roles');
      else if (location.state.action.includes('roles')) navigate('/settings/roles');
      else if (location.state.action.includes('organization')) navigate('/settings/org');
      
      if (location.state.openModal) {
        setModalAction(location.state.action);
      }

      window.history.replaceState({}, document.title);
    }
  }, [location.state, navigate]);

  const ActiveComponent = activeTabObj?.component || ProfileSection;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      {/* Scrollable Area */}
      <div className="flex-1 overflow-y-auto p-3 md:p-gutter custom-scrollbar min-w-0 flex flex-col">
        
        {/* Top Header/Toolbar like Dashboard */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full px-md mt-4 mb-lg gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Settings</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage your account and preferences</p>
          </div>
        </div>

        <div className="flex flex-col gap-6 px-md pb-12">
          {/* Horizontal Tabs Navigation */}
          <div className="w-full shrink-0 border-b border-outline-variant">
            <nav className="flex flex-row w-full pb-0 overflow-x-auto custom-scrollbar">
              {availableTabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => navigate(tab.path)}
                  className={`flex items-center justify-center shrink-0 gap-2 px-4 py-3 font-bold text-body-sm transition-all whitespace-nowrap border-b-2 ${
                    activeTab === tab.id 
                      ? 'border-primary text-primary' 
                      : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low/50'
                  }`}
                >
                  <span className="material-symbols-outlined text-[20px]">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        
          {/* Main Content Area */}
          <div className="flex-1 min-w-0 pb-12">
            <ActiveComponent modalAction={modalAction} onModalHandled={() => setModalAction(null)} />
          </div>

        </div>
    </div>
    </div>
  );
};

export default Settings;
