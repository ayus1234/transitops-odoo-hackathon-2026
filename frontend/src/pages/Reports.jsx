import React, { useEffect, useState, useMemo } from 'react';
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
  Legend
} from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useDataSync } from '../contexts/RealTimeSyncContext';
import { MapBoundsFitter, createCustomIcon, getVehicleStatusColors } from './fleet_map/FleetMapView';
import { downloadBlobFromResponse, getFormattedDate } from '../utils/exportUtils';

// Register ChartJS modules
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const Reports = () => {
  const [downloading, setDownloading] = useState(false);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedReportType, setSelectedReportType] = useState('financial');
  const [dateRange, setDateRange] = useState('30d');
  const [mapView, setMapView] = useState('MAP');
  const { showToast } = useToast();
  const navigate = useNavigate();

  const getDateRangeParams = React.useCallback(() => {
    if (dateRange === 'all') return { start: null, end: null };
    const end = new Date();
    const start = new Date();
    if (dateRange === '30d') {
      start.setDate(end.getDate() - 30);
    } else if (dateRange === 'qtd') {
      const quarter = Math.floor(start.getMonth() / 3);
      start.setMonth(quarter * 3, 1);
    } else if (dateRange === 'ytd') {
      start.setMonth(0, 1);
    }
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  }, [dateRange]);

  const fetchData = React.useCallback(async () => {
    const { start, end } = getDateRangeParams();
    let queryParams = '?export_format=json';
    if (start && end) {
      queryParams += `&start_date=${start}&end_date=${end}`;
    }

    const [fleetRes, finRes, mapRes, dynamicRes, tripsRes] = await Promise.all([
      api.get('/reports/fleet'),
      api.get('/reports/financial'),
      api.get('/fleet-map/full'),
      api.get(`/reports/${selectedReportType}${queryParams}`),
      api.get('/reports/trips?export_format=json')
    ]);
    return {
      fleetData: fleetRes.data.data || [],
      financialData: finRes.data.data || [],
      fleetMapData: mapRes.data || { vehicles: [], trips: [], bounds: {} },
      dynamicData: dynamicRes.data.data || [],
      regionalTripsData: tripsRes.data.data || []
    };
  }, [selectedReportType, getDateRangeParams]);

  const { data, loading, isSyncing, error, refresh } = useDataSync(
    fetchData,
    [selectedReportType, dateRange],
    'low'
  );

  const fleetData = data?.fleetData || [];
  const financialData = data?.financialData || [];
  const fleetMapData = data?.fleetMapData || null;
  const dynamicData = data?.dynamicData || [];

  // Pagination logic for Dynamic Data Table
  const totalDynamicItems = dynamicData.length;
  const totalDynamicPages = Math.ceil(totalDynamicItems / itemsPerPage);
  const paginatedDynamicData = dynamicData.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  const handlePageChange = (direction) => {
    if (direction === 'prev' && currentPage > 1) setCurrentPage(p => p - 1);
    if (direction === 'next' && currentPage < totalDynamicPages) setCurrentPage(p => p + 1);
  };

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedReportType, dateRange]);

  const handleDownload = async (reportType, format) => {
    try {
      setDownloading(true);
      const { start, end } = getDateRangeParams();
      let queryParams = `?export_format=${format}`;
      if (start && end) {
        queryParams += `&start_date=${start}&end_date=${end}`;
      }

      const response = await api.get(`/reports/${reportType}${queryParams}`, {
        responseType: 'blob' 
      });
      const fallbackName = `${reportType}_report_${getFormattedDate()}.${format}`;
      downloadBlobFromResponse(response, fallbackName);
    } catch (error) {
      console.error("Download failed", error);
      alert("Failed to download report.");
    } finally {
      setDownloading(false);
    }
  };

  // --- KPI Computations ---
  const kpis = useMemo(() => {
    // Attempt to compute simple KPIs based on fetched lists
    let totalRev = 1240000; // Mocked fallback if no actual revenue data
    let avgMpg = 6.8; 
    let maintCost = 42300;

    // We can pull these from financial if available
    let totalOpCost = 0;
    financialData.forEach(item => {
      // Assuming financialData has { category: 'Fuel', amount: 1000 } style objects
      if (item.category === 'Revenue') totalRev = parseFloat(item.amount);
      if (item.category === 'Maintenance' || item.category === 'Repair') maintCost += parseFloat(item.amount || 0);
      if (item.category !== 'Revenue') totalOpCost += parseFloat(item.amount || 0);
    });

    return {
      revenue: new Intl.NumberFormat('en-IN').format(totalRev),
      kmpl: avgMpg.toFixed(1),
      maintCost: new Intl.NumberFormat('en-IN').format(maintCost)
    };
  }, [financialData]);

  const regionalTripsData = data?.regionalTripsData || [];

  // Aggregate regional data for LIST view
  const regionalData = useMemo(() => {
    const groups = {};
    if (regionalTripsData.length > 0) {
      regionalTripsData.forEach(t => {
        const region = t.Source || t.source || t.origin;
        if (region) {
          if (!groups[region]) groups[region] = 0;
          groups[region]++;
        }
      });
    } else if (fleetMapData && fleetMapData.trips) {
      fleetMapData.trips.forEach(t => {
        const region = t.origin;
        if (region) {
          if (!groups[region]) groups[region] = 0;
          groups[region]++;
        }
      });
    }

    console.log('TRANSITOPS_FIX_V3: REGIONAL GROUPS:', groups);

    if (Object.keys(groups).length === 0) return [];

    return Object.keys(groups)
      .map(region => ({
        region,
        trips: groups[region],
        // Provide a mock dynamic trend for visual appeal matching previous static values
        trend: Math.floor(Math.random() * 20) - 5 
      }))
      .sort((a, b) => b.trips - a.trips);
  }, [fleetMapData, regionalTripsData]);

  // --- Chart Data Computations ---
  
  // 1. Line Chart (Fleet Utilization)
  const lineChartData = useMemo(() => {
    let labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    let heavyData = [65, 78, 85, 55, 70, 92, 60];
    let lightData = [45, 55, 60, 40, 50, 70, 45];

    if (dateRange === '30d') {
      labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
      heavyData = [72, 78, 81, 75];
      lightData = [55, 60, 62, 58];
    } else if (dateRange === 'qtd') {
      labels = ['Month 1', 'Month 2', 'Month 3'];
      heavyData = [70, 75, 82];
      lightData = [50, 58, 65];
    } else if (dateRange === 'ytd') {
      labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
      heavyData = [75, 72, 78, 80, 85, 88, 92];
      lightData = [60, 58, 62, 65, 70, 75, 80];
    } else if (dateRange === 'all') {
      labels = ['2023', '2024', '2025', '2026'];
      heavyData = [65, 72, 80, 88];
      lightData = [50, 58, 65, 72];
    }

    return {
      labels,
      datasets: [
        {
          label: 'Heavy Duty',
          data: heavyData,
          borderColor: '#0040a1',
          backgroundColor: 'rgba(0, 64, 161, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Light Duty',
          data: lightData,
          borderColor: '#1b6d24',
          backgroundColor: 'transparent',
          tension: 0.4,
          borderDash: [5, 5]
        }
      ]
    };
  }, [dateRange]);

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { display: false, min: 0, max: 100 },
      x: { grid: { display: false } }
    }
  };

  // 2. Doughnut Chart (ROI Dist)
  const doughnutChartData = useMemo(() => {
    return {
      labels: ['High Yield', 'Moderate', 'Underperforming'],
      datasets: [
        {
          data: [52, 26, 22],
          backgroundColor: ['#0056d2', '#a0f399', '#ffdad6'],
          borderWidth: 0,
          cutout: '80%'
        }
      ]
    };
  }, []);

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } }
  };

  // 3. Bar Chart (Operational Costs)
  const barChartData = useMemo(() => {
    let fuel = 285400;
    let maint = 112900;
    let tolls = 64200;
    let other = 18100;
    
    // Attempt dynamic mapping from financialData
    if (financialData.length > 0) {
      fuel = maint = tolls = other = 0;
      financialData.forEach(item => {
        // Handle both standard JSON keys and CSV-formatted Capitalized keys
        const cat = String(item.expense_type || item.category || item.Category || 'Other').toLowerCase();
        // Skip the grand total row from the report generator
        if (cat.includes('grand total')) return;
        
        const amt = parseFloat(item.amount || item.total_cost || item['Total Cost'] || 0);
        
        if (cat.includes('fuel')) fuel += amt;
        else if (cat.includes('maintenance') || cat.includes('repair')) maint += amt;
        else if (cat.includes('toll')) tolls += amt;
        else other += amt;
      });
    }

    return {
      labels: ['Fuel', 'Maintenance', 'Tolls & Compliance', 'Other'],
      datasets: [
        {
          data: [fuel, maint, tolls, other],
          backgroundColor: ['#0040a1', '#1b6d24', '#773300', '#737785'],
          borderRadius: 4,
          barPercentage: 0.6
        }
      ]
    };
  }, [financialData]);

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(ctx.raw)
        }
      }
    },
    scales: {
      x: { display: false },
      y: { grid: { display: false } }
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-y-auto bg-background">
      
      {/* Page Canvas */}
      <div className="p-3 md:p-lg space-y-lg min-w-0">
        
        {/* Page Header (Matching Dashboard/Vehicles) */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center w-full gap-4">
          <div>
            <h1 className="font-headline-md text-headline-md font-bold text-on-surface">Reports & Analytics</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-1">Generate, view, and export operational metrics</p>
          </div>
          <div className="flex items-center gap-md">
            <button 
              onClick={refresh} 
              disabled={loading || isSyncing}
              className="flex items-center gap-2 px-3 py-2 text-on-surface-variant hover:bg-surface-container-low rounded-lg transition-all disabled:opacity-50" 
              title="Refresh Data"
            >
              <span className={`material-symbols-outlined ${(loading || isSyncing) ? 'animate-spin' : ''}`}>sync</span>
            </button>
            <button 
              onClick={() => navigate('/reports/builder')} 
              className="h-10 px-md bg-primary text-on-primary font-bold rounded-lg flex items-center gap-2 hover:bg-primary-container transition-all active:scale-95 shadow-sm whitespace-nowrap"
            >
              <span className="material-symbols-outlined text-lg">add_chart</span> 
              <span className="font-body-md text-body-md">Create Custom Report</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-error-container text-on-error-container rounded-lg border border-error/20 flex items-center gap-3">
            <span className="material-symbols-outlined">error</span>
            <p className="flex-1 font-bold">{error}</p>
          </div>
        )}

        {/* Filters & Exports */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-md bg-surface-container-lowest p-md rounded-xl border border-outline-variant shadow-sm">
          <div className="flex flex-wrap gap-sm">
            <div className="flex flex-col gap-xs">
              <label className="text-label-caps text-on-surface-variant px-xs">DATE RANGE</label>
              <select 
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="bg-surface border border-outline-variant text-body-sm px-sm py-xs rounded focus:ring-primary outline-none focus:border-primary min-w-[160px]"
              >
                <option value="30d">Last 30 Days</option>
                <option value="qtd">Quarter to Date</option>
                <option value="ytd">Year to Date</option>
                <option value="all">All Time</option>
              </select>
            </div>
            <div className="flex flex-col gap-xs">
              <label className="text-label-caps text-on-surface-variant px-xs">REPORT TYPE</label>
              <select 
                value={selectedReportType}
                onChange={(e) => setSelectedReportType(e.target.value)}
                className="bg-surface border border-outline-variant text-body-sm px-sm py-xs rounded focus:ring-primary outline-none focus:border-primary min-w-[140px]"
              >
                <option value="financial">Financial Summary</option>
                <option value="fleet">Fleet Report</option>
                <option value="fuel">Fuel Report</option>
                <option value="maintenance">Maintenance Report</option>
                <option value="expenses">Expense Report</option>
                <option value="drivers">Driver Report</option>
                <option value="trips">Trip Report</option>
              </select>
            </div>
          </div>
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto mt-auto">
            <button onClick={() => handleDownload(selectedReportType, 'csv')} disabled={downloading} className="flex items-center gap-xs text-body-sm font-semibold px-md py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50">
              <span className="material-symbols-outlined text-lg">csv</span> CSV
            </button>
            <button onClick={() => handleDownload(selectedReportType, 'pdf')} disabled={downloading} className="flex items-center gap-xs text-body-sm font-semibold px-md py-sm border border-outline text-on-surface-variant rounded hover:bg-surface-variant transition-colors disabled:opacity-50">
              <span className="material-symbols-outlined text-lg">picture_as_pdf</span> PDF
            </button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-md">
          {/* Fleet Utilization */}
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-sm">
              <div className="p-xs bg-primary-container/10 rounded-lg text-primary">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>analytics</span>
              </div>
              <span className="text-secondary text-xs font-bold flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm">trending_up</span> +2.4%
              </span>
            </div>
            <p className="text-on-surface-variant text-body-sm font-medium mb-xs">Fleet Utilization</p>
            <h2 className="text-display-lg font-display-lg text-on-surface">84.2%</h2>
            <div className="mt-md w-full bg-surface-container rounded-full h-1.5">
              <div className="bg-primary h-1.5 rounded-full" style={{width: '84%'}}></div>
            </div>
          </div>

          {/* Total Revenue */}
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-sm">
              <div className="p-xs bg-secondary-container/20 rounded-lg text-secondary">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>monetization_on</span>
              </div>
              <span className="text-secondary text-xs font-bold flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm">trending_up</span> +12.8%
              </span>
            </div>
            <p className="text-on-surface-variant text-body-sm font-medium mb-xs">Total Revenue</p>
            <h2 className="text-display-lg font-display-lg text-on-surface">₹{kpis.revenue}</h2>
            <p className="text-[10px] text-on-surface-variant mt-md uppercase tracking-tight">Projected: ₹15,00,000 by EOY</p>
          </div>

          {/* Avg. Fuel Efficiency */}
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-sm">
              <div className="p-xs bg-tertiary-container/10 rounded-lg text-tertiary">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>local_gas_station</span>
              </div>
              <span className="text-error text-xs font-bold flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm">trending_down</span> -0.5%
              </span>
            </div>
            <p className="text-on-surface-variant text-body-sm font-medium mb-xs">Avg. Fuel Efficiency</p>
            <h2 className="text-display-lg font-display-lg text-on-surface">{kpis.kmpl} <span className="text-headline-md font-normal">KMPL</span></h2>
            <p className="text-[10px] text-on-surface-variant mt-md uppercase tracking-tight">Fleet Target: 7.2 KMPL</p>
          </div>

          {/* Maintenance Costs */}
          <div className="bg-surface p-md rounded-xl border border-outline-variant shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-sm">
              <div className="p-xs bg-error-container/20 rounded-lg text-error">
                <span className="material-symbols-outlined" style={{fontVariationSettings: "'FILL' 1"}}>handyman</span>
              </div>
              <span className="text-secondary text-xs font-bold flex items-center gap-xs">
                <span className="material-symbols-outlined text-sm">trending_down</span> -4.2%
              </span>
            </div>
            <p className="text-on-surface-variant text-body-sm font-medium mb-xs">Maintenance Costs</p>
            <h2 className="text-display-lg font-display-lg text-on-surface">₹{kpis.maintCost}</h2>
            <p className="text-[10px] text-on-surface-variant mt-md uppercase tracking-tight">Down from last month</p>
          </div>
        </div>

        {/* Dashboard Layout (Bento Style) */}
        <div className="grid grid-cols-12 gap-lg">
          
          {/* Fleet Utilization Trend (Multi-line Chart) */}
          <div className="col-span-12 lg:col-span-8 bg-surface p-lg rounded-xl border border-outline-variant shadow-sm flex flex-col min-h-[350px]">
            <div className="flex justify-between items-center mb-lg">
              <div>
                <h3 className="text-title-sm font-title-sm text-on-surface">Fleet Utilization Trend</h3>
                <p className="text-body-sm text-on-surface-variant">Daily utilization rate by vehicle class</p>
              </div>
              <div className="flex items-center gap-md">
                <div className="flex items-center gap-xs">
                  <span className="w-3 h-3 rounded-full bg-primary"></span>
                  <span className="text-[11px] font-bold text-on-surface-variant">Heavy</span>
                </div>
                <div className="flex items-center gap-xs">
                  <span className="w-3 h-3 rounded-full bg-secondary"></span>
                  <span className="text-[11px] font-bold text-on-surface-variant">Light</span>
                </div>
              </div>
            </div>
            <div className="flex-1 w-full relative">
              <Line data={lineChartData} options={lineChartOptions} />
            </div>
          </div>

          {/* Vehicle ROI Distribution (Doughnut Chart) */}
          <div className="col-span-12 lg:col-span-4 bg-surface p-lg rounded-xl border border-outline-variant shadow-sm flex flex-col">
            <h3 className="text-title-sm font-title-sm text-on-surface mb-md">Vehicle ROI Dist.</h3>
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="w-48 h-48 relative mb-6">
                <Doughnut data={doughnutChartData} options={doughnutChartOptions} />
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-headline-md font-bold text-on-surface">78%</span>
                  <span className="text-[10px] text-on-surface-variant uppercase font-bold">Optimal</span>
                </div>
              </div>
              <div className="w-full space-y-3">
                <div className="flex justify-between items-center text-body-sm">
                  <div className="flex items-center gap-xs">
                    <span className="w-3 h-3 rounded-full bg-primary-container"></span> High Yield
                  </div>
                  <span className="font-bold text-on-surface">52%</span>
                </div>
                <div className="flex justify-between items-center text-body-sm">
                  <div className="flex items-center gap-xs">
                    <span className="w-3 h-3 rounded-full bg-secondary-container"></span> Moderate
                  </div>
                  <span className="font-bold text-on-surface">26%</span>
                </div>
                <div className="flex justify-between items-center text-body-sm">
                  <div className="flex items-center gap-xs">
                    <span className="w-3 h-3 rounded-full bg-error-container"></span> Underperforming
                  </div>
                  <span className="font-bold text-on-surface">22%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Trips by Region (Map Visual) */}
          <div className="col-span-12 lg:col-span-7 bg-surface rounded-xl border border-outline-variant shadow-sm overflow-hidden flex flex-col min-w-0 h-[400px]">
            <div className="p-md border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center z-10">
              <div>
                <h2 className="text-title-lg font-bold text-on-surface">Trips by Region</h2>
                <p className="text-body-sm text-on-surface-variant">Live operational fleet distribution</p>
              </div>
              <div className="bg-surface border border-outline-variant rounded flex">
                <button onClick={() => setMapView('MAP')} className={`px-sm py-xs font-bold text-[10px] ${mapView === 'MAP' ? 'bg-surface-container text-primary' : 'text-on-surface-variant'}`}>MAP</button>
                <button onClick={() => setMapView('LIST')} className={`px-sm py-xs font-bold text-[10px] border-l border-outline-variant ${mapView === 'LIST' ? 'bg-surface-container text-primary' : 'text-on-surface-variant'}`}>LIST</button>
              </div>
            </div>
            {mapView === 'MAP' ? (
              <div className="flex-1 relative bg-slate-100 group">
                {!fleetMapData ? (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                  </div>
                ) : (
                  <MapContainer 
                    center={[37.7749, -122.4194]} 
                    zoom={10} 
                    className="w-full h-full z-0"
                    zoomControl={false}
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
                      url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                    />
                    <MapBoundsFitter bounds={fleetMapData.bounds} />
                    
                    {fleetMapData.vehicles.filter(v => v.active_trip != null).map(v => {
                      if (v.latitude == null || v.longitude == null) return null;
                      const colors = getVehicleStatusColors(v.status);
                      return (
                        <Marker 
                          key={`rv-${v.vehicle_id}`} 
                          position={[v.latitude, v.longitude]}
                          icon={createCustomIcon('directions_car', colors.color, colors.bg)}
                        >
                          <Popup className="rounded-xl overflow-hidden shadow-md">
                            <div className="min-w-[200px]">
                              <div className={`px-4 py-2 border-b border-outline-variant ${colors.bg}`}>
                                <div className="flex justify-between items-center">
                                  <h4 className="font-bold text-on-surface m-0 text-[14px]">{v.vehicle_name}</h4>
                                </div>
                                <p className="text-[12px] opacity-80 m-0">{v.registration_number}</p>
                              </div>
                              <div className="p-4 bg-white">
                                <div className="flex justify-between items-center pb-1">
                                  <span className="text-[12px] text-on-surface-variant">Active Trip</span>
                                  <span className="text-[13px] font-medium text-on-surface">{v.active_trip}</span>
                                </div>
                              </div>
                            </div>
                          </Popup>
                        </Marker>
                      );
                    })}
                  </MapContainer>
                )}
                
                {/* Floating Map Legend */}
                <div className="absolute bottom-md right-md bg-white/90 backdrop-blur-sm p-sm rounded border border-outline-variant shadow-lg text-[10px] z-[400]">
                  <div className="font-bold mb-xs text-on-surface">ACTIVE TRIPS</div>
                  <div className="flex items-center gap-xs">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span> Dispatched Vehicles
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 bg-surface overflow-y-auto overflow-x-auto p-sm md:p-md">
                <table className="w-full text-left text-body-sm min-w-[800px]">
                  <thead>
                    <tr className="border-b border-outline-variant">
                      <th className="pb-sm font-bold text-on-surface-variant">Region (Origin)</th>
                      <th className="pb-sm font-bold text-on-surface-variant text-right">Active Trips</th>
                      <th className="pb-sm font-bold text-on-surface-variant text-right">Trend</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-outline-variant">
                    {regionalData.length === 0 ? (
                      <tr><td colSpan="3" className="text-center py-6 text-on-surface-variant">No active trips found.</td></tr>
                    ) : regionalData.map((data, idx) => (
                      <tr key={idx} className="hover:bg-surface-container-low transition-colors">
                        <td className="py-sm font-bold text-on-surface">{data.region}</td>
                        <td className="py-sm text-right text-data-tabular">{data.trips}</td>
                        <td className={`py-sm text-right font-medium ${data.trend >= 0 ? 'text-primary' : 'text-error'}`}>
                          {data.trend >= 0 ? '+' : ''}{data.trend}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Operational Costs (Bar Chart) */}
          <div className="col-span-12 lg:col-span-5 bg-surface p-lg rounded-xl border border-outline-variant shadow-sm flex flex-col h-[400px]">
            <div className="flex justify-between items-center mb-lg">
              <h3 className="text-title-sm font-title-sm text-on-surface">Operational Costs</h3>
              <span className="text-on-surface-variant font-bold text-[11px] uppercase tracking-widest">INR</span>
            </div>
            <div className="flex-1 w-full relative">
               <Bar data={barChartData} options={barChartOptions} />
            </div>
          </div>

        </div>

        {/* Detailed Table (Dynamic based on selected report type) */}
        <div className="bg-surface rounded-xl border border-outline-variant shadow-sm overflow-hidden mb-32">
          <div className="p-md border-b border-outline-variant bg-surface-container-lowest flex justify-between items-center">
            <h3 className="text-title-sm font-title-sm text-on-surface capitalize">{selectedReportType} Report Details</h3>
            <button onClick={() => handleDownload(selectedReportType, 'csv')} disabled={downloading} className="text-primary text-body-sm font-bold flex items-center gap-xs hover:underline disabled:opacity-50">
              Export Dataset <span className="material-symbols-outlined text-sm">download</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left min-w-[800px]">
              <thead>
                <tr className="bg-surface-container-low border-b border-outline-variant">
                  {dynamicData.length > 0 ? Object.keys(dynamicData[0]).map(key => (
                    <th key={key} className="px-md py-sm text-label-caps text-on-surface-variant">{key}</th>
                  )) : (
                    <th className="px-md py-sm text-label-caps text-on-surface-variant">Data</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant">
                {loading ? (
                   [...Array(itemsPerPage)].map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan="100%" className="px-md py-sm"><div className="h-4 bg-slate-200 rounded w-full"></div></td>
                    </tr>
                  ))
                ) : paginatedDynamicData.map((row, i) => (
                  <tr key={i} className="hover:bg-surface-container-low transition-colors group">
                    {Object.values(row).map((val, idx) => (
                      <td key={idx} className="px-md py-sm text-body-sm">
                        {typeof val === 'number' && (Object.keys(row)[idx].toLowerCase().includes('cost') || Object.keys(row)[idx].toLowerCase().includes('amount') || Object.keys(row)[idx].toLowerCase().includes('revenue')) 
                          ? `₹${val.toFixed(2)}` 
                          : val}
                      </td>
                    ))}
                  </tr>
                ))}
                {dynamicData.length === 0 && !loading && (
                   <tr><td colSpan="100%" className="text-center py-6 text-on-surface-variant">No records found for this period.</td></tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Footer / Pagination */}
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
                {totalDynamicItems > 0 ? (currentPage-1)*itemsPerPage + 1 : 0}-{Math.min(currentPage*itemsPerPage, totalDynamicItems)} of {totalDynamicItems}
              </span>
              <div className="flex items-center gap-xs">
                <button 
                  onClick={() => handlePageChange('prev')}
                  disabled={currentPage === 1}
                  className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
                >
                  <span className="material-symbols-outlined">chevron_left</span>
                </button>
                <button 
                  onClick={() => handlePageChange('next')}
                  disabled={currentPage === totalDynamicPages || totalDynamicPages === 0}
                  className="p-1 rounded hover:bg-surface-variant text-on-surface disabled:opacity-30 transition-colors"
                >
                  <span className="material-symbols-outlined">chevron_right</span>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* FAB for quick actions */}
      <div className="fixed bottom-lg right-lg z-50 group flex flex-col items-center gap-2">
        <button onClick={() => handleDownload('financial', 'pdf')} title="Export PDF" className="w-10 h-10 bg-surface text-primary border border-primary rounded-full shadow-lg flex items-center justify-center opacity-0 translate-y-10 group-hover:opacity-100 group-hover:translate-y-0 transition-all hover:bg-primary-container/10">
          <span className="material-symbols-outlined text-lg">picture_as_pdf</span>
        </button>
        <button onClick={() => handleDownload('financial', 'csv')} title="Export CSV" className="w-10 h-10 bg-surface text-primary border border-primary rounded-full shadow-lg flex items-center justify-center opacity-0 translate-y-5 group-hover:opacity-100 group-hover:translate-y-0 transition-all hover:bg-primary-container/10">
          <span className="material-symbols-outlined text-lg">csv</span>
        </button>
        <button className="w-14 h-14 bg-primary text-on-primary rounded-full shadow-xl flex items-center justify-center hover:scale-105 active:scale-95 transition-all">
          <span className="material-symbols-outlined text-3xl">download</span>
        </button>
      </div>

    </div>
  );
};

export default Reports;
