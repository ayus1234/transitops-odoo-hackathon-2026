import React, { useState } from 'react';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';

const ScheduleModal = ({ reportId, onClose }) => {
  const [frequency, setFrequency] = useState('daily');
  const [cronExpression, setCronExpression] = useState('0 0 * * *');
  const [emails, setEmails] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { showToast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const payload = {
        frequency,
        cron_expression: frequency === 'custom' ? cronExpression : undefined,
        email_recipients: emails.split(',').map(e => e.trim()).filter(e => e)
      };
      
      await api.post(`/custom-reports/${reportId}/schedule`, payload);
      showToast('Report scheduled successfully', 'success');
      onClose();
    } catch (error) {
      showToast('Failed to schedule report. Ensure you have admin privileges.', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
      <div className="bg-surface rounded-xl shadow-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200" style={{ width: '100%', maxWidth: '448px' }}>
        <div className="p-md border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center">
          <h2 className="text-title-md font-bold text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">schedule</span>
            Schedule Report
          </h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-error transition-colors">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-md space-y-md">
          <div className="space-y-xs">
            <label className="text-label-caps text-on-surface-variant">Frequency</label>
            <select 
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant text-body-sm p-2 rounded focus:ring-primary outline-none focus:border-primary"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="custom">Custom Cron</option>
            </select>
          </div>

          {frequency === 'custom' && (
            <div className="space-y-xs">
              <label className="text-label-caps text-on-surface-variant">Cron Expression</label>
              <input 
                type="text" 
                value={cronExpression}
                onChange={(e) => setCronExpression(e.target.value)}
                placeholder="* * * * *"
                className="w-full bg-surface-container-lowest border border-outline-variant text-body-sm p-2 rounded focus:ring-primary outline-none focus:border-primary font-mono"
                required
              />
            </div>
          )}

          <div className="space-y-xs">
            <label className="text-label-caps text-on-surface-variant">Email Recipients (Comma Separated)</label>
            <textarea 
              value={emails}
              onChange={(e) => setEmails(e.target.value)}
              placeholder="user1@example.com, user2@example.com"
              className="w-full bg-surface-container-lowest border border-outline-variant text-body-sm p-2 rounded focus:ring-primary outline-none focus:border-primary h-20 resize-none"
              required
            />
          </div>

          <div className="flex justify-end gap-sm pt-sm border-t border-outline-variant">
            <button 
              type="button" 
              onClick={onClose}
              className="px-4 py-2 text-body-sm font-bold text-on-surface-variant hover:bg-surface-container rounded transition-colors"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={submitting}
              className="px-4 py-2 text-body-sm font-bold bg-primary text-on-primary rounded hover:bg-primary-container hover:text-on-primary-container transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? <span className="material-symbols-outlined animate-spin text-sm">sync</span> : 'Save Schedule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ScheduleModal;
