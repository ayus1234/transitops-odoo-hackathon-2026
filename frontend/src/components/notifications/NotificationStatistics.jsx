import React, { useEffect, useState } from 'react';
import Modal from '../ui/Modal';
import { getNotificationStatistics } from '../../services/notificationApi';
import { useToast } from '../../contexts/ToastContext';

const NotificationStatistics = ({ isOpen, onClose }) => {
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast } = useToast();

  useEffect(() => {
    const fetchStats = async () => {
      if (!isOpen) return;
      setIsLoading(true);
      try {
        const data = await getNotificationStatistics();
        setStats(data);
      } catch (error) {
        showToast('Failed to load notification statistics', 'error');
        console.error('Stats error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [isOpen, showToast]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Notification Statistics" maxWidth="min-w-[320px] sm:min-w-[400px] max-w-sm">
      {isLoading ? (
        <div className="flex justify-center p-8">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : stats ? (
        <div className="flex flex-col gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant flex flex-col items-center justify-center">
              <span className="text-display-sm font-bold text-primary">{stats.total}</span>
              <span className="text-body-sm text-on-surface-variant uppercase tracking-wider font-bold">Total</span>
            </div>
            <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant flex flex-col items-center justify-center">
              <span className="text-display-sm font-bold text-error">{stats.unread}</span>
              <span className="text-body-sm text-on-surface-variant uppercase tracking-wider font-bold">Unread</span>
            </div>
            <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant flex flex-col items-center justify-center">
              <span className="text-display-sm font-bold text-success">{stats.read}</span>
              <span className="text-body-sm text-on-surface-variant uppercase tracking-wider font-bold">Read</span>
            </div>
            <div className="bg-surface-container-low p-4 rounded-lg border border-outline-variant flex flex-col items-center justify-center">
              <span className="text-display-sm font-bold text-outline">{stats.archived}</span>
              <span className="text-body-sm text-on-surface-variant uppercase tracking-wider font-bold">Archived</span>
            </div>
          </div>

          <h4 className="text-title-sm font-bold text-on-surface mt-2 border-b border-outline-variant pb-2">By Priority</h4>
          <div className="space-y-2">
            {Object.entries(stats.by_priority || {}).map(([priority, count]) => (
              <div key={priority} className="flex justify-between items-center text-body-md">
                <span className={`font-medium ${
                  priority === 'Critical' ? 'text-error font-bold' :
                  priority === 'High' ? 'text-warning' : 'text-on-surface'
                }`}>{priority}</span>
                <span className="bg-surface-container-high px-2 py-0.5 rounded-full text-body-sm">{count}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-2 flex justify-end">
            <button 
              onClick={onClose}
              className="text-primary hover:bg-primary-container px-4 py-2 rounded-full transition-colors text-label-lg font-bold"
            >
              Close
            </button>
          </div>
        </div>
      ) : (
        <div className="p-4 text-center text-on-surface-variant">No data available</div>
      )}
    </Modal>
  );
};

export default NotificationStatistics;
