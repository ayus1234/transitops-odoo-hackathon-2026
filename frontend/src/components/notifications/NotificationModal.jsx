import React from 'react';
import Modal from '../ui/Modal';

const NotificationModal = ({ isOpen, onClose, notification, onDelete, onExecute }) => {
  if (!notification) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Notification Details" maxWidth="min-w-[320px] sm:min-w-[500px] max-w-lg">
      <div className="flex flex-col gap-4">
        {/* Header section */}
        <div className="flex items-start gap-4 pb-4 border-b border-outline-variant">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center shrink-0 ${
            notification.priority === 'Critical' ? 'bg-error-container text-error' :
            notification.category === 'Error' ? 'bg-error-container text-error' :
            notification.category === 'Warning' ? 'bg-warning-container text-warning' :
            notification.category === 'Success' ? 'bg-success-container text-success' :
            'bg-primary-container text-primary'
          }`}>
            <span className="material-symbols-outlined text-[24px]">
              {notification.icon || (
                notification.category === 'Error' ? 'error' :
                notification.category === 'Warning' ? 'warning' :
                notification.category === 'Success' ? 'check_circle' : 'info'
              )}
            </span>
          </div>
          <div className="flex-1">
            <h3 className="text-title-lg font-bold text-on-surface mb-1">{notification.title}</h3>
            <div className="flex flex-wrap items-center gap-2 text-body-sm">
              <span className="text-on-surface-variant">
                {new Date(notification.created_at).toLocaleString()}
              </span>
              <span className="w-1 h-1 rounded-full bg-outline-variant" />
              <span className="font-bold text-outline uppercase tracking-wider">{notification.module_name}</span>
              <span className="w-1 h-1 rounded-full bg-outline-variant" />
              <span className="font-bold text-primary">{notification.type}</span>
              <span className="w-1 h-1 rounded-full bg-outline-variant" />
              <span className={`font-bold ${notification.priority === 'Critical' ? 'text-error' : 'text-on-surface-variant'}`}>
                {notification.priority} Priority
              </span>
            </div>
          </div>
        </div>

        {/* Message */}
        <div className="py-2">
          <p className="text-body-lg text-on-surface whitespace-pre-wrap leading-relaxed">
            {notification.description}
          </p>
        </div>

        {/* Metadata section if exists */}
        {notification.metadata && Object.keys(notification.metadata).length > 0 && (
          <div className="bg-surface-container-low rounded-lg p-4 border border-outline-variant mt-2">
            <h4 className="text-label-lg font-bold text-on-surface-variant mb-2">Additional Information</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-body-sm">
              {Object.entries(notification.metadata).map(([key, value]) => (
                <div key={key} className="flex flex-col">
                  <span className="text-outline capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-on-surface font-medium truncate" title={String(value)}>{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        {notification.route && onExecute && (
          <div className="mt-4 pt-4 border-t border-outline-variant flex justify-center">
            <button 
              onClick={() => onExecute(notification)}
              className="bg-primary text-on-primary px-6 py-2 rounded-full font-bold text-label-lg hover:opacity-90 transition-opacity flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[20px]">bolt</span>
              Execute Action
            </button>
          </div>
        )}

        {/* Footer Actions */}
        <div className="flex justify-between items-center mt-4 pt-4 border-t border-outline-variant">
          <button 
            onClick={() => onDelete(notification)}
            className="text-error hover:bg-error-container hover:text-on-error-container px-3 py-1.5 rounded transition-colors text-body-sm font-bold flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[18px]">delete</span>
            Delete
          </button>
          <button 
            onClick={onClose}
            className="text-primary hover:bg-primary-container px-4 py-1.5 rounded transition-colors text-body-sm font-bold"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default NotificationModal;
