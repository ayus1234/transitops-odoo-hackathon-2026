import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import UserModal from './UserModal';

const UserManagement = ({ modalAction, onModalHandled }) => {
  const { addToast } = useToast();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination & Filtering
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [totalItems, setTotalItems] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage,
        page_size: itemsPerPage,
      });
      if (searchTerm) params.append('search', searchTerm);

      const res = await api.get(`/admin/users?${params.toString()}`);
      if (res.data && res.data.success) {
        setUsers(res.data.data);
        setTotalItems(res.data.pagination.total_items);
      }
    } catch (err) {
      console.error("Error fetching users:", err);
      addToast('Failed to load enterprise users', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUsers();
    }, 300); // Debounce search
    return () => clearTimeout(timer);
  }, [currentPage, itemsPerPage, searchTerm]);

  const handleToggleStatus = async (user) => {
    try {
      const endpoint = user.is_active ? 'disable' : 'enable';
      await api.patch(`/admin/users/${user.id}/${endpoint}`);
      addToast(`User ${user.full_name} has been ${user.is_active ? 'disabled' : 'enabled'}`, 'success');
      fetchUsers();
    } catch (err) {
      addToast(err.response?.data?.error?.message || `Failed to change status`, 'error');
    }
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setIsModalOpen(true);
  };

  useEffect(() => {
    if (modalAction === '/settings/users/new') {
      setSelectedUser(null);
      setIsModalOpen(true);
      if (onModalHandled) onModalHandled();
    }
  }, [modalAction, onModalHandled]);

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <div className="flex flex-col gap-md h-full min-w-0">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
        <div>
          <h2 className="font-title-lg text-title-lg font-bold text-on-surface">User Management</h2>
          <p className="text-body-sm text-on-surface-variant">Manage enterprise users and access</p>
        </div>
        
        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto w-full md:w-auto">
          <div className="relative flex-1 md:w-80">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
            <input 
              type="text" 
              placeholder="Search users by name or email..." 
              value={searchTerm}
              onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              className="h-10 pl-10 pr-4 w-full bg-surface-container border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary outline-none transition-all"
            />
          </div>
          <button onClick={() => {setSearchTerm(''); fetchUsers();}} className="p-2 bg-surface-container hover:bg-surface-container-high rounded text-on-surface transition-colors">
            <span className="material-symbols-outlined">sync</span>
          </button>
        </div>
      </div>

      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col min-w-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="bg-surface-container-low text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                <th className="px-md py-3 w-16">User</th>
                <th className="px-md py-3">Full Name</th>
                <th className="px-md py-3">Email Address</th>
                <th className="px-md py-3">Role</th>
                <th className="px-md py-3">Status</th>
                <th className="px-md py-3">Last Login</th>
                <th className="px-md py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-outline-variant animate-pulse">
                    <td className="px-md py-3"><div className="w-8 h-8 rounded-full bg-slate-200"></div></td>
                    <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-32"></div></td>
                    <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-48"></div></td>
                    <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                    <td className="px-md py-3"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3 text-right"><div className="h-8 bg-slate-200 rounded w-16 ml-auto"></div></td>
                  </tr>
                ))
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-12 text-on-surface-variant">
                    <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">group_off</span>
                    <p>No users found matching your search criteria.</p>
                  </td>
                </tr>
              ) : users.map(user => (
                <tr key={user.id} className={`border-b border-outline-variant hover:bg-surface-container-lowest transition-colors ${!user.is_active ? 'opacity-70 bg-surface-container-lowest' : ''}`}>
                  <td className="px-md py-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${user.is_active ? 'bg-primary text-on-primary' : 'bg-surface-container-highest text-outline'}`}>
                      {user.first_name?.[0]}{user.last_name?.[0]}
                    </div>
                  </td>
                  <td className="px-md py-3 font-bold text-on-surface">{user.full_name}</td>
                  <td className="px-md py-3">{user.email}</td>
                  <td className="px-md py-3 font-bold text-secondary">{user.role_name}</td>
                  <td className="px-md py-3">
                    {user.is_active ? 
                      <span className="bg-primary-container/30 text-primary px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">Active</span> :
                      <span className="bg-error-container/30 text-error px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1">Disabled</span>
                    }
                  </td>
                  <td className="px-md py-3 text-outline">
                    {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                  </td>
                  <td className="px-md py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button 
                        onClick={() => openEditModal(user)}
                        className="p-1.5 rounded hover:bg-surface-container-high text-outline hover:text-primary transition-colors" title="Manage Account"
                      >
                        <span className="material-symbols-outlined text-[18px]">manage_accounts</span>
                      </button>
                      <button 
                        onClick={() => handleToggleStatus(user)}
                        className={`p-1.5 rounded text-outline transition-colors ${user.is_active ? 'hover:bg-error-container hover:text-error' : 'hover:bg-primary-container hover:text-primary'}`} 
                        title={user.is_active ? "Disable User" : "Enable User"}
                      >
                        <span className="material-symbols-outlined text-[18px]">{user.is_active ? 'block' : 'check_circle'}</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer / Pagination */}
        <div className="mt-auto p-md border-t border-outline-variant flex flex-col md:flex-row items-center justify-between gap-4 flex-wrap bg-surface-container-lowest">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <span className="text-body-sm text-outline hidden md:inline">Rows per page:</span>
            <select 
              value={itemsPerPage}
              onChange={(e) => {setItemsPerPage(Number(e.target.value)); setCurrentPage(1);}}
              className="bg-transparent border-none text-body-sm font-bold text-on-surface focus:ring-0 cursor-pointer outline-none"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </div>
          <div className="flex items-center gap-md">
            <span className="text-body-sm text-outline">
              {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems}
            </span>
            <div className="flex items-center gap-xs">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button 
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages || totalPages === 0}
                className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <UserModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        user={selectedUser}
        onSave={() => {setIsModalOpen(false); fetchUsers();}}
      />
    </div>
  );
};

export default UserManagement;
