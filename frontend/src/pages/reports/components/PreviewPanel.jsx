import React from 'react';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const PreviewPanel = ({ loading, data, columns, chartType, error }) => {
  if (error) {
    return (
      <div className="bg-error-container text-on-error-container p-md rounded-xl border border-error/20 flex flex-col items-center justify-center min-h-[300px]">
        <span className="material-symbols-outlined text-4xl mb-sm">error</span>
        <p className="font-bold">{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm min-h-[300px] flex flex-col justify-center items-center">
        <span className="material-symbols-outlined animate-spin text-primary text-4xl mb-sm">sync</span>
        <p className="text-on-surface-variant font-bold">Executing Report...</p>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm min-h-[300px] flex flex-col justify-center items-center">
        <span className="material-symbols-outlined text-on-surface-variant text-4xl mb-sm opacity-50">analytics</span>
        <p className="text-on-surface-variant font-bold">No data to preview</p>
        <p className="text-body-sm text-on-surface-variant">Click Generate to execute the report.</p>
      </div>
    );
  }

  // Render Chart or Table
  const renderContent = () => {
    if (chartType === 'table' || !chartType) {
      return (
        <div className="overflow-x-auto h-[400px]">
          <table className="w-full text-left min-w-[600px]">
            <thead className="sticky top-0 bg-surface z-10 shadow-sm">
              <tr className="bg-surface-container-low border-b border-outline-variant">
                {columns.map((col, idx) => (
                  <th key={idx} className="px-md py-sm text-label-caps text-on-surface-variant whitespace-nowrap">
                    {col.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant">
              {data.map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-surface-container-low transition-colors">
                  {columns.map((col, colIdx) => (
                    <td key={colIdx} className="px-md py-sm text-body-sm text-on-surface">
                      {row[col] !== null ? String(row[col]) : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // Prepare rudimentary chart data for preview
    // Note: In a real enterprise app, we'd have robust metric/dimension selection for charts.
    // Here we'll try to use the first column as labels and second column as data if possible.
    const labelCol = columns[0];
    const dataCol = columns.length > 1 ? columns[1] : columns[0];
    
    const chartLabels = data.map(d => d[labelCol] || 'Unknown');
    const chartDataValues = data.map(d => {
      const val = parseFloat(d[dataCol]);
      return isNaN(val) ? 1 : val; // Fallback to 1 if not numeric (e.g., counting)
    });

    const chartData = {
      labels: chartLabels,
      datasets: [
        {
          label: dataCol,
          data: chartDataValues,
          backgroundColor: [
            '#0056d2', '#1b6d24', '#773300', '#9c27b0', '#e91e63', '#00bcd4', '#ff9800'
          ],
          borderColor: chartType === 'line' ? '#0056d2' : undefined,
          tension: 0.3,
          fill: chartType === 'area',
        }
      ]
    };

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
    };

    return (
      <div className="h-[400px] w-full p-md">
        {chartType === 'bar' && <Bar data={chartData} options={chartOptions} />}
        {chartType === 'line' && <Line data={chartData} options={chartOptions} />}
        {chartType === 'pie' && <Pie data={chartData} options={chartOptions} />}
        {chartType === 'doughnut' && <Doughnut data={chartData} options={chartOptions} />}
        {chartType === 'area' && <Line data={chartData} options={chartOptions} />}
      </div>
    );
  };

  return (
    <div className="bg-surface rounded-xl border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0 h-full">
      <div className="p-md border-b border-outline-variant flex justify-between items-center bg-surface-container-lowest">
        <h3 className="text-title-sm font-title-sm text-on-surface flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">visibility</span> 
          Preview
        </h3>
        <span className="text-[11px] font-bold text-on-surface-variant bg-surface-container px-2 py-1 rounded">
          {data.length} Records
        </span>
      </div>
      <div className="flex-1 bg-surface">
        {renderContent()}
      </div>
    </div>
  );
};

export default PreviewPanel;
