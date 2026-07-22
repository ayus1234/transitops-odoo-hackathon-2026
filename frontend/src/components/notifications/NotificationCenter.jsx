import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import NotificationBell from './NotificationBell';
import NotificationDropdown from './NotificationDropdown';
import NotificationModal from './NotificationModal';
import NotificationStatistics from './NotificationStatistics';
import { 
  getNotifications, 
  markAsRead, 
  markAsUnread, 
  markAllAsRead, 
  archiveNotification, 
  unarchiveNotification,
  deleteNotification,
  getNotificationStatistics,
  searchNotifications,
  executeNotification
} from '../../services/notificationApi';
import { useToast } from '../../contexts/ToastContext';
import { useDataSync } from '../../contexts/RealTimeSyncContext';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isStatsOpen, setIsStatsOpen] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  
  const [activeTab, setActiveTab] = useState('all'); // all, unread, archived
  const [filters, setFilters] = useState({});
  const pageRef = useRef(0);
  const [hasMore, setHasMore] = useState(false);
  const LIMIT = 5;
  
  const bellRef = useRef(null);
  const { showToast } = useToast();
  const navigate = useNavigate();

  const fetchUnreadCount = useCallback(async () => {
    try {
      const stats = await getNotificationStatistics();
      setUnreadCount(stats.unread);
    } catch (error) {
      console.error("Failed to fetch unread count:", error);
    }
  }, []);

  const loadNotifications = useCallback(async (isLoadMore = false, silent = false) => {
    if (!silent) setIsLoading(true);
    try {
      const currentPage = isLoadMore ? pageRef.current + 1 : 0;
      const skip = currentPage * LIMIT;
      
      const queryParams = {
        skip,
        limit: LIMIT,
        ...filters,
        is_archived: activeTab === 'archived',
      };
      
      // Remove search from queryParams if we use explicit search API
      const searchQuery = queryParams.search;
      if (searchQuery) {
        delete queryParams.search;
      }

      if (activeTab === 'unread') queryParams.is_read = false;
      
      let response;
      if (searchQuery && searchQuery.trim().length > 0) {
        response = await searchNotifications(searchQuery, queryParams);
      } else {
        response = await getNotifications(queryParams);
      }
      
      if (isLoadMore) {
        setNotifications(prev => [...prev, ...response.data]);
      } else {
        setNotifications(response.data);
      }
      
      pageRef.current = currentPage;
      setHasMore((currentPage + 1) * LIMIT < response.total);
    } catch (error) {
      if (!silent) showToast('Failed to load notifications', 'error');
    } finally {
      if (!silent) setIsLoading(false);
    }
  }, [activeTab, filters, showToast]);

  // Initial load
  useEffect(() => {
    fetchUnreadCount();
  }, [fetchUnreadCount]);

  // Centralized background polling using RealTimeSyncEngine
  const handlePeriodicSync = useCallback(async () => {
    await fetchUnreadCount();
    if (isOpen) {
      await loadNotifications(false, true);
    }
    return null;
  }, [fetchUnreadCount, isOpen, loadNotifications]);

  useDataSync(handlePeriodicSync, [isOpen], 'high');

  // Debounced load when dropdown opens or filters/tabs change
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (isOpen) {
        loadNotifications(false);
      }
    }, 300); // 300ms debounce
    return () => clearTimeout(timeoutId);
  }, [isOpen, activeTab, filters, loadNotifications]);

  const toggleDropdown = () => {
    setIsOpen(prev => !prev);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const handleNotificationClick = (notification) => {
    setSelectedNotification(notification);
    setIsModalOpen(true);
    setIsOpen(false);
    
    // Auto mark as read when opened
    if (!notification.is_read) {
      handleToggleRead(notification, true);
    }
  };

  const handleToggleRead = async (notification, skipRefetch = false) => {
    try {
      // Optimistic update
      setNotifications(prev => 
        prev.map(n => n.id === notification.id ? { ...n, is_read: !n.is_read } : n)
      );
      setUnreadCount(prev => notification.is_read ? prev + 1 : Math.max(0, prev - 1));

      if (notification.is_read) {
        await markAsUnread(notification.id);
        if (!skipRefetch) showToast('Marked as unread', 'success');
      } else {
        await markAsRead(notification.id);
        if (!skipRefetch) showToast('Marked as read', 'success');
      }
    } catch (error) {
      showToast('Failed to update notification', 'error');
      if (!skipRefetch) loadNotifications(false); // Revert on failure
      fetchUnreadCount();
    }
  };

  const handleArchive = async (notification) => {
    try {
      // Optimistic update
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
      if (!notification.is_read) setUnreadCount(prev => Math.max(0, prev - 1));
      
      await archiveNotification(notification.id);
      showToast('Notification archived', 'success');
    } catch (error) {
      showToast('Failed to archive notification', 'error');
      loadNotifications(false);
    }
  };

  const handleUnarchive = async (notification) => {
    try {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
      await unarchiveNotification(notification.id);
      showToast('Notification unarchived', 'success');
      fetchUnreadCount();
    } catch (error) {
      showToast('Failed to unarchive notification', 'error');
      loadNotifications(false);
    }
  };

  const handleExecute = async (notification) => {
    try {
      const response = await executeNotification(notification.id);
      
      // Update UI immediately for unread
      if (!notification.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      
      if (response.route) {
        navigate(response.route);
        setIsOpen(false);
        setIsModalOpen(false);
      }
      
      showToast('Action executed successfully', 'success');
      loadNotifications(false, true); // silent reload to sync state
    } catch (error) {
      showToast('Failed to execute action', 'error');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
      showToast('All notifications marked as read', 'success');
    } catch (error) {
      showToast('Failed to mark all as read', 'error');
    }
  };

  const handleDelete = async (notification) => {
    try {
      await deleteNotification(notification.id);
      setIsModalOpen(false);
      showToast('Notification deleted', 'success');
      loadNotifications(false);
      fetchUnreadCount();
    } catch (error) {
      showToast('Failed to delete notification', 'error');
    }
  };

  return (
    <div className="relative inline-flex items-center">
      <div ref={bellRef}>
        <NotificationBell 
          unreadCount={unreadCount} 
          onClick={toggleDropdown}
          isOpen={isOpen}
        />
      </div>

      <button 
        onClick={() => setIsStatsOpen(true)}
        className="p-1 md:p-2 ml-1 rounded-full hover:bg-surface-container-high transition-all text-on-surface-variant flex"
        title="Notification Statistics"
      >
        <span className="material-symbols-outlined">analytics</span>
      </button>

      <NotificationDropdown 
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        bellRef={bellRef}
        notifications={notifications}
        isLoading={isLoading}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNotificationClick={handleNotificationClick}
        onToggleRead={handleToggleRead}
        onArchive={handleArchive}
        onUnarchive={handleUnarchive}
        onExecute={handleExecute}
        onMarkAllRead={handleMarkAllRead}
        filters={filters}
        onFilterChange={handleFilterChange}
        hasMore={hasMore}
        onLoadMore={() => loadNotifications(true)}
      />

      {createPortal(
        <>
          <NotificationModal 
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            notification={selectedNotification}
            onDelete={handleDelete}
            onExecute={handleExecute}
          />
          <NotificationStatistics 
            isOpen={isStatsOpen}
            onClose={() => setIsStatsOpen(false)}
          />
        </>,
        document.body
      )}
    </div>
  );
};

export default NotificationCenter;
