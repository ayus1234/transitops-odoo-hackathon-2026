import React, { useEffect, useState, useCallback } from 'react';
import api from '../../../services/api';
import { useToast } from '../../../contexts/ToastContext';
import { useDataSync } from '../../../contexts/RealTimeSyncContext';

const SavedReports = ({ onSelectReport }) => {
  const { showToast } = useToast();

  const fetchReports = useCallback(async () => {
    const res = await api.get('/custom-reports');
    return res.data.items || [];
  }, []);

  const { data: reportsData, loading, isSyncing, error, refresh } = useDataSync(
    fetchReports,
    [],
    'low'
  );

  const reports = reportsData || [];

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this report?")) return;
    try {
      await api.delete(`/custom-reports/${id}`);
      showToast('Report deleted successfully', 'success');
      refresh();
    } catch (error) {
      showToast('Failed to delete report', 'error');
    }
  };

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm h-full flex flex-col">
      <div className="flex justify-between items-center mb-sm">
        <h3 className="text-title-sm font-title-sm text-on-surface">Saved Reports</h3>
        <button onClick={refresh} disabled={loading || isSyncing} className="text-on-surface-variant hover:text-primary transition-colors disabled:opacity-50">
          <span className={`material-symbols-outlined text-sm ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 space-y-2">
        {loading && <p className="text-body-sm text-on-surface-variant text-center py-4">Loading reports...</p>}
        {!loading && reports.length === 0 && (
          <p className="text-body-sm text-on-surface-variant text-center py-4">No saved reports found.</p>
        )}
        {!loading && reports.map(report => (
          <div 
            key={report.id} 
            onClick={() => onSelectReport(report)}
            className="p-3 bg-surface-container-lowest border border-outline-variant rounded hover:bg-surface-container-low cursor-pointer transition-colors group"
          >
            <div className="flex justify-between items-start">
              <div>
                <p className="font-bold text-body-sm text-on-surface flex items-center gap-2">
                  {report.name}
                  {report.is_public && <span className="material-symbols-outlined text-[14px] text-primary" title="Public Report">public</span>}
                </p>
                <p className="text-[11px] text-on-surface-variant uppercase tracking-wide mt-0.5">{report.module}</p>
              </div>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={(e) => handleDelete(e, report.id)} className="text-error hover:bg-error-container p-1 rounded transition-colors" title="Delete">
                  <span className="material-symbols-outlined text-sm">delete</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SavedReports;
