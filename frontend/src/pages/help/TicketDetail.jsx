import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { helpApi } from '../../services/helpApi';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';

const TicketDetail = () => {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [ticket, setTicket] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [isCloseModalOpen, setIsCloseModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [assigneeId, setAssigneeId] = useState('');

  const isAdminOrSupport = user?.role === 'System Admin' || user?.role === 'Support Agent' || user?.role?.name === 'System Admin' || user?.role?.name === 'Support Agent';

  useEffect(() => {
    const fetchTicket = async () => {
      setIsLoading(true);
      try {
        const res = await helpApi.getTicket(ticketId);
        if (res.data?.success) {
          setTicket(res.data.data);
        } else {
          navigate('/help/tickets');
        }
      } catch (err) {
        console.error('Failed to load ticket:', err);
        showToast('Failed to load ticket details or unauthorized.', 'error');
        navigate('/help/tickets');
      } finally {
        setIsLoading(false);
      }
    };

    if (ticketId) {
      fetchTicket();
    }
  }, [ticketId, navigate, showToast]);

  const handleResolve = async () => {
    if (!resolutionNotes.trim()) {
      showToast('Resolution notes are required.', 'error');
      return;
    }
    try {
      setIsUpdating(true);
      const res = await helpApi.resolveTicket(ticketId, resolutionNotes);
      if (res.data?.success) {
        setTicket(res.data.data);
        showToast('Ticket resolved successfully', 'success');
        setIsResolveModalOpen(false);
        setResolutionNotes('');
      }
    } catch (error) {
      console.error('Failed to resolve ticket', error);
      showToast('Failed to resolve ticket', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleClose = async () => {
    try {
      setIsUpdating(true);
      const res = await helpApi.closeTicket(ticketId);
      if (res.data?.success) {
        setTicket(res.data.data);
        showToast('Ticket closed successfully', 'success');
        setIsCloseModalOpen(false);
      }
    } catch (error) {
      console.error('Failed to close ticket', error);
      showToast('Failed to close ticket', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAssign = async () => {
    if (!assigneeId.trim()) {
      showToast('Assignee ID is required.', 'error');
      return;
    }
    try {
      setIsUpdating(true);
      const res = await helpApi.assignTicket(ticketId, assigneeId);
      if (res.data?.success) {
        setTicket(res.data.data);
        showToast('Ticket assigned successfully', 'success');
        setIsAssignModalOpen(false);
        setAssigneeId('');
      }
    } catch (error) {
      console.error('Failed to assign ticket', error);
      showToast('Failed to assign ticket', 'error');
    } finally {
      setIsUpdating(false);
    }
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

  if (isLoading) {
    return (
      <div className="p-6 md:p-8 max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-8 w-32 bg-surface-container rounded"></div>
        <div className="card p-8 space-y-4">
          <div className="h-8 w-1/2 bg-surface-container rounded"></div>
          <div className="flex gap-4">
            <div className="h-6 w-24 bg-surface-container rounded-full"></div>
            <div className="h-6 w-24 bg-surface-container rounded-full"></div>
          </div>
          <div className="h-32 w-full bg-surface-container rounded mt-8"></div>
        </div>
      </div>
    );
  }

  if (!ticket) return null;

  return (
    <div className="p-4 md:p-8 max-w-4xl mx-auto space-y-6">
      <nav className="flex items-center text-sm text-on-surface-variant mb-4">
        <Link to="/help/tickets" className="hover:text-primary transition-colors flex items-center gap-1">
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Back to Tickets
        </Link>
      </nav>

      <div className="card overflow-hidden">
        {/* Ticket Header */}
        <div className="p-6 md:p-8 border-b border-outline-variant bg-surface">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="font-mono text-sm font-bold text-primary bg-primary/10 px-2 py-1 rounded">
                  {ticket.ticket_number}
                </span>
                <span className="text-sm text-on-surface-variant">
                  {new Date(ticket.created_at).toLocaleString()}
                </span>
              </div>
              <h1 className="text-2xl font-bold text-on-surface">{ticket.title}</h1>
            </div>

            {/* Status Actions (Admins) or Status Badge */}
            <div className="flex flex-col items-end gap-2 shrink-0">
              <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium border ${getStatusColor(ticket.status)}`}>
                {ticket.status}
              </span>
              
              {isAdminOrSupport && ticket.status !== 'Closed' && (
                <div className="flex items-center gap-2 mt-1">
                  {ticket.status !== 'Resolved' && (
                    <button onClick={() => setIsResolveModalOpen(true)} className="btn btn-primary py-1 px-3 text-xs" disabled={isUpdating}>
                      Resolve
                    </button>
                  )}
                  {ticket.status === 'Resolved' && (
                    <button onClick={() => setIsCloseModalOpen(true)} className="btn bg-error/10 text-error hover:bg-error/20 border border-error/20 py-1 px-3 text-xs" disabled={isUpdating}>
                      Close
                    </button>
                  )}
                  <button onClick={() => setIsAssignModalOpen(true)} className="btn btn-secondary py-1 px-3 text-xs" disabled={isUpdating}>
                    Assign
                  </button>
                </div>
              )}
              
              <span className={`inline-flex items-center px-3 py-1 rounded text-xs font-medium ${getPriorityColor(ticket.priority)}`}>
                {ticket.priority} Priority
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-4 gap-4 py-4 border-t border-outline-variant">
            <div>
              <span className="block text-xs font-medium text-on-surface-variant mb-1">Requester</span>
              <span className="text-sm text-on-surface flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">person</span>
                {ticket.user?.first_name} {ticket.user?.last_name}
              </span>
            </div>
            <div>
              <span className="block text-xs font-medium text-on-surface-variant mb-1">Category</span>
              <span className="text-sm text-on-surface flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">category</span>
                {ticket.category}
              </span>
            </div>
            <div>
              <span className="block text-xs font-medium text-on-surface-variant mb-1">Module Name</span>
              <span className="text-sm text-on-surface flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">extension</span>
                {ticket.module_name}
              </span>
            </div>
            <div>
              <span className="block text-xs font-medium text-on-surface-variant mb-1">Assigned To</span>
              <span className="text-sm text-on-surface flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">support_agent</span>
                {ticket.assignee ? `${ticket.assignee.first_name} ${ticket.assignee.last_name}` : 'Unassigned'}
              </span>
            </div>
            <div>
              <span className="block text-xs font-medium text-on-surface-variant mb-1">Last Updated</span>
              <span className="text-sm text-on-surface">
                {new Date(ticket.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Ticket Description */}
        <div className="p-6 md:p-8 bg-surface-container-lowest border-b border-outline-variant">
          <h3 className="text-sm font-semibold text-on-surface mb-4 uppercase tracking-wider">Description</h3>
          <div className="prose prose-on-surface max-w-none whitespace-pre-wrap text-on-surface-variant mb-6">
            {ticket.description}
          </div>
          
          {ticket.attachments && ticket.attachments.length > 0 && (
            <div className="mt-8 pt-6 border-t border-outline-variant">
              <h3 className="text-sm font-semibold text-on-surface mb-4 uppercase tracking-wider flex items-center gap-2">
                <span className="material-symbols-outlined text-[18px]">attachment</span>
                Attachments ({ticket.attachments.length})
              </h3>
              <div className="flex flex-wrap gap-4">
                {ticket.attachments.map((url, i) => {
                  const isImage = url.match(/\.(jpeg|jpg|gif|png|webp)$/i) != null;
                  const filename = url.split('/').pop();
                  
                  return (
                    <a 
                      key={i} 
                      href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="group flex flex-col items-center gap-2 p-3 border border-outline-variant rounded-xl bg-surface hover:bg-surface-container hover:border-primary transition-all max-w-[200px]"
                    >
                      {isImage ? (
                        <div className="w-full h-24 bg-surface-container-low rounded-lg overflow-hidden flex items-center justify-center">
                          <img 
                            src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`} 
                            alt={filename} 
                            className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300"
                          />
                        </div>
                      ) : (
                        <div className="w-full h-24 bg-surface-container-lowest rounded-lg flex items-center justify-center text-outline">
                          <span className="material-symbols-outlined text-4xl">description</span>
                        </div>
                      )}
                      <span className="text-xs font-medium text-on-surface-variant truncate w-full text-center group-hover:text-primary transition-colors">
                        {filename}
                      </span>
                    </a>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Resolution Area */}
        {(ticket.resolution_notes || isAdminOrSupport) && (
          <div className="p-6 md:p-8 bg-surface">
            <h3 className="text-sm font-semibold text-on-surface mb-4 uppercase tracking-wider flex items-center gap-2">
              <span className="material-symbols-outlined text-green-500">check_circle</span>
              Resolution
            </h3>
            
            {ticket.resolution_notes ? (
              <div className="p-4 bg-green-500/5 border border-green-500/20 rounded-lg text-on-surface-variant whitespace-pre-wrap">
                {ticket.resolution_notes}
              </div>
            ) : isAdminOrSupport ? (
              <div className="text-sm text-on-surface-variant italic">
                Resolution can be provided when the ticket status is updated to Resolved.
              </div>
            ) : null}
            
            {ticket.resolved_at && (
              <div className="mt-3 text-xs text-on-surface-variant">
                Resolved on {new Date(ticket.resolved_at).toLocaleString()}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Modals */}
      {isResolveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-surface rounded-xl p-6 max-w-[448px] min-w-[320px] shrink-0 w-full shadow-lg">
            <h3 className="text-xl font-bold mb-4">Resolve Ticket</h3>
            <textarea
              className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface-container-lowest text-on-surface focus:outline-none focus:ring-2 focus:ring-primary mb-4"
              rows={4}
              placeholder="Enter resolution notes..."
              value={resolutionNotes}
              onChange={(e) => setResolutionNotes(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button className="btn btn-secondary" onClick={() => setIsResolveModalOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleResolve} disabled={isUpdating || !resolutionNotes.trim()}>Resolve Ticket</button>
            </div>
          </div>
        </div>
      )}

      {isCloseModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-surface rounded-xl p-6 max-w-[448px] min-w-[320px] shrink-0 w-full shadow-lg">
            <h3 className="text-xl font-bold mb-4 text-error">Close Ticket</h3>
            <p className="text-on-surface-variant mb-6">Are you sure you want to close this ticket? This action cannot be easily undone.</p>
            <div className="flex justify-end gap-3">
              <button className="btn btn-secondary" onClick={() => setIsCloseModalOpen(false)}>Cancel</button>
              <button className="btn bg-error text-on-error px-4 py-2 rounded font-bold hover:bg-error/90" onClick={handleClose} disabled={isUpdating}>Close Ticket</button>
            </div>
          </div>
        </div>
      )}

      {isAssignModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-surface rounded-xl p-6 max-w-[448px] min-w-[320px] shrink-0 w-full shadow-lg">
            <h3 className="text-xl font-bold mb-4">Assign Ticket</h3>
            <input
              type="text"
              placeholder="Enter User ID to assign to"
              className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface-container-lowest text-on-surface focus:outline-none focus:ring-2 focus:ring-primary mb-4"
              value={assigneeId}
              onChange={(e) => setAssigneeId(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button className="btn btn-secondary" onClick={() => setIsAssignModalOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleAssign} disabled={isUpdating || !assigneeId.trim()}>Assign Ticket</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketDetail;
