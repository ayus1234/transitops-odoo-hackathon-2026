import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

// Components
import StatisticsCards from './components/StatisticsCards';
import ModuleSelector from './components/ModuleSelector';
import FieldSelector from './components/FieldSelector';
import FilterBuilder from './components/FilterBuilder';
import SortGroupBuilder from './components/SortGroupBuilder';
import ChartSelector from './components/ChartSelector';
import PreviewPanel from './components/PreviewPanel';
import ExportPanel from './components/ExportPanel';
import SavedReports from './components/SavedReports';
import ExecutionHistory from './components/ExecutionHistory';
import ScheduleModal from './components/ScheduleModal';

const ReportBuilder = () => {
  const navigate = useNavigate();
  const { showToast } = useToast();

  // Report State
  const [reportId, setReportId] = useState(null);
  const [name, setName] = useState('');
  const [module, setModule] = useState('');
  const [selectedFields, setSelectedFields] = useState([]);
  const [filters, setFilters] = useState([]);
  const [groupBy, setGroupBy] = useState('');
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [chartType, setChartType] = useState('table');
  const [isPublic, setIsPublic] = useState(false);

  // Execution State
  const [executing, setExecuting] = useState(false);
  const [previewData, setPreviewData] = useState([]);
  const [previewColumns, setPreviewColumns] = useState([]);
  const [executionError, setExecutionError] = useState(null);

  // Modals
  const [showSchedule, setShowSchedule] = useState(false);

  const handleModuleChange = (newModule) => {
    setModule(newModule);
    setSelectedFields([]);
    setFilters([]);
    setGroupBy('');
    setSortBy('');
  };

  const handleSelectSavedReport = (report) => {
    setReportId(report.id);
    setName(report.name);
    // Fix case sensitivity for module
    const capModule = report.module ? report.module.charAt(0).toUpperCase() + report.module.slice(1).toLowerCase() : '';
    setModule(capModule);
    setSelectedFields(report.selected_fields || []);
    setFilters(report.filters || []);
    setGroupBy(report.group_by || '');
    setSortBy(report.sort_by || '');
    setSortOrder(report.sort_order || 'asc');
    setChartType(report.chart_type || 'table');
    setIsPublic(report.is_public || false);
    
    // Clear preview when loading saved report
    setPreviewData([]);
    setPreviewColumns([]);
    setExecutionError(null);
  };

  const resetForm = () => {
    setReportId(null);
    setName('');
    setModule('');
    setSelectedFields([]);
    setFilters([]);
    setGroupBy('');
    setSortBy('');
    setSortOrder('asc');
    setChartType('table');
    setIsPublic(false);
    setPreviewData([]);
    setPreviewColumns([]);
    setExecutionError(null);
  };

  const saveReport = async () => {
    if (!name || !module || selectedFields.length === 0) {
      showToast('Please provide a name, select a module, and at least one field.', 'warning');
      return null;
    }

    const payload = {
      name,
      module,
      selected_fields: selectedFields,
      filters,
      group_by: groupBy || null,
      sort_by: sortBy || null,
      sort_order: sortOrder,
      chart_type: chartType,
      is_public: isPublic
    };

    try {
      let res;
      if (reportId) {
        res = await api.put(`/custom-reports/${reportId}`, payload);
        showToast('Report updated successfully.', 'success');
      } else {
        res = await api.post('/custom-reports', payload);
        setReportId(res.data.id);
        showToast('Report created successfully.', 'success');
      }
      return res.data.id;
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to save report.', 'error');
      return null;
    }
  };

  const handleSaveAndExecute = async () => {
    // We must save the report first because /execute requires a report ID
    const currentId = await saveReport();
    if (!currentId) return;

    try {
      setExecuting(true);
      setExecutionError(null);
      const res = await api.post(`/custom-reports/${currentId}/execute`);
      setPreviewData(res.data.data);
      setPreviewColumns(res.data.columns);
    } catch (error) {
      setExecutionError(error.response?.data?.detail || 'Failed to execute report.');
      showToast('Execution failed.', 'error');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-background">
      {showSchedule && reportId && <ScheduleModal reportId={reportId} onClose={() => setShowSchedule(false)} />}
      
      <div className="p-3 md:p-lg space-y-lg min-w-0">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4 mb-4">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/reports')} className="p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors">
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Enterprise Report Builder</h1>
              <p className="font-body-md text-body-md text-on-surface-variant mt-1">Design, execute, and schedule custom analytics</p>
            </div>
          </div>
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <button onClick={resetForm} className="px-4 py-2 text-on-surface-variant font-bold border border-outline rounded-lg hover:bg-surface-container transition-all">
              New Report
            </button>
            {reportId && (
              <button onClick={() => setShowSchedule(true)} className="px-4 py-2 text-primary font-bold border border-primary rounded-lg hover:bg-primary-container/10 transition-all flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">schedule</span> Schedule
              </button>
            )}
            <button onClick={saveReport} className="px-4 py-2 bg-secondary text-on-secondary font-bold rounded-lg hover:bg-secondary/90 transition-all flex items-center gap-2">
              <span className="material-symbols-outlined text-sm">save</span> Save
            </button>
            <button onClick={handleSaveAndExecute} disabled={executing} className="px-4 py-2 bg-primary text-on-primary font-bold rounded-lg hover:bg-primary-container hover:text-on-primary-container transition-all flex items-center gap-2 disabled:opacity-50 shadow-sm">
              <span className={`material-symbols-outlined text-sm ${executing ? 'animate-spin' : ''}`}>
                {executing ? 'sync' : 'play_arrow'}
              </span> 
              Generate
            </button>
          </div>
        </div>

        <StatisticsCards />

        <div className="grid grid-cols-12 gap-lg">
          
          {/* Left Column: Builder Controls */}
          <div className="col-span-12 lg:col-span-8 space-y-md flex flex-col">
            
            {/* Metadata Configuration */}
            <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm flex flex-col sm:flex-row gap-4 items-center">
              <div className="flex-1 w-full">
                <label className="text-label-caps text-on-surface-variant block mb-1">Report Name</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Monthly Maintenance Costs"
                  className="w-full bg-surface-container-lowest border border-outline-variant text-body-md p-2 rounded focus:ring-primary outline-none focus:border-primary"
                />
              </div>
              <div className="flex items-center gap-2 mt-4 sm:mt-0 pt-4 sm:pt-0">
                <input 
                  type="checkbox" 
                  id="is_public"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="rounded text-primary focus:ring-primary w-4 h-4"
                />
                <label htmlFor="is_public" className="text-body-sm text-on-surface cursor-pointer font-bold flex items-center gap-1">
                  Make Public <span className="material-symbols-outlined text-sm text-on-surface-variant">info</span>
                </label>
              </div>
            </div>

            <ModuleSelector selectedModule={module} onChange={handleModuleChange} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-md flex-1">
              <FieldSelector module={module} selectedFields={selectedFields} onChange={setSelectedFields} />
              <div className="flex flex-col gap-md">
                <FilterBuilder module={module} filters={filters} onChange={setFilters} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
              <SortGroupBuilder 
                module={module}
                groupBy={groupBy} setGroupBy={setGroupBy}
                sortBy={sortBy} setSortBy={setSortBy}
                sortOrder={sortOrder} setSortOrder={setSortOrder}
              />
              <ChartSelector selectedChart={chartType} onChange={setChartType} />
            </div>

            <div className="mt-md">
              <PreviewPanel 
                loading={executing}
                error={executionError}
                data={previewData}
                columns={previewColumns}
                chartType={chartType}
              />
            </div>
            
          </div>

          {/* Right Column: Saved Reports & History & Exports */}
          <div className="col-span-12 lg:col-span-4 flex flex-col gap-md">
            <div className="h-[400px]">
              <SavedReports onSelectReport={handleSelectSavedReport} />
            </div>
            
            <ExportPanel reportId={reportId} disabled={!reportId || executing || previewData.length === 0} />
            
            {reportId && (
              <ExecutionHistory reportId={reportId} />
            )}
          </div>

        </div>
      </div>
    </div>
  );
};

export default ReportBuilder;
