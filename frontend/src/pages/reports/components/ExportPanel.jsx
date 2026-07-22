import React, { useState } from 'react';
import api from '../../../services/api';
import { downloadBlobFromResponse, getFormattedDate } from '../../../utils/exportUtils';
import { useToast } from '../../../contexts/ToastContext';

const ExportPanel = ({ reportId, disabled }) => {
  const [downloading, setDownloading] = useState(false);
  const { showToast } = useToast();

  const handleExport = async (format) => {
    if (!reportId) {
      showToast('Please save the report before exporting.', 'warning');
      return;
    }

    try {
      setDownloading(true);
      const response = await api.post(`/custom-reports/${reportId}/export?format=${format}`, {}, {
        responseType: 'blob'
      });
      
      const fallbackName = `custom_report_${getFormattedDate()}.${format === 'excel' ? 'xls' : format}`;
      downloadBlobFromResponse(response, fallbackName);
      
      showToast(`Successfully exported as ${format.toUpperCase()}`, 'success');
    } catch (error) {
      console.error("Export failed", error);
      showToast('Failed to export report.', 'error');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm h-full">
      <h3 className="text-title-sm font-title-sm text-on-surface mb-sm">Export Data</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        <button 
          onClick={() => handleExport('csv')} 
          disabled={disabled || downloading}
          className="flex items-center justify-center gap-xs text-body-sm font-semibold px-2 py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-lg">csv</span> CSV
        </button>
        <button 
          onClick={() => handleExport('excel')} 
          disabled={disabled || downloading}
          className="flex items-center justify-center gap-xs text-body-sm font-semibold px-2 py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-lg">table_view</span> Excel
        </button>
        <button 
          onClick={() => handleExport('pdf')} 
          disabled={disabled || downloading}
          className="flex items-center justify-center gap-xs text-body-sm font-semibold px-2 py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-lg">picture_as_pdf</span> PDF
        </button>
        <button 
          onClick={() => handleExport('json')} 
          disabled={disabled || downloading}
          className="flex items-center justify-center gap-xs text-body-sm font-semibold px-2 py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
        >
          <span className="material-symbols-outlined text-lg">data_object</span> JSON
        </button>
      </div>
    </div>
  );
};

export default ExportPanel;
