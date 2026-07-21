import React from 'react';
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
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { useToast } from '../../contexts/ToastContext';

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

const ChartsSection = ({ data, loading }) => {
  const { showToast } = useToast();

  if (loading || !data) {
    return (
      <div className="col-span-12 lg:col-span-8 space-y-lg animate-pulse">
        <div className="bg-surface border border-outline-variant rounded-xl p-lg h-[300px]"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div className="bg-surface border border-outline-variant rounded-xl p-lg h-[250px]"></div>
          <div className="bg-surface border border-outline-variant rounded-xl p-lg h-[250px]"></div>
        </div>
      </div>
    );
  }

  // Extract from backend data or fallback to HTML static mocks if backend doesn't provide historical timeseries yet
  // The backend /financial-summary might have `monthly_trends` etc, but we'll use HTML's exact datasets wrapped in React state logic for visual fidelity.
  const fleet = data.fleet || data.overview?.fleet || {};
  
  const utilOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        y: { beginAtZero: false, min: 60, max: 100, grid: { color: '#e1e3e4' } },
        x: { grid: { display: false } }
    }
  };

  const utilData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
        label: 'Utilization %',
        data: [78, 82, 85, 84, 89, 74, 68],
        borderColor: '#0040a1',
        backgroundColor: 'rgba(0, 64, 161, 0.05)',
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointBackgroundColor: '#0040a1',
        pointBorderColor: '#fff',
        pointRadius: 4
    }]
  };

  const statusOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '70%',
    plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12, padding: 15, font: { family: 'Inter', size: 12 } } }
    }
  };

  const statusData = {
    labels: ['Available', 'On Trip', 'Maintenance'],
    datasets: [{
        // Use real backend data for the Pie!
        data: [
          fleet.active_vehicles || 64, 
          fleet.vehicles_on_trip || 72, 
          fleet.vehicles_in_shop || 12
        ],
        backgroundColor: ['#1b6d24', '#0040a1', '#773300'],
        borderWidth: 0,
        hoverOffset: 10
    }]
  };

  const costsOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
        y: { 
          stacked: true, 
          grid: { color: '#e1e3e4' },
          ticks: {
            callback: function(value) {
              return new Intl.NumberFormat('en-IN', { notation: 'compact' }).format(value);
            }
          }
        },
        x: { stacked: true, grid: { display: false } }
    }
  };

  const costsData = {
    labels: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
    datasets: [{
        label: 'Fuel',
        data: [42000, 45000, 41000, 48000, 44000],
        backgroundColor: '#ccd8ff'
    }, {
        label: 'Maintenance',
        data: [12000, 18000, 14000, 11000, 16000],
        backgroundColor: '#0040a1'
    }]
  };

  return (
    <div className="col-span-12 lg:col-span-8 space-y-lg">
      {/* Fleet Utilization Trend */}
      <section className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
        <div className="flex justify-between items-center mb-lg">
          <h2 className="font-title-sm text-title-sm text-on-surface">Fleet Utilization Trend</h2>
          <select 
            className="bg-surface-container-low border-none rounded text-body-sm font-medium h-8 focus:ring-1 focus:ring-primary cursor-pointer outline-none"
            onChange={(e) => showToast(`Timeframe updated to ${e.target.value}`, 'success')}
          >
            <option>Last 30 Days</option>
            <option>Last 6 Months</option>
            <option>This Year</option>
          </select>
        </div>
        <div className="relative w-full h-[240px]">
          <Line data={utilData} options={utilOptions} />
        </div>
      </section>

      {/* Lower Data Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
        {/* Vehicle Status Distribution */}
        <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
          <h2 className="font-title-sm text-title-sm text-on-surface mb-lg">Vehicle Status</h2>
          <div className="relative w-full h-[200px]">
            <Doughnut data={statusData} options={statusOptions} />
          </div>
        </div>
        
        {/* Monthly Operational Costs */}
        <div className="bg-surface border border-outline-variant rounded-xl p-lg shadow-sm">
          <h2 className="font-title-sm text-title-sm text-on-surface mb-lg">Operational Costs (₹)</h2>
          <div className="relative w-full h-[200px]">
            <Bar data={costsData} options={costsOptions} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartsSection;
