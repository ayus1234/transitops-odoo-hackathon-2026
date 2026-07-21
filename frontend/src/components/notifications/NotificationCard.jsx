import React from 'react';

// Maps category/priority to appropriate colors and icons
const getTypeConfig = (category, priority) => {
  let icon = 'notifications';
  let colorClass = 'text-primary bg-primary-container';
  let dotClass = 'bg-primary';

  switch (category) {
    case 'Error':
      icon = 'error';
      colorClass = 'text-error bg-error-container';
      dotClass = 'bg-error';
      break;
    case 'Warning':
      icon = 'warning';
      colorClass = 'text-warning bg-warning-container'; // Need to ensure these Tailwind classes exist, or fallback
      dotClass = 'bg-warning';
      break;
    case 'Success':
      icon = 'check_circle';
      colorClass = 'text-success bg-success-container'; // Fallbacks to primary if custom don't exist
      dotClass = 'bg-success';
      break;
    case 'Information':
    default:
      icon = 'info';
      colorClass = 'text-primary bg-primary-container';
      dotClass = 'bg-primary';
      break;
  }

  // Override for high priority
  if (priority === 'Critical') {
    icon = 'emergency';
    colorClass = 'text-error bg-error-container';
    dotClass = 'bg-error';
  }

  return { icon, colorClass, dotClass };
};

const formatTimeAgo = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now - date) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  
  return date.toLocaleDateString();
};

const NotificationCard = ({ notification, onClick, onToggleRead, onArchive, onUnarchive, onExecute }) => {
  const { icon, colorClass, dotClass } = getTypeConfig(notification.category, notification.priority);
  
  return (
    <div 
      className={`group relative p-4 border-b border-outline-variant hover:bg-surface-container-low transition-colors cursor-pointer ${
        !notification.is_read ? 'bg-surface-container-lowest' : 'bg-surface'
      }`}
      onClick={() => onClick(notification)}
    >
      <div className="flex gap-3">
        {/* Icon & Unread Indicator */}
        <div className="flex-shrink-0 relative mt-1">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${colorClass}`}>
            <span className="material-symbols-outlined text-[20px]">{notification.icon || icon}</span>
          </div>
          {!notification.is_read && (
            <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-surface ${dotClass}`} />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start gap-2 mb-1">
            <h4 className={`text-title-sm truncate font-medium ${!notification.is_read ? 'text-on-surface font-bold' : 'text-on-surface-variant'}`}>
              {notification.title}
            </h4>
            <span className="text-body-sm text-outline flex-shrink-0 whitespace-nowrap">
              {formatTimeAgo(notification.created_at)}
            </span>
          </div>
          <p className="text-body-sm text-on-surface-variant line-clamp-2 leading-relaxed">
            {notification.description}
          </p>
          
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            <span className="text-[10px] font-bold tracking-wider uppercase text-outline">
              {notification.module_name}
            </span>
            <span className="w-1 h-1 rounded-full bg-outline-variant" />
            <span className="text-[10px] font-bold tracking-wider uppercase text-outline">
              {notification.type}
            </span>
            <span className="w-1 h-1 rounded-full bg-outline-variant" />
            <span className={`text-[10px] font-bold tracking-wider uppercase ${notification.priority === 'Critical' ? 'text-error' : 'text-outline'}`}>
              {notification.priority}
            </span>
          </div>
        </div>

        {/* Quick Actions (Hover) */}
        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex flex-col gap-1">
          {onExecute && (
            <button
              onClick={(e) => { e.stopPropagation(); onExecute(notification); }}
              className="p-1.5 rounded-full hover:bg-primary-container text-primary transition-colors"
              title="Execute Action"
            >
              <span className="material-symbols-outlined text-[18px]">bolt</span>
            </button>
          )}
          <button
            onClick={(e) => { e.stopPropagation(); onToggleRead(notification); }}
            className="p-1.5 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
            title={notification.is_read ? "Mark as unread" : "Mark as read"}
          >
            <span className="material-symbols-outlined text-[18px]">
              {notification.is_read ? 'mark_email_unread' : 'mark_email_read'}
            </span>
          </button>
          {!notification.is_archived ? (
            <button
              onClick={(e) => { e.stopPropagation(); onArchive(notification); }}
              className="p-1.5 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
              title="Archive"
            >
              <span className="material-symbols-outlined text-[18px]">archive</span>
            </button>
          ) : (
            onUnarchive && (
              <button
                onClick={(e) => { e.stopPropagation(); onUnarchive(notification); }}
                className="p-1.5 rounded-full hover:bg-surface-container-high text-on-surface-variant transition-colors"
                title="Unarchive"
              >
                <span className="material-symbols-outlined text-[18px]">unarchive</span>
              </button>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationCard;
