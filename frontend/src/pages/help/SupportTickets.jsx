import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';
import CreateTicketModal from '../../components/help/CreateTicketModal';
import { useDataSync } from '../../contexts/RealTimeSyncContext';

const SupportTickets = () => {
  const [filter, setFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);

  const fetchTickets = React.useCallback(async () => {
    let res;
    if (searchQuery.trim()) {
      res = await helpApi.searchTickets({ q: searchQuery, skip: 0, limit: 100 });
    } else {
      res = await helpApi.getTickets({ 
        status: filter === 'All' ? null : filter,
        limit: 100 
      });
    }
    if (res.data?.success) {
      return res.data.data;
    }
    return [];
  }, [filter, searchQuery]);

  const { data: ticketsData, loading: isLoading, refresh, silentRefresh } = useDataSync(
    fetchTickets,
    [filter, searchQuery],
    'medium'
  );

  const tickets = ticketsData || [];

  const paginatedTickets = React.useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return tickets.slice(start, start + itemsPerPage);
  }, [tickets, currentPage, itemsPerPage]);

  const totalItems = tickets.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [filter, searchQuery, itemsPerPage]);

  const handleTicketCreated = (newTicket) => {
    silentRefresh();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Critical': return 'bg-error text-on-error';
      case 'High': return 'bg-amber-500 text-white';
      case 'Medium': return 'bg-primary text-on-primary';
      case 'Low': return 'bg-surface-container-highest text-on-surface';
      default: return 'bg-surface-container-highest text-on-surface';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Open': return 'border-error text-error bg-error/10';
      case 'In Progress': return 'border-amber-500 text-amber-600 bg-amber-500/10';
      case 'Resolved': return 'border-green-500 text-green-600 bg-green-500/10';
      case 'Closed': return 'border-outline text-on-surface-variant bg-surface-container';
      default: return 'border-outline text-on-surface-variant bg-surface-container';
    }
  };

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 w-full min-w-0">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-on-surface">Support Tickets</h1>
          <p className="text-on-surface-variant mt-1">Manage and track your support requests.</p>
        </div>
        <button 
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-primary text-on-primary px-4 py-2 rounded font-bold hover:opacity-90 active:scale-95 transition-all flex items-center gap-2 shadow-sm shrink-0"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Ticket
        </button>
      </div>

      {/* Filters & Content */}
      <div className="card overflow-hidden w-full min-w-0 bg-surface shadow-sm rounded-xl border border-outline-variant">
        <div className="border-b border-outline-variant p-4 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex flex-wrap gap-2 shrink-0">
            {['All', 'Open', 'In Progress', 'Resolved', 'Closed'].map(status => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  filter === status 
                    ? 'bg-primary text-on-primary' 
                    : 'bg-surface hover:bg-surface-container border border-outline-variant text-on-surface-variant'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
          <div className="relative w-full lg:w-72 shrink-0">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">search</span>
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-surface border border-outline-variant rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-on-surface"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-8 flex justify-center">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
            </div>
          ) : tickets.length > 0 ? (
            <table className="w-full text-left border-collapse min-w-[1200px]">
              <thead>
                <tr className="bg-surface-container-lowest border-b border-outline-variant text-sm font-medium text-on-surface-variant">
                  <th className="p-4">Ticket ID</th>
                  <th className="p-4">Title</th>
                  <th className="p-4">Category</th>
                  <th className="p-4">Module</th>
                  <th className="p-4">Assigned To</th>
                  <th className="p-4">Priority</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Created Date</th>
                  <th className="p-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {paginatedTickets.map(ticket => (
                  <tr key={ticket.id} className="hover:bg-surface-container-lowest transition-colors group">
                    <td className="p-4 font-mono text-sm font-medium text-primary">
                      {ticket.ticket_number}
                    </td>
                    <td className="p-4 font-medium text-on-surface min-w-[200px]">
                      {ticket.title}
                    </td>
                    <td className="p-4 text-on-surface-variant">
                      {ticket.category}
                    </td>
                    <td className="p-4 text-on-surface-variant">
                      {ticket.module_name}
                    </td>
                    <td className="p-4 text-on-surface-variant">
                      {ticket.assignee ? `${ticket.assignee.first_name} ${ticket.assignee.last_name}` : 'Unassigned'}
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(ticket.status)}`}>
                        {ticket.status}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-on-surface-variant whitespace-nowrap">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right whitespace-nowrap">
                      <Link 
                        to={`/help/tickets/${ticket.id}`}
                        className="btn btn-secondary py-1 px-3 text-sm transition-opacity whitespace-nowrap inline-block"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-12 flex flex-col items-center text-center">
              <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center text-on-surface-variant mb-4">
                <span className="material-symbols-outlined text-3xl">inbox</span>
              </div>
              <h3 className="text-lg font-medium text-on-surface mb-2">No tickets found</h3>
              <p className="text-on-surface-variant mb-6">
                {filter === 'All' 
                  ? "You haven't submitted any support tickets yet." 
                  : `There are no tickets with the status "${filter}".`}
              </p>
              {filter !== 'All' && (
                <button onClick={() => setFilter('All')} className="btn btn-secondary">
                  Clear Filters
                </button>
              )}
            </div>
          )}
        </div>
        
        {/* Pagination Footer */}
        {tickets.length > 0 && (
          <div className="p-4 border-t border-outline-variant flex flex-wrap items-center justify-between gap-4 bg-surface-container-lowest">
            <div className="flex items-center gap-2">
              <span className="text-sm text-on-surface-variant">Rows per page:</span>
              <select 
                value={itemsPerPage}
                onChange={(e) => setItemsPerPage(Number(e.target.value))}
                className="bg-transparent text-sm font-bold text-on-surface focus:outline-none"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-on-surface-variant">
                {totalItems > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0}-{Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems}
              </span>
              <div className="flex items-center gap-1">
                <button 
                  onClick={() => handlePageChange('prev')}
                  disabled={currentPage === 1}
                  className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30"
                >
                  <span className="material-symbols-outlined">chevron_left</span>
                </button>
                <button 
                  onClick={() => handlePageChange('next')}
                  disabled={currentPage === totalPages || totalPages === 0}
                  className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30"
                >
                  <span className="material-symbols-outlined">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <CreateTicketModal 
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreated={handleTicketCreated}
      />
    </div>
  );
};

export default SupportTickets;
