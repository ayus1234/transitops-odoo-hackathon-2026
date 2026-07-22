import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import { renderToString } from 'react-dom/server';
import { useDataSync } from '../../contexts/RealTimeSyncContext';

// Fix leafet default icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Component to handle bounds changes
export const MapBoundsFitter = ({ bounds, isWidget }) => {
  const map = useMap();
  
  useEffect(() => {
    const container = map.getContainer();
    if (!container) return;
    
    // Robust fix for un-rendered tiles on mount or resize
    const observer = new ResizeObserver(() => {
      map.invalidateSize();
    });
    
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);

  useEffect(() => {
    if (bounds && bounds.min_lat != null) {
      const corner1 = L.latLng(bounds.min_lat, bounds.min_lng);
      const corner2 = L.latLng(bounds.max_lat, bounds.max_lng);
      const mapBounds = L.latLngBounds(corner1, corner2);
      
      const pad = isWidget ? 20 : 50;
      map.fitBounds(mapBounds, { 
        padding: [pad, pad],
        maxZoom: 15 
      });
    }
  }, [bounds, map, isWidget]);
  
  return null;
};

// Custom Marker Generators
export const createCustomIcon = (status, isDriver = false, hasAlert = false) => {
  const colors = isDriver ? getDriverStatusColors(status) : getVehicleStatusColors(status);
  const iconName = isDriver ? 'person' : 'local_shipping';
  
  const alertRing = hasAlert ? '<div class="absolute -inset-1 rounded-full border-2 border-red-500 animate-pulse"></div>' : '';

  const html = `
    <div class="relative w-8 h-8 flex items-center justify-center rounded-full shadow-md bg-white border-2 border-white">
      ${alertRing}
      <div class="w-full h-full rounded-full flex items-center justify-center ${colors.bg} ${colors.color}">
        <span class="material-symbols-outlined text-[16px]">${iconName}</span>
      </div>
      <div class="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rotate-45 bg-white border-b-2 border-r-2 border-white"></div>
    </div>
  `;
  
  return L.divIcon({
    html: html,
    className: 'custom-leaflet-icon',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

export const getVehicleStatusColors = (status) => {
  switch (status?.toLowerCase()) {
    case 'active':
    case 'on trip': return { color: 'text-green-700', bg: 'bg-green-100' };
    case 'idle':
    case 'available': return { color: 'text-blue-700', bg: 'bg-blue-100' };
    case 'maintenance':
    case 'in shop': return { color: 'text-orange-700', bg: 'bg-orange-100' };
    case 'offline':
    case 'retired': return { color: 'text-gray-700', bg: 'bg-gray-200' };
    case 'critical': return { color: 'text-red-700', bg: 'bg-red-100' };
    default: return { color: 'text-gray-700', bg: 'bg-gray-200' };
  }
};

export const getDriverStatusColors = (status) => {
  switch (status?.toLowerCase()) {
    case 'available': return { color: 'text-green-700', bg: 'bg-green-100' };
    case 'on trip': return { color: 'text-blue-700', bg: 'bg-blue-100' };
    case 'off duty': return { color: 'text-gray-700', bg: 'bg-gray-200' };
    default: return { color: 'text-gray-700', bg: 'bg-gray-200' };
  }
};

const FleetMapView = ({ isModal = false, isWidget = false, onExpand, onClose }) => {
  const { addToast } = useToast();
  
  const prevBoundsRef = useRef(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  
  const [vehicleFilter, setVehicleFilter] = useState('');
  const [driverFilter, setDriverFilter] = useState('');
  const [tripFilter, setTripFilter] = useState('');
  
  const [showVehicles, setShowVehicles] = useState(true);
  const [showDrivers, setShowDrivers] = useState(true);

  // Debounce search
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 500);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  const fetchFleetData = useCallback(async (isBackground = false) => {
    let endpoint = '/fleet-map/full';
    let params = new URLSearchParams();
    
    if (debouncedQuery) {
      endpoint = '/fleet-map/search';
      params.append('q', debouncedQuery);
    } else if (vehicleFilter || driverFilter || tripFilter) {
      endpoint = '/fleet-map/filter';
      if (vehicleFilter) params.append('vehicle_status', vehicleFilter);
      if (driverFilter) params.append('driver_status', driverFilter);
      if (tripFilter) params.append('trip_status', tripFilter);
    }
    
    const queryString = params.toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    
    const response = await api.get(url);
    
    const newBounds = isBackground && prevBoundsRef.current 
      ? prevBoundsRef.current 
      : response.data.bounds;
      
    prevBoundsRef.current = newBounds;

    return {
      ...response.data,
      bounds: newBounds
    };
  }, [debouncedQuery, vehicleFilter, driverFilter, tripFilter]);

  const { data, loading, isSyncing, error, refresh } = useDataSync(
    fetchFleetData,
    [debouncedQuery, vehicleFilter, driverFilter, tripFilter],
    'high'
  );

  const fleetData = data || { vehicles: [], drivers: [], trips: [], bounds: {} };

  const activeVehiclesCount = fleetData.vehicles.filter(v => ['active', 'on trip'].includes(v.status?.toLowerCase())).length;
  const totalVehiclesCount = fleetData.vehicles.length || 1;
  const onRoutePercent = Math.round((activeVehiclesCount / totalVehiclesCount) * 100);
  const avgEta = "4.8 hrs";
  
  const stats = {
    activeVehicles: activeVehiclesCount,
    onRoutePercent: onRoutePercent,
    avgEta: avgEta,
    lowAlerts: fleetData.vehicles.filter(v => v.has_critical_alert).length,
  };

  const handleFitBounds = async () => {
    refresh();
  };

  const mapLoading = loading && !isSyncing;

  const containerClasses = isWidget
    ? "bg-surface rounded-xl overflow-hidden shadow-sm h-full relative group cursor-pointer border border-outline-variant flex flex-col min-w-0"
    : isModal 
      ? "bg-surface rounded-2xl shadow-lg w-[95vw] max-w-7xl h-[85vh] md:h-[90vh] flex flex-col overflow-hidden animate-fade-in relative z-50 shrink-0"
      : "bg-surface rounded-xl border border-outline-variant flex flex-col h-[calc(100dvh-140px)] overflow-hidden shadow-sm min-w-0";

  return (
    <div className={containerClasses}>
      {/* Header */}
      {!isWidget && (
        <div className="flex flex-col md:flex-row justify-between items-center px-lg py-md border-b border-outline-variant bg-surface-container-lowest gap-md">
        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
          <span className="material-symbols-outlined text-primary bg-primary-container p-2 rounded-lg">map</span>
          <div>
            <h1 className="font-title-lg text-on-surface">Live Fleet Map</h1>
            <p className="text-body-sm text-on-surface-variant">Real-time tracking and intelligence</p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row flex-wrap md:flex-nowrap items-stretch md:items-center gap-sm w-full md:w-auto">
          {/* Search */}
          <div className="relative w-full md:min-w-[300px]">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px] pointer-events-none">search</span>
            <input
              type="text"
              placeholder="Search fleet..."
              className="pl-10 pr-4 py-2 bg-surface border border-outline-variant rounded-lg text-body-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary w-full transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-sm w-full md:w-auto">
            <select 
              className="flex-1 md:flex-none px-3 py-2 bg-surface border border-outline-variant rounded-lg text-body-sm focus:outline-none focus:border-primary min-w-[120px]"
              value={vehicleFilter}
              onChange={(e) => setVehicleFilter(e.target.value)}
            >
              <option value="">All Vehicles</option>
              <option value="On Trip">On Trip</option>
              <option value="Available">Available</option>
              <option value="In Shop">In Shop</option>
              <option value="Retired">Retired</option>
            </select>
            
            <button 
              onClick={handleFitBounds}
              className="flex items-center justify-center p-2 bg-surface-container border border-outline-variant hover:bg-surface-container-high rounded-lg transition-colors shrink-0"
              title="Fit to Bounds"
            >
              <span className="material-symbols-outlined text-[20px]">fit_screen</span>
            </button>

            {isModal && (
              <button 
                onClick={onClose}
                className="p-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-low rounded-full transition-colors ml-auto md:ml-2"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            )}
          </div>
        </div>
      </div>
      )}

      {/* Map Area */}
      <div className="flex-1 relative bg-[#E3EAEC]">
        {mapLoading && (
          <div className="absolute inset-0 bg-surface/50 z-[1000] flex flex-col items-center justify-center backdrop-blur-sm">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 font-medium text-on-surface-variant">Syncing Fleet Data...</p>
          </div>
        )}

        {(!mapLoading && fleetData.vehicles.length === 0 && fleetData.drivers.length === 0 && !fleetData.bounds?.min_lat) ? (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-surface-container-lowest">
            <span className="material-symbols-outlined text-6xl text-outline mb-4">location_off</span>
            <h3 className="font-title-md text-on-surface">No Fleet Data Found</h3>
            <p className="text-body-md text-on-surface-variant mt-2 max-w-md text-center">
              Try adjusting your search criteria or ensuring vehicles have active GPS coordinates.
            </p>
          </div>
        ) : (
          <MapContainer 
            center={[37.7749, -122.4194]} 
            zoom={10} 
            className="w-full h-full z-0"
            zoomControl={false}
            dragging={!isWidget}
            touchZoom={!isWidget}
            doubleClickZoom={!isWidget}
            scrollWheelZoom={!isWidget}
            boxZoom={!isWidget}
            keyboard={!isWidget}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />
            <MapBoundsFitter bounds={fleetData.bounds} isWidget={isWidget} />
            {!isWidget && <ZoomControl position="topright" />}

            {/* Vehicle Markers */}
            {showVehicles && fleetData.vehicles.map(v => {
              if (v.latitude == null || v.longitude == null) return null;
              const colors = getVehicleStatusColors(v.status);
              return (
                <Marker 
                  key={`v-${v.vehicle_id}`} 
                  position={[v.latitude, v.longitude]}
                  icon={createCustomIcon(v.status, false, v.has_critical_alert)}
                >
                  <Popup className="rounded-xl overflow-hidden shadow-md">
                    <div className="min-w-[200px]">
                      <div className={`px-4 py-2 border-b border-outline-variant ${colors.bg}`}>
                        <div className="flex justify-between items-center">
                          <h4 className="font-bold text-on-surface m-0 text-[14px]">{v.vehicle_name}</h4>
                          <span className={`text-[11px] font-bold uppercase ${colors.color}`}>{v.status}</span>
                        </div>
                        <p className="text-[12px] opacity-80 m-0">{v.registration_number}</p>
                      </div>
                      <div className="p-4 space-y-2 bg-white">
                        <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                          <span className="text-[12px] text-on-surface-variant">Driver</span>
                          <span className="text-[13px] font-medium text-on-surface">{v.driver_name || 'Unassigned'}</span>
                        </div>
                        <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                          <span className="text-[12px] text-on-surface-variant">Active Trip</span>
                          <span className="text-[13px] font-medium text-on-surface">{v.active_trip || 'None'}</span>
                        </div>
                        <div className="flex justify-between items-center pt-1">
                          <span className="text-[11px] text-on-surface-variant">Last Updated</span>
                          <span className="text-[11px] text-on-surface-variant">{new Date(v.last_updated).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* Driver Markers */}
            {showDrivers && fleetData.drivers.map(d => {
              if (d.latitude == null || d.longitude == null) return null;
              const colors = getDriverStatusColors(d.status);
              return (
                <Marker 
                  key={`d-${d.driver_id}`} 
                  position={[d.latitude, d.longitude]}
                  icon={createCustomIcon(d.status, true, d.has_critical_alert)}
                >
                  <Popup className="rounded-xl overflow-hidden shadow-md">
                    <div className="min-w-[200px]">
                      <div className={`px-4 py-2 border-b border-outline-variant ${colors.bg}`}>
                        <div className="flex justify-between items-center">
                          <h4 className="font-bold text-on-surface m-0 text-[14px]">{d.driver_name}</h4>
                          <span className={`text-[11px] font-bold uppercase ${colors.color}`}>{d.status}</span>
                        </div>
                      </div>
                      <div className="p-4 space-y-2 bg-white">
                        <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                          <span className="text-[12px] text-on-surface-variant">Vehicle</span>
                          <span className="text-[13px] font-medium text-on-surface">{d.assigned_vehicle || 'Unassigned'}</span>
                        </div>
                        <div className="flex justify-between items-center border-b border-outline-variant/30 pb-2">
                          <span className="text-[12px] text-on-surface-variant">Active Trip</span>
                          <span className="text-[13px] font-medium text-on-surface">{d.active_trip || 'None'}</span>
                        </div>
                        <div className="flex justify-between items-center pt-1">
                          <span className="text-[11px] text-on-surface-variant">Last Updated</span>
                          <span className="text-[11px] text-on-surface-variant">{new Date(d.last_updated).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        )}
        
        {/* Floating Filter Overlay */}
        {!isWidget && (
          <div className="absolute top-4 left-4 z-[400] flex flex-col gap-2 bg-white/90 backdrop-blur rounded-lg shadow-sm border border-outline-variant p-2">
            <label className="flex items-center gap-2 cursor-pointer hover:bg-surface-container px-2 py-1 rounded">
              <input type="checkbox" checked={showVehicles} onChange={(e) => setShowVehicles(e.target.checked)} className="rounded text-primary focus:ring-primary" />
              <span className="text-body-sm font-medium text-on-surface flex items-center gap-1"><span className="material-symbols-outlined text-[16px] text-blue-600">directions_car</span> Vehicles</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer hover:bg-surface-container px-2 py-1 rounded">
              <input type="checkbox" checked={showDrivers} onChange={(e) => setShowDrivers(e.target.checked)} className="rounded text-primary focus:ring-primary" />
              <span className="text-body-sm font-medium text-on-surface flex items-center gap-1"><span className="material-symbols-outlined text-[16px] text-green-600">person</span> Drivers</span>
            </label>
          </div>
        )}

        {isWidget && onExpand && (
          <div 
            className="absolute inset-0 z-[500] cursor-pointer group hover:bg-black/5 transition-colors"
            onClick={onExpand}
          >
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none"></div>
            
            <div className="absolute bottom-[80px] left-4 right-4 flex justify-between items-end pointer-events-none">
              <div className="text-white">
                <h3 className="font-title-sm drop-shadow-md">Live Fleet Map</h3>
                <p className="text-[12px] opacity-80 drop-shadow-md">View full fleet tracking</p>
              </div>
              <div className="bg-primary text-white p-2 rounded-full shadow-lg flex items-center justify-center opacity-100 pointer-events-none">
                <span className="material-symbols-outlined">open_in_full</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className={`grid grid-cols-2 md:grid-cols-4 gap-0 shrink-0 ${isWidget ? 'absolute bottom-0 left-0 right-0 z-[600] bg-black/40 text-white backdrop-blur-sm' : 'border-t border-outline-variant bg-surface-container-lowest'}`}>
        <div className={`p-3 text-center ${isWidget ? 'border-r border-white/20' : 'border-r border-b md:border-b-0 border-outline-variant'}`}>
          <p className={`text-[11px] font-medium uppercase tracking-wider ${isWidget ? 'text-white/70' : 'text-on-surface-variant'}`}>Active Vehicles</p>
          <p className={`text-title-md font-bold ${isWidget ? 'text-white' : 'text-primary'}`}>{stats.activeVehicles}</p>
        </div>
        <div className={`p-3 text-center ${isWidget ? 'border-r border-white/20' : 'border-r border-b md:border-b-0 border-outline-variant'}`}>
          <p className={`text-[11px] font-medium uppercase tracking-wider ${isWidget ? 'text-white/70' : 'text-on-surface-variant'}`}>On Route</p>
          <p className={`text-title-md font-bold ${isWidget ? 'text-white' : 'text-on-surface'}`}>{stats.onRoutePercent}%</p>
        </div>
        <div className={`p-3 text-center ${isWidget ? 'border-r border-white/20' : 'border-r border-outline-variant'}`}>
          <p className={`text-[11px] font-medium uppercase tracking-wider ${isWidget ? 'text-white/70' : 'text-on-surface-variant'}`}>Avg ETA</p>
          <p className={`text-title-md font-bold ${isWidget ? 'text-white' : 'text-on-surface'}`}>{stats.avgEta}</p>
        </div>
        <div className="p-3 text-center">
          <p className={`text-[11px] font-medium uppercase tracking-wider ${isWidget ? 'text-white/70' : 'text-on-surface-variant'}`}>Low Alerts</p>
          <p className={`text-title-md font-bold ${isWidget ? 'text-white' : (stats.lowAlerts > 0 ? 'text-error' : 'text-on-surface')}`}>{stats.lowAlerts}</p>
        </div>
      </div>
    </div>
  );
};

export default FleetMapView;
