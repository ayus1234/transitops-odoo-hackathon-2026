import React, { useState, useEffect, useCallback } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { useDataSync } from '../../contexts/RealTimeSyncContext';
import { useNavigate } from 'react-router-dom';

// Components
import ActivityStatistics from './ActivityStatistics';
import ActivityFilters from './ActivityFilters';
import ActivityTimeline from './ActivityTimeline';
import PaginationControls from './PaginationControls';
import ActivityDetailsModal from './ActivityDetailsModal';

const ActivityLog = () => {
  const { addToast } = useToast();
  const navigate = useNavigate();
  
  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  
  // Filter State
  const [filters, setFilters] = useState({
    module: '',
    severity: '',
    activity_type: '',
    status: '',
    search: '',
    start_date: '',
    end_date: '',
    user_id: '',
    vehicle_id: '',
    driver_id: ''
  });
  
  // Modal State
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch Everything
  const fetchAllData = useCallback(async () => {
    const skip = (currentPage - 1) * itemsPerPage;
    
    const queryParamsAct = new URLSearchParams({
      skip: skip.toString(),
      limit: itemsPerPage.toString(),
    });
    
    const queryParamsStat = new URLSearchParams();
    
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        if (['user_id', 'vehicle_id', 'driver_id'].includes(key) && !uuidRegex.test(value)) {
          // Skip appending invalid UUIDs to prevent 422 errors from the backend
          return;
        }
        queryParamsAct.append(key, value);
        queryParamsStat.append(key, value);
      }
    });
    
    const [actRes, statRes] = await Promise.all([
      api.get(`/activity?${queryParamsAct.toString()}`),
      api.get(`/activity/statistics?${queryParamsStat.toString()}`)
    ]);
    
    return {
      activities: actRes.data.items || [],
      totalItems: actRes.data.total || 0,
      statistics: statRes.data
    };
  }, [currentPage, itemsPerPage, filters]);

  const { data, loading, isSyncing, error, refresh } = useDataSync(
    fetchAllData,
    [currentPage, itemsPerPage, filters],
    'high'
  );

  const activities = data?.activities || [];
  const statistics = data?.statistics || null;
  const totalItems = data?.totalItems || 0;

  // Handlers
  const handleRefresh = () => {
    refresh();
  };

  const handleActivityClick = (activity) => {
    setSelectedActivity(activity);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedActivity(null), 200); // Wait for transition
  };

  // Reset pagination to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters, itemsPerPage]);

  return (
    <div className="p-3 md:p-gutter flex flex-col gap-gutter flex-1 min-w-0 bg-surface-container-lowest h-full overflow-y-auto">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full px-md mt-4 gap-4">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => navigate(-1)}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface-variant text-on-surface transition-colors"
            title="Go Back"
          >
            <span className="material-symbols-outlined text-2xl">arrow_back</span>
          </button>
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Enterprise Activity Log</h1>
            <p className="text-body-sm text-outline mt-1">Centralized audit trail for all system and user actions.</p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <ActivityStatistics stats={statistics} />

      {/* Search, Filters & Export */}
      <ActivityFilters 
        filters={filters} 
        setFilters={setFilters} 
        onRefresh={handleRefresh} 
        loading={loading} 
      />

      {/* Activity Timeline List */}
      <ActivityTimeline 
        activities={activities} 
        loading={loading && !isSyncing} 
        onActivityClick={handleActivityClick}
      />

      {/* Bottom Pagination */}
      <div className="mx-1 md:mx-md mb-md">
        <PaginationControls 
          currentPage={currentPage}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={setCurrentPage}
          onPageSizeChange={setItemsPerPage}
        />
      </div>

      {/* Details Modal */}
      <ActivityDetailsModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        activity={selectedActivity}
      />
    </div>
  );
};

export default ActivityLog;
