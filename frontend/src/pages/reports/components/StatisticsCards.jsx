import React, { useEffect, useState } from 'react';
import api from '../../../services/api';

const StatisticsCards = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/custom-reports/statistics');
        setStats(res.data);
      } catch (error) {
        console.error("Failed to fetch statistics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-4 gap-md mb-lg">
        {[1,2,3,4].map(i => (
          <div key={i} className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm h-24 animate-pulse">
            <div className="h-4 bg-surface-container-high rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-surface-container-high rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 md:grid-cols-4 gap-md mb-lg">
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
        <p className="text-on-surface-variant text-label-caps mb-xs">Total Reports</p>
        <h2 className="text-display-sm font-display-sm text-on-surface flex items-center gap-2">
          {stats.total_reports}
          <span className="material-symbols-outlined text-primary opacity-50">description</span>
        </h2>
      </div>
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
        <p className="text-on-surface-variant text-label-caps mb-xs">Public Reports</p>
        <h2 className="text-display-sm font-display-sm text-on-surface flex items-center gap-2">
          {stats.public_reports}
          <span className="material-symbols-outlined text-secondary opacity-50">public</span>
        </h2>
      </div>
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
        <p className="text-on-surface-variant text-label-caps mb-xs">My Reports</p>
        <h2 className="text-display-sm font-display-sm text-on-surface flex items-center gap-2">
          {stats.my_reports}
          <span className="material-symbols-outlined text-tertiary opacity-50">person</span>
        </h2>
      </div>
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
        <p className="text-on-surface-variant text-label-caps mb-xs">Total Executions</p>
        <h2 className="text-display-sm font-display-sm text-on-surface flex items-center gap-2">
          {stats.total_executions}
          <span className="material-symbols-outlined text-error opacity-50">play_circle</span>
        </h2>
      </div>
    </div>
  );
};

export default StatisticsCards;
