import React, { useState, useEffect } from 'react';
import api from '../../../services/api';
import { downloadBlobFromResponse, getFormattedDate } from '../../../utils/exportUtils';
import { useToast } from '../../../contexts/ToastContext';
import UserRoleModal from './UserRoleModal';

const getAuditLogDescription = (log) => {
  const action = log.action;
  if (action === 'CREATE_ROLE') return `Created role: ${log.new_value?.name || 'Unknown'}`;
  if (action === 'BULK_ASSIGN_ROLE') return `Bulk assigned roles to ${log.new_value?.users_affected || 0} users`;
  if (action === 'REMOVE_ADDITIONAL_ROLES') return `Removed ${log.previous_value?.removed_count || 0} additional roles`;
  if (action === 'ASSIGN_ROLE') {
    if (log.new_value?.users_affected) {
      return `Assigned ${log.new_value?.role} to ${log.new_value.users_affected} users`;
    }
    return `Assigned ${log.new_value?.role || 'role'} to user`;
  }
  if (action === 'UPDATE_ROLE') {
     if (log.new_value?.name) return `Updated role: ${log.new_value.name}`;
     return `Updated role permissions`;
  }
  
  return log.target_user_id ? 'User roles modified' : (log.target_role_id ? 'Role modified' : 'System changed');
};

const formatActionName = (action) => {
  if (!action) return '';
  return action.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
};

