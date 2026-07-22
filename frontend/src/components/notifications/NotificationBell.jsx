import React from 'react';
import NotificationBadge from './NotificationBadge';

const NotificationBell = ({ unreadCount, onClick, isOpen }) => {
  return (
    <button 
      onClick={onClick} 
      className={`relative p-1 md:p-2 rounded-full transition-all text-on-surface-variant focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-surface ${
        isOpen ? 'bg-surface-container-high' : 'hover:bg-surface-container-high'
      }`}
      aria-label="Notifications"
      aria-expanded={isOpen}
    >
      <span className="material-symbols-outlined">
        {isOpen ? 'notifications_active' : 'notifications'}
      </span>
      <NotificationBadge count={unreadCount} />
    </button>
  );
};

export default NotificationBell;
