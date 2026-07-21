import React from 'react';

const KpiRow = ({ data, loading }) => {
  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-xs md:gap-md animate-pulse">
        {[...Array(7)].map((_, i) => (
          <div key={i} className="bg-surface border border-outline-variant rounded-xl p-md h-[120px]"></div>
        ))}
      </div>
    );
  }

  // Extract variables safely — data comes directly as { fleet, drivers, trips, financial }
  const fleet = data.fleet || data.overview?.fleet || {};
  const drivers = data.drivers || data.overview?.drivers || {};
  const trips = data.trips || data.overview?.trips || {};

  const totalVehicles = fleet.total_vehicles || 0;
  const available = fleet.active_vehicles || 0;
  const onTrip = fleet.vehicles_on_trip || 0;
  const inMaintenance = fleet.vehicles_in_shop || 0;
  const totalDrivers = drivers.total_drivers || 0;
  const activeTrips = trips.active_trips || 0;
  
  // Calculate utilization securely avoiding div by zero
  const utilizationPct = totalVehicles > 0 ? ((available + onTrip) / totalVehicles * 100).toFixed(1) : 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-xs md:gap-md">
      {/* Total Vehicles */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">Total<br/>Vehicles</p>
          <span className="material-symbols-outlined text-primary">local_shipping</span>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{totalVehicles}</h2>
      </div>

      {/* Available */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">Available</p>
          <div className="w-2 h-2 rounded-full bg-secondary mt-1"></div>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{available}</h2>
      </div>

      {/* On Trip */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">On Trip</p>
          <div className="w-2 h-2 rounded-full bg-primary mt-1"></div>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{onTrip}</h2>
      </div>

      {/* In Maintenance */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">In Shop</p>
          <div className="w-2 h-2 rounded-full bg-tertiary mt-1"></div>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{inMaintenance}</h2>
      </div>

      {/* Drivers */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">Active<br/>Drivers</p>
          <span className="material-symbols-outlined text-outline">person_pin</span>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{totalDrivers}</h2>
      </div>

      {/* Active Trips */}
      <div className="bg-surface border border-outline-variant p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between">
        <div className="flex justify-between items-start mb-sm">
          <p className="text-[11px] text-outline font-bold uppercase tracking-wide leading-tight">Active<br/>Trips</p>
          <span className="material-symbols-outlined text-primary">route</span>
        </div>
        <h2 className="text-display-lg font-display-lg text-on-surface">{activeTrips}</h2>
      </div>

      {/* Fleet Utilization */}
      <div className="bg-primary text-on-primary border border-primary p-md rounded-lg shadow-[0px_2px_4px_rgba(0,0,0,0.05)] flex flex-col justify-between relative overflow-hidden">
        <div className="relative z-10">
          <p className="text-[11px] text-on-primary-container opacity-90 font-bold uppercase tracking-wide mb-sm">Utilization</p>
          <h2 className="text-display-lg font-display-lg">{utilizationPct}%</h2>
          <div className="w-full bg-white/20 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-white h-full" style={{ width: `${utilizationPct}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KpiRow;
