import React, { useRef, useEffect } from 'react';
import NotificationCard from './NotificationCard';
import NotificationFilters from './NotificationFilters';

const NotificationDropdown = ({ 
  isOpen, 
  onClose, 
  bellRef,
  notifications, 
  isLoading, 
  activeTab, 
  setActiveTab,
  onNotificationClick,
  onToggleRead,
  onArchive,
  onUnarchive,
  onExecute,
  onMarkAllRead,
  filters,
  onFilterChange,
  hasMore,
  onLoadMore
}) => {
  const dropdownRef = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        isOpen && 
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target) &&
        bellRef.current &&
        !bellRef.current.contains(event.target)
      ) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose, bellRef]);

  if (!isOpen) return null;

  return (
    <div 
      ref={dropdownRef}
      className="fixed inset-x-2 top-[70px] sm:absolute sm:inset-auto sm:right-0 sm:top-full sm:mt-2 w-auto sm:w-[400px] bg-surface rounded-lg shadow-elevation-3 border border-outline-variant overflow-hidden z-[100] flex flex-col max-h-[calc(100vh-90px)] sm:max-h-[85vh] animate-fade-in sm:origin-top-right"
    >
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b border-outline-variant bg-surface-container-lowest">
        <h3 className="font-bold text-title-md text-on-surface">Notifications</h3>
        <div className="flex gap-2">
          {activeTab !== 'archived' && (
            <button 
              onClick={onMarkAllRead}
              className="text-body-sm text-primary font-medium hover:underline px-2 py-1 rounded hover:bg-surface-container-low transition-colors"
            >
              Mark all read
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-outline-variant bg-surface">
        {['all', 'unread', 'archived'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-label-md font-bold capitalize transition-colors border-b-2 ${
              activeTab === tab 
                ? 'border-primary text-primary' 
                : 'border-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Filters */}
      {activeTab !== 'archived' && (
        <NotificationFilters filters={filters} onFilterChange={onFilterChange} />
      )}

      {/* List */}
      <div className="overflow-y-auto flex-1 bg-surface-container-lowest">
        {isLoading && notifications.length === 0 ? (
          <div className="p-4 flex flex-col gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="flex gap-3 animate-pulse">
                <div className="w-10 h-10 rounded-full bg-surface-variant shrink-0" />
                <div className="flex-1 space-y-2 py-1">
                  <div className="h-4 bg-surface-variant rounded w-3/4" />
                  <div className="h-3 bg-surface-variant rounded w-full" />
                  <div className="h-3 bg-surface-variant rounded w-5/6" />
                </div>
              </div>
            ))}
          </div>
        ) : notifications.length > 0 ? (
          <>
            {notifications.map(notif => (
              <NotificationCard 
                key={notif.id}
                notification={notif}
                onClick={onNotificationClick}
                onToggleRead={onToggleRead}
                onArchive={onArchive}
                onUnarchive={onUnarchive}
                onExecute={onExecute}
              />
            ))}
            {hasMore && (
              <div className="p-3 text-center border-t border-outline-variant">
                <button 
                  onClick={onLoadMore}
                  disabled={isLoading}
                  className="text-primary text-body-sm font-bold hover:underline disabled:opacity-50"
                >
                  {isLoading ? 'Loading...' : 'Load More'}
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 text-center h-48">
            <div className="w-16 h-16 rounded-full bg-surface-variant flex items-center justify-center mb-3 text-on-surface-variant">
              <span className="material-symbols-outlined text-[32px]">
                {activeTab === 'archived' ? 'archive' : 'notifications_off'}
              </span>
            </div>
            <p className="text-title-sm font-medium text-on-surface">No notifications found</p>
            <p className="text-body-sm text-on-surface-variant mt-1">
              {activeTab === 'unread' ? "You're all caught up!" : activeTab === 'archived' ? "No archived notifications found." : "You don't have any notifications matching these filters."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationDropdown;
