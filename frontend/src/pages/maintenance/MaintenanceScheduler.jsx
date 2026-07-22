import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import api from '../../services/api';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useNavigate } from 'react-router-dom';

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const HOURS_OF_DAY = Array.from({ length: 24 }, (_, i) => i);

export default function MaintenanceScheduler() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [currentView, setCurrentView] = useState('month'); // 'month', 'week', 'day'
  const [currentDate, setCurrentDate] = useState(new Date());
  
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [rescheduleData, setRescheduleData] = useState({
    scheduled_date: '',
    start_time: '',
    end_time: '',
  });

  const canReschedule = user?.role === 'System Admin' || user?.role === 'Fleet Manager' || user?.role === 'Super Admin' || user?.role === 'Administrator' || user?.role?.name === 'Super Admin' || user?.role?.name === 'Administrator';

  // Format date helper (Uses local timezone to avoid UTC boundary shifts)
  const formatDate = (date) => {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };

  const getWeekStartDate = (date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  };

  // Debounce search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Fetch All Data
  const fetchAllData = useCallback(async () => {
    let calendarRes;
    
    // Determine if we should use search/filter or standard views
    if (debouncedSearch.trim().length > 0) {
      calendarRes = await api.get(`/maintenance/scheduler/search?q=${encodeURIComponent(debouncedSearch)}`);
    } else if (filters.status || filters.priority) {
      let url = `/maintenance/scheduler/filter?`;
      if (filters.status) url += `status=${filters.status}&`;
      if (filters.priority) url += `priority=${filters.priority}&`;
      calendarRes = await api.get(url);
    } else {
      // Standard views
      if (currentView === 'month') {
        calendarRes = await api.get(`/maintenance/scheduler/month?year=${currentDate.getFullYear()}&month=${currentDate.getMonth() + 1}`);
      } else if (currentView === 'week') {
        const weekStart = getWeekStartDate(currentDate);
        calendarRes = await api.get(`/maintenance/scheduler/week?start_date=${formatDate(weekStart)}`);
      } else if (currentView === 'day') {
        calendarRes = await api.get(`/maintenance/scheduler/day?day_date=${formatDate(currentDate)}`);
      }
    }
    
    const [upcomingRes, completedRes] = await Promise.all([
      api.get('/maintenance/scheduler/upcoming'),
      api.get('/maintenance/scheduler/completed')
    ]);

    return {
      events: calendarRes?.data?.data || [],
      upcomingJobs: upcomingRes.data.data || [],
      completedJobs: completedRes.data.data || []
    };
  }, [currentView, currentDate, debouncedSearch, filters]);

  const { data, loading, isSyncing, error, refresh, silentRefresh } = useDataSync(
    fetchAllData,
    [currentView, currentDate, debouncedSearch, filters],
    'medium'
  );

  const events = data?.events || [];
  const upcomingJobs = data?.upcomingJobs || [];
  const completedJobs = data?.completedJobs || [];

  // Handle Reschedule Modal
  const openRescheduleModal = (event) => {
    if (!canReschedule || event.status === 'Completed') return;
    setSelectedEvent(event);
    setRescheduleData({
      scheduled_date: event.scheduled_date || '',
      start_time: event.start_time || '',
      end_time: event.end_time || '',
    });
    setIsModalOpen(true);
  };

  const handleRescheduleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/maintenance/scheduler/${selectedEvent.id}/reschedule`, rescheduleData);
      showToast("Maintenance rescheduled successfully", "success");
      setIsModalOpen(false);
      silentRefresh();
    } catch (err) {
      showToast(err.response?.data?.error?.message || "Failed to reschedule", "error");
    }
  };

  // Nav actions
  const nextDate = () => {
    const next = new Date(currentDate);
    if (currentView === 'month') next.setMonth(next.getMonth() + 1);
    if (currentView === 'week') next.setDate(next.getDate() + 7);
    if (currentView === 'day') next.setDate(next.getDate() + 1);
    setCurrentDate(next);
  };

  const prevDate = () => {
    const prev = new Date(currentDate);
    if (currentView === 'month') prev.setMonth(prev.getMonth() - 1);
    if (currentView === 'week') prev.setDate(prev.getDate() - 7);
    if (currentView === 'day') prev.setDate(prev.getDate() - 1);
    setCurrentDate(prev);
  };

  const goToday = () => setCurrentDate(new Date());

  // Colors
  const getColorClass = (colorName) => {
    switch (colorName.toLowerCase()) {
      case 'red': return 'bg-error-container text-on-error-container border-error';
      case 'blue': return 'bg-primary-container text-on-primary-container border-primary';
      case 'green': return 'bg-tertiary-container text-on-tertiary-container border-tertiary';
      case 'yellow': return 'bg-secondary-container text-on-secondary-container border-secondary';
      case 'orange': return 'bg-orange-100 text-orange-800 border-orange-500';
      case 'gray': return 'bg-surface-variant text-on-surface-variant border-outline';
      default: return 'bg-primary-container text-on-primary-container border-primary';
    }
  };

  // Render Event Card
  const EventCard = ({ event, isCompact = false }) => {
    return (
      <div 
        onClick={() => openRescheduleModal(event)}
        className={`p-1.5 rounded border-l-4 text-xs cursor-pointer truncate shadow-sm transition-transform hover:scale-[1.02] ${getColorClass(event.color)} ${!canReschedule || event.status === 'Completed' ? '' : 'hover:opacity-80'}`}
        title={`${event.title} - ${event.technician_name || 'Unassigned'} - ${event.status}`}
      >
        <div className="font-bold truncate">{event.title}</div>
        {!isCompact && (
          <>
            <div className="truncate opacity-90">{event.vehicle_name}</div>
            {event.start_time && (
              <div className="text-[10px] mt-0.5 font-medium opacity-80">
                {event.start_time.substring(0, 5)} {event.end_time ? `- ${event.end_time.substring(0, 5)}` : ''}
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  // Render Month View
  const renderMonthView = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const cells = [];
    // Padding empty cells
    for (let i = 0; i < firstDay; i++) {
      cells.push(<div key={`empty-${i}`} className="min-h-[100px] bg-surface-container-lowest/50 border border-outline-variant p-2"></div>);
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayEvents = events.filter(e => e.scheduled_date === dateStr);
      const isToday = formatDate(new Date()) === dateStr;

      cells.push(
        <div key={day} className={`min-h-[120px] bg-surface border border-outline-variant p-1.5 flex flex-col gap-1 ${isToday ? 'bg-primary/5 border-primary' : ''}`}>
          <div className={`text-right font-medium text-sm p-1 ${isToday ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
            {day}
          </div>
          <div className="flex flex-col gap-1 overflow-y-auto max-h-[90px] custom-scrollbar hide-scrollbar">
            {dayEvents.slice(0, 2).map(e => <EventCard key={e.id} event={e} />)}
          </div>
        </div>
      );
    }

    return (
      <div className="w-full overflow-x-auto">
        <div className="min-w-[700px]">
          <div className="grid grid-cols-7 border-b border-outline-variant bg-surface-container-low rounded-t-lg">
          {DAYS_OF_WEEK.map(day => (
            <div key={day} className="py-2 text-center text-xs font-bold uppercase text-on-surface-variant">{day}</div>
          ))}
        </div>
          <div className="grid grid-cols-7 rounded-b-lg overflow-hidden">
            {cells}
          </div>
        </div>
      </div>
    );
  };

  // Render Week View
  const renderWeekView = () => {
    const weekStart = getWeekStartDate(currentDate);
    const weekDays = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(weekStart);
      d.setDate(d.getDate() + i);
      return d;
    });

    return (
      <div className="w-full overflow-x-auto">
        <div className="flex bg-surface border border-outline-variant rounded-lg overflow-hidden min-w-[700px]">
          {/* Timeline Axis */}
        <div className="w-16 flex flex-col border-r border-outline-variant bg-surface-container-lowest flex-shrink-0">
          <div className="h-12 border-b border-outline-variant"></div>
          {HOURS_OF_DAY.map(h => (
            <div key={h} className="h-16 border-b border-outline-variant text-right pr-2 pt-1 text-[10px] text-on-surface-variant font-medium">
              {h}:00
            </div>
          ))}
        </div>
        
        {/* Days Grid */}
        <div className="flex-1 grid grid-cols-7">
          {weekDays.map(date => {
            const dateStr = formatDate(date);
            const dayEvents = events.filter(e => e.scheduled_date === dateStr).slice(0, 2);
            const isToday = formatDate(new Date()) === dateStr;

            return (
              <div key={dateStr} className="flex flex-col border-r border-outline-variant last:border-r-0 min-w-0">
                {/* Header */}
                <div className={`h-12 border-b border-outline-variant flex flex-col items-center justify-center ${isToday ? 'bg-primary/5' : 'bg-surface-container-low'}`}>
                  <span className="text-[10px] font-bold uppercase text-on-surface-variant">{DAYS_OF_WEEK[date.getDay()]}</span>
                  <span className={`text-sm ${isToday ? 'text-primary font-bold' : 'text-on-surface'}`}>{date.getDate()}</span>
                </div>
                
                {/* Hourly Slots (Simplified rendering for grid visualization) */}
                <div className="relative h-[1536px]"> {/* 24 hours * 64px (h-16) = 1536px */}
                  {HOURS_OF_DAY.map(h => (
                    <div key={`slot-${h}`} className="h-16 border-b border-outline-variant border-dashed opacity-50"></div>
                  ))}
                  
                  {/* Position Events Absolutely */}
                  {dayEvents.map((e, index) => {
                    let top = 0;
                    let height = 60; // default block height
                    let startMins = 0;
                    let endMins = 60;
                    
                    if (e.start_time) {
                      const [hours, mins] = e.start_time.split(':').map(Number);
                      startMins = (hours * 60) + mins;
                      top = (hours * 64) + (mins / 60 * 64);
                      if (e.end_time) {
                        const [eh, em] = e.end_time.split(':').map(Number);
                        endMins = (eh * 60) + em;
                        height = Math.max(32, ((endMins - startMins) / 60 * 64) - 4);
                      } else if (e.estimated_duration) {
                        endMins = startMins + e.estimated_duration;
                        height = Math.max(32, (e.estimated_duration / 60 * 64) - 4);
                      }
                    }

                    return (
                      <div 
                        key={e.id} 
                        className="absolute w-full px-0.5 z-10 transition-transform hover:z-50 hover:scale-[1.02]" 
                        style={{ top: `${top}px`, height: `${height}px` }}
                      >
                        <div className="h-full w-full">
                           <EventCard event={e} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
        </div>
      </div>
    );
  };

  // Render Day View
  const renderDayView = () => {
    const dateStr = formatDate(currentDate);
    const dayEvents = events.filter(e => e.scheduled_date === dateStr).slice(0, 2);

    return (
      <div className="w-full flex bg-surface border border-outline-variant rounded-lg overflow-hidden">
        {/* Timeline Axis */}
        <div className="w-20 flex flex-col border-r border-outline-variant bg-surface-container-lowest flex-shrink-0">
          {HOURS_OF_DAY.map(h => (
            <div key={h} className="h-24 border-b border-outline-variant text-right pr-3 pt-2 text-xs text-on-surface-variant font-medium">
              {h}:00
            </div>
          ))}
        </div>
        
        {/* Day Column */}
        <div className="flex-1 relative min-h-[576px] bg-surface">
          {HOURS_OF_DAY.map(h => (
            <div key={`slot-${h}`} className="h-24 border-b border-outline-variant border-dashed opacity-50"></div>
          ))}
          
          {dayEvents.map((e, index) => {
            let top = 0;
            let height = 90; 
            let startMins = 0;
            let endMins = 60;
            
            if (e.start_time) {
              const [hours, mins] = e.start_time.split(':').map(Number);
              startMins = (hours * 60) + mins;
              top = (hours * 96) + (mins / 60 * 96);
              if (e.end_time) {
                const [eh, em] = e.end_time.split(':').map(Number);
                endMins = (eh * 60) + em;
                height = Math.max(48, ((endMins - startMins) / 60 * 96) - 6);
              } else if (e.estimated_duration) {
                endMins = startMins + e.estimated_duration;
                height = Math.max(48, (e.estimated_duration / 60 * 96) - 6);
              }
            }

            return (
              <div 
                key={e.id} 
                className="absolute w-[95%] left-[2.5%] z-10 transition-transform hover:z-50 hover:scale-[1.01]" 
                style={{ top: `${top}px`, height: `${height}px` }}
              >
                <div className="h-full w-full">
                    <div 
                      onClick={() => openRescheduleModal(e)}
                      className={`h-full p-3 rounded-lg border-l-4 text-sm cursor-pointer shadow-sm transition-transform hover:scale-[1.01] ${getColorClass(e.color)} ${!canReschedule || e.status === 'Completed' ? '' : 'hover:opacity-90'}`}
                    >
                      <div className="font-bold flex justify-between items-start">
                        <span>{e.title}</span>
                        {e.start_time && <span className="opacity-80 text-xs">{e.start_time.substring(0, 5)} {e.end_time ? `- ${e.end_time.substring(0, 5)}` : ''}</span>}
                      </div>
                      <div className="mt-1 font-medium opacity-90">{e.vehicle_name} • {e.technician_name || 'Unassigned'}</div>
                      <div className="mt-1 text-xs opacity-80">{e.description}</div>
                      <div className="mt-2 inline-flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded-full bg-white/20 text-xs font-bold tracking-wide uppercase">{e.priority}</span>
                        <span className="px-2 py-0.5 rounded-full bg-black/10 text-xs font-bold tracking-wide uppercase">{e.status}</span>
                      </div>
                    </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const getHeaderTitle = () => {
    if (currentView === 'month') {
      return currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });
    }
    if (currentView === 'week') {
      const start = getWeekStartDate(currentDate);
      const end = new Date(start);
      end.setDate(end.getDate() + 6);
      return `${start.toLocaleString('default', { month: 'short', day: 'numeric' })} - ${end.toLocaleString('default', { month: 'short', day: 'numeric', year: 'numeric' })}`;
    }
    return currentDate.toLocaleString('default', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
  };

  const SidebarCard = ({ event }) => (
    <div 
      className="p-3 bg-surface border border-outline-variant rounded-lg mb-2 hover:bg-surface-container-low transition-colors cursor-pointer"
      onClick={() => {
        setCurrentDate(new Date(event.scheduled_date));
        setCurrentView('day');
      }}
    >
      <div className="flex justify-between items-start mb-1">
        <h4 className="font-bold text-sm text-on-surface truncate pr-2">{event.title}</h4>
        <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${getColorClass(event.color).split(' ')[0]}`}></div>
      </div>
      <p className="text-xs text-on-surface-variant mb-2 truncate">{event.vehicle_name}</p>
      <div className="flex justify-between items-center text-[11px] font-medium text-on-surface-variant">
        <span>{event.scheduled_date}</span>
        <span className="uppercase tracking-wider opacity-80">{event.status}</span>
      </div>
    </div>
  );

  return (
    <div className="p-3 md:p-md lg:p-lg space-y-lg flex-1 min-w-0 flex flex-col">
      {/* Header Toolbar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate(-1)}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-variant text-on-surface transition-colors"
            title="Go Back"
          >
            <span className="material-symbols-outlined text-2xl">arrow_back</span>
          </button>
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Fleet Maintenance Scheduler</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Manage and assign vehicle maintenance jobs.</p>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-sm w-full md:w-auto">
          {/* Search */}
          <div className="relative flex-1">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm pointer-events-none">search</span>
            <input 
              type="text" 
              placeholder="Search tasks..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-4 py-2 bg-surface border border-outline-variant rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-full transition-all"
            />
          </div>

          {/* Filters */}
          <select 
            value={filters.status} 
            onChange={(e) => setFilters({...filters, status: e.target.value})}
            className="flex-1 sm:flex-none px-3 py-2 bg-surface border border-outline-variant rounded-lg text-sm text-on-surface-variant focus:outline-none focus:border-primary"
          >
            <option value="">All Statuses</option>
            <option value="Scheduled">Scheduled</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Overdue">Overdue</option>
            <option value="Cancelled">Cancelled</option>
          </select>

          <select 
            value={filters.priority} 
            onChange={(e) => setFilters({...filters, priority: e.target.value})}
            className="flex-1 sm:flex-none px-3 py-2 bg-surface border border-outline-variant rounded-lg text-sm text-on-surface-variant focus:outline-none focus:border-primary"
          >
            <option value="">All Priorities</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
            <option value="Critical">Critical</option>
          </select>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="flex-1 flex gap-lg">
        
        {/* Main Calendar Area */}
        <div className="flex-1 flex flex-col bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm min-w-0">
          
          {/* Calendar Controls */}
          <div className="p-4 border-b border-outline-variant flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 bg-surface flex-shrink-0">
            <div className="flex flex-wrap items-center gap-4 w-full xl:w-auto">
              <div className="flex items-center bg-surface-container-low rounded-lg p-1 border border-outline-variant shrink-0">
                <button onClick={prevDate} className="p-1 hover:bg-surface-container-high rounded text-on-surface-variant transition-colors"><span className="material-symbols-outlined text-[20px]">chevron_left</span></button>
                <button onClick={goToday} className="px-3 py-1 text-sm font-bold text-on-surface hover:bg-surface-container-high rounded transition-colors">Today</button>
                <button onClick={nextDate} className="p-1 hover:bg-surface-container-high rounded text-on-surface-variant transition-colors"><span className="material-symbols-outlined text-[20px]">chevron_right</span></button>
              </div>
              <h2 className="text-lg font-bold text-on-surface min-w-[200px] truncate">{getHeaderTitle()}</h2>
            </div>
            <div className="flex items-center bg-surface-container-low rounded-lg p-1 border border-outline-variant w-full xl:w-auto">
              <button onClick={() => setCurrentView('month')} className={`px-4 py-1.5 text-sm font-bold rounded transition-colors ${currentView === 'month' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}>Month</button>
              <button onClick={() => setCurrentView('week')} className={`px-4 py-1.5 text-sm font-bold rounded transition-colors ${currentView === 'week' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}>Week</button>
              <button onClick={() => setCurrentView('day')} className={`px-4 py-1.5 text-sm font-bold rounded transition-colors ${currentView === 'day' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'}`}>Day</button>
            </div>
          </div>

          {/* Calendar View */}
          <div className="flex-1 p-4 bg-surface-container-lowest relative">
            {(loading && !isSyncing) ? (
              <div className="absolute inset-0 bg-surface/50 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
              </div>
            ) : null}
            
            {events.length === 0 && !(loading && !isSyncing) && (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-on-surface-variant opacity-60">
                <span className="material-symbols-outlined text-[48px] mb-2">event_busy</span>
                <p className="font-medium">No maintenance scheduled for this period.</p>
              </div>
            )}

            {currentView === 'month' && renderMonthView()}
            {currentView === 'week' && renderWeekView()}
            {currentView === 'day' && renderDayView()}
          </div>
        </div>

        {/* Right Sidebar - Upcoming & Completed */}
        <div className="w-72 flex flex-col gap-4 flex-shrink-0 hidden xl:flex">
          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm flex flex-col max-h-[400px]">
            <div className="p-3 border-b border-outline-variant bg-surface flex justify-between items-center sticky top-0">
              <h3 className="font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">upcoming</span>
                Upcoming Jobs
              </h3>
              <span className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full font-bold">{upcomingJobs.length}</span>
            </div>
            <div className="p-3 overflow-y-auto custom-scrollbar flex-1">
              {upcomingJobs.length === 0 ? (
                <p className="text-center text-sm text-on-surface-variant p-4">No upcoming jobs.</p>
              ) : (
                upcomingJobs.map(job => <SidebarCard key={`up-${job.id}`} event={job} />)
              )}
            </div>
          </div>

          <div className="bg-surface-container-lowest rounded-xl border border-outline-variant shadow-sm flex flex-col max-h-[400px]">
            <div className="p-3 border-b border-outline-variant bg-surface flex justify-between items-center sticky top-0">
              <h3 className="font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-tertiary text-[20px]">task_alt</span>
                Completed Jobs
              </h3>
              <span className="bg-tertiary/10 text-tertiary text-xs px-2 py-0.5 rounded-full font-bold">{completedJobs.length}</span>
            </div>
            <div className="p-3 overflow-y-auto custom-scrollbar flex-1">
              {completedJobs.length === 0 ? (
                <p className="text-center text-sm text-on-surface-variant p-4">No completed jobs.</p>
              ) : (
                completedJobs.map(job => <SidebarCard key={`cp-${job.id}`} event={job} />)
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Reschedule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in">
          <div className="bg-surface rounded-xl shadow-xl overflow-hidden border border-outline-variant" style={{ width: '100%', maxWidth: '448px' }}>
            <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center">
              <h2 className="text-title-md font-bold text-on-surface">Reschedule Maintenance</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-on-surface-variant hover:text-on-surface transition-colors">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
            <div className="p-6">
              <div className="mb-6 bg-surface-container-low p-4 rounded-lg border border-outline-variant">
                <h3 className="font-bold text-sm text-on-surface">{selectedEvent?.title}</h3>
                <p className="text-sm text-on-surface-variant mt-1">{selectedEvent?.vehicle_name} • {selectedEvent?.technician_name || 'Unassigned'}</p>
                <div className="mt-2 inline-flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${getColorClass(selectedEvent?.color)}`}>{selectedEvent?.status}</span>
                </div>
              </div>

              <form id="rescheduleForm" onSubmit={handleRescheduleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-on-surface mb-1">Scheduled Date</label>
                  <input 
                    type="date" 
                    required
                    value={rescheduleData.scheduled_date}
                    onChange={e => setRescheduleData({...rescheduleData, scheduled_date: e.target.value})}
                    className="w-full px-3 py-2 bg-surface border border-outline-variant rounded-lg text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-on-surface mb-1">Start Time (Optional)</label>
                    <input 
                      type="time" 
                      value={rescheduleData.start_time}
                      onChange={e => setRescheduleData({...rescheduleData, start_time: e.target.value})}
                      className="w-full px-3 py-2 bg-surface border border-outline-variant rounded-lg text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-on-surface mb-1">End Time (Optional)</label>
                    <input 
                      type="time" 
                      value={rescheduleData.end_time}
                      onChange={e => setRescheduleData({...rescheduleData, end_time: e.target.value})}
                      className="w-full px-3 py-2 bg-surface border border-outline-variant rounded-lg text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                    />
                  </div>
                </div>
              </form>
            </div>
            <div className="px-6 py-4 border-t border-outline-variant bg-surface-container-lowest flex justify-end gap-3">
              <button 
                type="button" 
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-sm font-bold text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                form="rescheduleForm"
                className="px-4 py-2 text-sm font-bold bg-primary text-on-primary hover:bg-primary/90 rounded-lg shadow-sm transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
