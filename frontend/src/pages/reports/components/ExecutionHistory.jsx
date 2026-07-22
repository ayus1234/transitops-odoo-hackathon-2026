import React, { useEffect, useState } from 'react';
import api from '../../../services/api';

const ExecutionHistory = ({ reportId }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!reportId) {
      setHistory([]);
      return;
    }
    const fetchHistory = async () => {
      try {
        setLoading(true);
        // Assuming backend supports filtering history by report_id
        const res = await api.get(`/custom-reports/executions?report_id=${reportId}&limit=10`);
        setHistory(res.data.items || []);
      } catch (error) {
        console.error("Failed to fetch execution history", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [reportId]);

  if (!reportId) return null;

  return (
    <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm mt-md">
      <h3 className="text-title-sm font-title-sm text-on-surface mb-sm flex items-center gap-2">
        <span className="material-symbols-outlined text-sm text-primary">history</span>
        Recent Executions
      </h3>
      
      {loading ? (
        <p className="text-body-sm text-on-surface-variant">Loading history...</p>
      ) : history.length === 0 ? (
        <p className="text-body-sm text-on-surface-variant">No executions found for this report.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[11px] min-w-[800px]">
            <thead>
              <tr className="border-b border-outline-variant text-on-surface-variant">
                <th className="py-1">Date</th>
                <th className="py-1">Status</th>
                <th className="py-1 text-right">Rows</th>
                <th className="py-1 text-right">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {history.map((exec, idx) => (
                <tr key={idx} className="hover:bg-surface-container-lowest">
                  <td className="py-1.5 text-on-surface">{new Date(exec.executed_at).toLocaleString()}</td>
                  <td className="py-1.5">
                    <span className={`px-1.5 py-0.5 rounded-sm font-bold uppercase ${exec.status === 'success' ? 'bg-secondary/10 text-secondary' : 'bg-error/10 text-error'}`}>
                      {exec.status}
                    </span>
                  </td>
                  <td className="py-1.5 text-right font-bold text-on-surface">{exec.row_count}</td>
                  <td className="py-1.5 text-right text-on-surface-variant">{exec.execution_time_ms}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ExecutionHistory;