const UserRoleAssignment = () => {
  const { addToast } = useToast();
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination & Search
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  
  // Modal State for Assignment/Edit
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [usersRes, auditRes] = await Promise.all([
        api.get('/admin/users?page_size=100'), // simplified for demo
        api.get('/settings/permissions/audit')
      ]);
      setUsers(usersRes.data?.data || []);
      setAuditLogs(auditRes.data || []);
    } catch (err) {
      console.error(err);
      addToast('Failed to load user role data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openAssignModal = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  const handleExport = async () => {
    try {
      const res = await api.get('/settings/permissions/export', { responseType: 'blob' });
      downloadBlobFromResponse(res, `permissions_matrix_report_${getFormattedDate()}.csv`);
      addToast('Audit log exported successfully', 'success');
    } catch (err) {
      addToast('Failed to export audit logs', 'error');
    }
  };

  const filteredUsers = users.filter(u => 
    u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredUsers.length / pageSize);
  const paginatedUsers = filteredUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const multipleRoleUsers = users.filter(u => u.additional_roles && u.additional_roles.length > 0).length;

  return (
    <div className="flex flex-col gap-md h-full min-w-0 max-w-7xl">
      <div className="flex justify-between items-end w-full border-b border-outline-variant pb-4">
        <div>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">User Role Assignment</h2>
          <p className="text-body-sm text-on-surface-variant">Manage and assign primary and additional roles to users.</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={handleExport}
            className="border border-outline-variant text-on-surface px-4 py-2 rounded font-bold text-body-sm hover:bg-surface-container transition-all flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto"
          >
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export Audit
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-md mt-2">
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-primary-container text-primary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">group</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Total Users</p>
            <h3 className="text-headline-md font-bold text-on-surface">{users.length}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-secondary-container text-secondary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">how_to_reg</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Assigned Users</p>
            <h3 className="text-headline-md font-bold text-on-surface">{users.filter(u => u.role_name).length}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-tertiary-container text-tertiary flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">layers</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Multi-Role Users</p>
            <h3 className="text-headline-md font-bold text-on-surface">{multipleRoleUsers}</h3>
          </div>
        </div>
        <div className="bg-surface border border-outline-variant rounded-xl p-md flex items-center gap-4 shadow-sm">
          <div className="w-12 h-12 rounded-full bg-error-container text-error flex items-center justify-center shrink-0">
            <span className="material-symbols-outlined">person_off</span>
          </div>
          <div>
            <p className="text-body-sm text-on-surface-variant font-bold">Unassigned</p>
            <h3 className="text-headline-md font-bold text-on-surface">{users.filter(u => !u.role_name || u.role_name === 'Unassigned').length}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-md mt-4 mb-12">
        {/* User Table */}
        <div className="lg:col-span-2 bg-surface border border-outline-variant rounded-lg shadow-sm flex flex-col min-w-0">
          <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
            <h3 className="font-title-md font-bold text-on-surface">Enterprise Users</h3>
            <div className="relative w-64">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">search</span>
              <input 
                type="text" 
                placeholder="Search..." 
                value={searchTerm}
                onChange={handleSearchChange}
                className="h-8 pl-9 pr-3 w-full bg-surface border border-outline-variant rounded text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
              />
            </div>
          </div>
          <div className="overflow-x-auto flex-1 h-[400px] overflow-y-auto custom-scrollbar">
            <table className="w-full text-left border-collapse min-w-[600px]">
              <thead className="sticky top-0 bg-surface-container-lowest z-10">
                <tr className="text-label-caps text-on-surface-variant uppercase border-b border-outline-variant">
                  <th className="px-4 py-3 font-bold">User</th>
                  <th className="px-4 py-3 font-bold">Roles</th>
                  <th className="px-4 py-3 text-right font-bold">Actions</th>
                </tr>
              </thead>
              <tbody className="text-body-sm">
                {paginatedUsers.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="text-center py-8 text-on-surface-variant italic">No users found.</td>
                  </tr>
                ) : paginatedUsers.map(user => (
                  <tr key={user.id} className="border-b border-outline-variant hover:bg-surface-container-lowest transition-colors">
                    <td className="px-4 py-3">
                      <p className="font-bold text-on-surface">{user.full_name}</p>
                      <p className="text-xs text-on-surface-variant">{user.email}</p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        <span className="bg-primary-container/30 text-primary px-2 py-0.5 rounded text-xs font-bold border border-primary/20">
                          Primary: {user.role_name || 'None'}
                        </span>
                        {user.additional_roles?.map((r, i) => (
                          <span key={i} className="bg-tertiary-container/30 text-tertiary px-2 py-0.5 rounded text-xs border border-tertiary/20">
                            + {r.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button 
                        onClick={() => openAssignModal(user)}
                        className="p-1.5 rounded bg-surface-container hover:bg-primary-container text-on-surface hover:text-primary transition-colors text-xs font-bold"
                      >
                        Manage Access
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Pagination Controls */}
          <div className="p-3 border-t border-outline-variant bg-surface flex justify-between items-center text-xs">
            <div className="flex items-center gap-2">
              <span className="text-on-surface-variant">Rows per page:</span>
              <select 
                value={pageSize} 
                onChange={handlePageSizeChange}
                className="bg-surface border border-outline-variant rounded px-2 py-1 outline-none text-on-surface"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-on-surface-variant">
                {filteredUsers.length > 0 ? (currentPage - 1) * pageSize + 1 : 0}-
                {Math.min(currentPage * pageSize, filteredUsers.length)} of {filteredUsers.length}
              </span>
              <div className="flex gap-1">
                <button 
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-1 rounded hover:bg-surface-container disabled:opacity-30 disabled:hover:bg-transparent"
                >
                  <span className="material-symbols-outlined text-[18px]">chevron_left</span>
                </button>
                <button 
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                  className="p-1 rounded hover:bg-surface-container disabled:opacity-30 disabled:hover:bg-transparent"
                >
                  <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Audit Log Panel */}
        <div className="bg-surface border border-outline-variant rounded-lg shadow-sm flex flex-col min-w-0">
          <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
            <h3 className="font-title-md font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">history</span>
              Audit Logs
            </h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 custom-scrollbar h-[400px]">
            {auditLogs.length === 0 ? (
              <p className="text-body-sm text-outline italic text-center mt-10">No recent RBAC events</p>
            ) : (
              <div className="flex flex-col gap-4">
                {auditLogs.slice(0, 10).map((log) => (
                  <div key={log.id} className="border-l-2 border-primary pl-3">
                    <div className="flex justify-between items-start">
                      <p className="text-body-sm font-bold text-on-surface">{formatActionName(log.action)}</p>
                      <span className="text-[10px] text-outline">{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <p className="text-xs text-on-surface-variant mt-1">
                      {getAuditLogDescription(log)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <UserRoleModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        user={selectedUser}
        onSave={() => {setIsModalOpen(false); fetchData();}}
      />
    </div>
  );
};

export default UserRoleAssignment;
