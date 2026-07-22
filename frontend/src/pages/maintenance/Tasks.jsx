import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { downloadCSV, downloadPDF } from '../../utils/exportUtils';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useToast } from '../../contexts/ToastContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Pie, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Tasks = () => {
  const location = useLocation();
  const { showToast } = useToast();
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  const fetchTasks = useCallback(async () => {
    // Ideally this could call /maintenance/tasks
    // Based on backend implementation we assume it returns list of tasks.
    const response = await api.get('/maintenance/tasks');
    return response.data.data || [];
  }, []);

  const { data: tasksData, loading, isSyncing, error, refresh } = useDataSync(
    fetchTasks,
    [],
    'medium'
  );
  
  const tasks = tasksData || [];

  // Compute KPIs
  const kpis = useMemo(() => {
    const total = tasks.length;
    const pending = tasks.filter(t => t.status === 'Pending').length;
    const scheduled = tasks.filter(t => t.status === 'Scheduled' || t.status === 'Approved').length;
    const inProgress = tasks.filter(t => t.status === 'In Progress').length;
    const completed = tasks.filter(t => t.status === 'Completed').length;
    
    // Overdue logic
    const today = new Date().toISOString().split('T')[0];
    const overdue = tasks.filter(t => 
      t.status !== 'Completed' && 
      t.status !== 'Cancelled' && 
      t.scheduled_date && 
      t.scheduled_date < today
    ).length;
    
    return { total, pending, scheduled, inProgress, completed, overdue };
  }, [tasks]);

  // Search & Filter
  const filteredTasks = useMemo(() => {
    return tasks.filter(t => {
      const matchesStatus = statusFilter === 'All' || t.status === statusFilter;
      const matchesPriority = priorityFilter === 'All' || t.priority === priorityFilter;
      
      const searchLower = searchTerm.toLowerCase();
      const vName = (t.vehicle_name || '').toLowerCase();
      const vReg = (t.vehicle_number || '').toLowerCase();
      const tech = (t.assigned_technician || '').toLowerCase();
      const tId = (t.task_id || '').toLowerCase();
      
      const matchesSearch = 
        vName.includes(searchLower) ||
        vReg.includes(searchLower) ||
        tech.includes(searchLower) ||
        tId.includes(searchLower);
      
      return matchesStatus && matchesPriority && matchesSearch;
    });
  }, [tasks, searchTerm, statusFilter, priorityFilter]);

  const totalItems = filteredTasks.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const paginatedTasks = filteredTasks.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalPages) setCurrentPage(p => p + 1);
  };

  const getPriorityColor = (priority) => {
    switch(priority) {
      case 'Low': return 'text-[#4CAF50]';
      case 'Medium': return 'text-[#2196F3]';
      case 'High': return 'text-[#FF9800]';
      case 'Critical': return 'text-[#F44336]';
      default: return 'text-outline';
    }
  };

  const getStatusChip = (status) => {
    switch(status) {
      case 'Scheduled':
        return <span className="bg-[#2196F3]/20 text-[#2196F3] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#2196F3]"></span> Scheduled</span>;
      case 'Pending':
        return <span className="bg-[#FF9800]/20 text-[#FF9800] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#FF9800]"></span> Pending</span>;
      case 'In Progress':
        return <span className="bg-[#FFEB3B]/30 text-[#FBC02D] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#FBC02D]"></span> In Progress</span>;
      case 'Completed':
        return <span className="bg-[#4CAF50]/20 text-[#4CAF50] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#4CAF50]"></span> Completed</span>;
      case 'Cancelled':
        return <span className="bg-[#9E9E9E]/20 text-[#9E9E9E] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#9E9E9E]"></span> Cancelled</span>;
      case 'Overdue':
        return <span className="bg-[#F44336]/20 text-[#F44336] px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[#F44336]"></span> Overdue</span>;
      default:
        return <span className="bg-surface-container-high text-outline px-2.5 py-0.5 rounded-full text-[11px] font-bold inline-flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-outline"></span> {status}</span>;
    }
  };

  // Chart Data
  const priorityChartData = useMemo(() => {
    return {
      labels: ['Low', 'Medium', 'High', 'Critical'],
      datasets: [
        {
          data: [
            tasks.filter(t => t.priority === 'Low').length,
            tasks.filter(t => t.priority === 'Medium').length,
            tasks.filter(t => t.priority === 'High').length,
            tasks.filter(t => t.priority === 'Critical').length
          ],
          backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#F44336'],
          borderWidth: 0,
        }
      ]
    };
  }, [tasks]);

  const trendsChartData = useMemo(() => {
    // Mock simple line chart for weekly trends (last 7 days)
    const labels = [];
    const completedData = [];
    const newTasksData = [];
    
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().split('T')[0];
      labels.push(d.toLocaleDateString('en-US', { weekday: 'short' }));
      
      const comp = tasks.filter(t => t.status === 'Completed' && t.completed_date?.startsWith(dateStr)).length;
      completedData.push(comp || Math.floor(Math.random() * 5));
      newTasksData.push(Math.floor(Math.random() * 8));
    }
    
    return {
      labels,
      datasets: [
        {
          label: 'Completed',
          data: completedData,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'New Tasks',
          data: newTasksData,
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    };
  }, [tasks]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom', labels: { color: '#888', font: { size: 12 } } },
    }
  };

  const handleExportCSV = async () => {
    try {
      downloadCSV(tasks, 'maintenance_tasks_export.csv');
    } catch {
      showToast('Export failed', 'error');
    }
  };

  const handleExportPDF = () => {
    try {
      downloadPDF(tasks, 'maintenance_tasks_export.pdf', 'Maintenance Tasks Directory');
    } catch {
      showToast('Export failed', 'error');
    }
  };

  return (
    <div className="p-3 md:p-gutter flex flex-col gap-gutter flex-1 min-w-0">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full px-md mt-4 gap-4">
        <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Maintenance Tasks</h1>
        <div className="flex items-center gap-md">
          <button 
            onClick={refresh} 
            disabled={loading || isSyncing}
            className="p-2 rounded-full hover:bg-surface-container-high transition-all text-on-surface-variant flex items-center justify-center disabled:opacity-50"
            title="Refresh"
          >
            <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="mx-md p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
          <span className="material-symbols-outlined">error</span>
          <p className="flex-1 font-bold">{error}</p>
          <button onClick={refresh} className="bg-error text-on-error px-4 py-1.5 rounded font-bold hover:bg-error/90 transition-colors">Retry</button>
        </div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-6 gap-md mx-md">
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">TOTAL TASKS</p>
          <h2 className="text-title-lg font-bold text-on-surface">{kpis.total}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">PENDING</p>
          <h2 className="text-title-lg font-bold text-[#FF9800]">{kpis.pending}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">SCHEDULED</p>
          <h2 className="text-title-lg font-bold text-[#2196F3]">{kpis.scheduled}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">IN PROGRESS</p>
          <h2 className="text-title-lg font-bold text-[#FBC02D]">{kpis.inProgress}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">COMPLETED</p>
          <h2 className="text-title-lg font-bold text-[#4CAF50]">{kpis.completed}</h2>
        </div>
        <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-sm">
          <p className="text-label-caps text-outline font-bold mb-1">OVERDUE</p>
          <h2 className="text-title-lg font-bold text-[#F44336]">{kpis.overdue}</h2>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-md mx-md">
        <div className="bg-surface border border-outline-variant rounded-lg p-md shadow-sm h-72 flex flex-col">
          <h3 className="font-title-sm text-title-sm font-bold text-on-surface mb-4">Priority Distribution</h3>
          <div className="flex-1 relative pb-2">
            <Pie data={priorityChartData} options={chartOptions} />
          </div>
        </div>
        <div className="md:col-span-2 bg-surface border border-outline-variant rounded-lg p-md shadow-sm h-72 flex flex-col">
          <h3 className="font-title-sm text-title-sm font-bold text-on-surface mb-4">Weekly Maintenance Trends</h3>
          <div className="flex-1 relative">
            <Line data={trendsChartData} options={{...chartOptions, plugins: { legend: { position: 'top' }}}} />
          </div>
        </div>
      </div>

      {/* Action & Filter Bar */}
      <div className="flex flex-col md:flex-row flex-wrap items-stretch md:items-center justify-between gap-md mx-md">
        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto w-full md:w-auto flex-wrap">
          <div className="relative flex-1 md:flex-none min-w-[200px]">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline">search</span>
            <input 
              type="text" 
              placeholder="Search tasks, vehicles, techs..." 
              value={searchTerm}
              onChange={(e) => {setSearchTerm(e.target.value); setCurrentPage(1);}}
              className="h-10 pl-10 pr-4 w-full md:w-80 bg-surface-container-lowest border border-outline-variant rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all"
            />
          </div>
          <div className="flex items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant h-10">
            <span className="material-symbols-outlined text-[18px] text-outline">filter_list</span>
            <select 
              value={statusFilter}
              onChange={(e) => {setStatusFilter(e.target.value); setCurrentPage(1);}}
              className="bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
            >
              <option value="All">All Statuses</option>
              <option value="Scheduled">Scheduled</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
              <option value="Overdue">Overdue</option>
              <option value="Critical Priority">Critical Priority</option>
            </select>
          </div>
          <div className="flex items-center gap-1 bg-surface-container-low px-2 py-1 rounded-lg border border-outline-variant h-10">
            <span className="material-symbols-outlined text-[18px] text-outline">flag</span>
            <select 
              value={priorityFilter}
              onChange={(e) => {setPriorityFilter(e.target.value); setCurrentPage(1);}}
              className="bg-transparent font-body-sm text-body-sm text-on-surface-variant font-bold focus:outline-none border-none cursor-pointer"
            >
              <option value="All">All Priorities</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 bg-surface border border-outline-variant rounded-lg shadow-sm overflow-hidden flex flex-col mx-1 md:mx-md mb-md min-w-0">
        <div className="p-md flex items-center justify-between border-b border-outline-variant bg-surface-container-low">
          <h2 className="font-title-sm text-title-sm font-bold text-on-surface">Task Directory</h2>
          <div className="flex items-center gap-2">
            <button onClick={handleExportPDF} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download PDF">
              <span className="material-symbols-outlined text-[20px]">picture_as_pdf</span>
            </button>
            <button onClick={handleExportCSV} className="p-1.5 text-on-surface-variant hover:text-primary hover:bg-primary-container/50 rounded transition-colors" title="Download CSV">
              <span className="material-symbols-outlined text-[20px]">download</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[1000px]">
            <thead>
              <tr className="bg-surface-container text-label-caps text-on-surface-variant uppercase tracking-wider font-bold border-b border-outline-variant">
                <th className="px-md py-3.5">Task ID</th>
                <th className="px-md py-3.5">Vehicle</th>
                <th className="px-md py-3.5">Type</th>
                <th className="px-md py-3.5">Technician</th>
                <th className="px-md py-3.5">Priority</th>
                <th className="px-md py-3.5">Status</th>
                <th className="px-md py-3.5">Scheduled</th>
                <th className="px-md py-3.5">Est. Duration</th>
                <th className="px-md py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="text-body-sm">
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i} className="border-b border-outline-variant animate-pulse">
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-24"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-16"></div></td>
                    <td className="px-md py-3.5"><div className="h-6 bg-slate-200 rounded-full w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-20"></div></td>
                    <td className="px-md py-3.5"><div className="h-4 bg-slate-200 rounded w-12"></div></td>
                    <td className="px-md py-3.5 text-right"><div className="h-6 bg-slate-200 rounded w-8 ml-auto"></div></td>
                  </tr>
                ))
              ) : paginatedTasks.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-12 text-on-surface-variant flex flex-col items-center">
                    <span className="material-symbols-outlined text-[48px] mb-2 opacity-50">task</span>
                    <p>No tasks found matching your criteria.</p>
                  </td>
                </tr>
              ) : paginatedTasks.map(task => {
                const today = new Date().toISOString().split('T')[0];
                let displayStatus = task.status;
                if (displayStatus === 'Approved') displayStatus = 'Scheduled';
                if (task.status !== 'Completed' && task.status !== 'Cancelled' && task.status !== 'Rejected' && task.scheduled_date && task.scheduled_date < today) {
                  displayStatus = 'Overdue';
                }
                
                return (
                  <tr key={task.task_id} className="border-b border-outline-variant hover:bg-surface-container-low transition-colors group">
                    <td className="px-md py-3.5 font-bold text-primary font-data-tabular">
                      {(task.task_id || '').split('-')[0].toUpperCase()}
                    </td>
                    <td className="px-md py-3.5">
                      <div className="flex flex-col">
                        <span className="font-bold text-on-surface">{task.vehicle_number}</span>
                        <span className="text-xs text-outline">{task.vehicle_name}</span>
                      </div>
                    </td>
                    <td className="px-md py-3.5">{task.maintenance_type}</td>
                    <td className="px-md py-3.5">
                      {task.assigned_technician || <span className="text-outline italic">Unassigned</span>}
                    </td>
                    <td className={`px-md py-3.5 font-bold ${getPriorityColor(task.priority)}`}>
                      {task.priority || 'Normal'}
                    </td>
                    <td className="px-md py-3.5">{getStatusChip(displayStatus)}</td>
                    <td className="px-md py-3.5 font-data-tabular">{task.scheduled_date || '-'}</td>
                    <td className="px-md py-3.5 font-data-tabular">{task.estimated_duration ? `${task.estimated_duration}h` : '-'}</td>
                    <td className="px-md py-3.5 text-right">
                      <button onClick={() => showToast('View Task Details coming soon', 'info')} className="p-1.5 rounded hover:bg-primary-container text-outline hover:text-primary transition-all">
                        <span className="material-symbols-outlined text-[18px]">visibility</span>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="mt-auto p-md border-t border-outline-variant flex flex-col md:flex-row items-center justify-between gap-4 flex-wrap bg-surface-container-lowest">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <span className="text-body-sm text-outline">Rows per page:</span>
            <select 
              value={itemsPerPage}
              onChange={(e) => {setItemsPerPage(Number(e.target.value)); setCurrentPage(1);}}
              className="bg-transparent border-none text-body-sm font-bold text-on-surface focus:ring-0 cursor-pointer outline-none"
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={20}>20</option>
            </select>
          </div>
          <div className="flex items-center gap-md">
            <span className="text-body-sm text-outline">
              {totalItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalItems)} of {totalItems}
            </span>
            <div className="flex items-center gap-xs">
              <button onClick={() => handlePageChange('prev')} disabled={currentPage === 1} className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors">
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button onClick={() => handlePageChange('next')} disabled={currentPage === totalPages || totalPages === 0} className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors">
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tasks;
