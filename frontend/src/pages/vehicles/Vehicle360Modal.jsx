import React, { useState, useEffect, useCallback } from 'react';
import vehicleApi from '../../services/vehicleApi';
import DocumentsPanel from '../../components/documents/DocumentsPanel';

const Vehicle360Modal = ({ isOpen, onClose, vehicleId, onStatusChange }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [profile, setProfile] = useState(null);
  const [tco, setTco] = useState(null);
  const [odometerHistory, setOdometerHistory] = useState([]);
  const [odometerStats, setOdometerStats] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Status transition state
  const [targetStatus, setTargetStatus] = useState('');
  const [transitionReason, setTransitionReason] = useState('');
  const [retiredDate, setRetiredDate] = useState('');
  const [salePrice, setSalePrice] = useState('');
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Odometer recording state
  const [showOdometerModal, setShowOdometerModal] = useState(false);
  const [newReadingKm, setNewReadingKm] = useState('');
  const [readingSource, setReadingSource] = useState('manual');
  const [readingNotes, setReadingNotes] = useState('');
  const [isRecordingOdo, setIsRecordingOdo] = useState(false);

  const loadData = useCallback(async () => {
    if (!vehicleId) return;
    try {
      setLoading(true);
      setError(null);

      const [pRes, tcoRes, odoHistRes, odoStatsRes] = await Promise.all([
        vehicleApi.getVehicle360(vehicleId),
        vehicleApi.getVehicleTCO(vehicleId).catch(() => ({ data: { data: null } })),
        vehicleApi.getOdometerHistory(vehicleId).catch(() => ({ data: { data: [] } })),
        vehicleApi.getOdometerStats(vehicleId).catch(() => ({ data: { data: null } }))
      ]);

      setProfile(pRes.data);
      setTco(tcoRes.data.data);
      setOdometerHistory(odoHistRes.data.data || []);
      setOdometerStats(odoStatsRes.data);
    } catch (err) {
      console.error('Failed to load Vehicle 360:', err);
      setError('Failed to load vehicle profile.');
    } finally {
      setLoading(false);
    }
  }, [vehicleId]);

  useEffect(() => {
    if (isOpen && vehicleId) {
      loadData();
    }
  }, [isOpen, vehicleId, loadData]);

  if (!isOpen) return null;

  const vehicle = profile?.vehicle;
  const allowedTransitions = profile?.allowed_transitions || [];

  const handleStatusTransition = async (e) => {
    e.preventDefault();
    if (!targetStatus) return;
    try {
      setIsTransitioning(true);
      await vehicleApi.updateVehicleStatus(vehicleId, {
        new_status: targetStatus,
        reason: transitionReason || undefined,
        retired_date: retiredDate || undefined,
        sale_price: salePrice ? parseFloat(salePrice) : undefined
      });
      setTargetStatus('');
      setTransitionReason('');
      setRetiredDate('');
      setSalePrice('');
      await loadData();
      if (onStatusChange) onStatusChange();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to update vehicle status.');
    } finally {
      setIsTransitioning(false);
    }
  };

  const handleRecordOdometer = async (e) => {
    e.preventDefault();
    if (!newReadingKm) return;
    try {
      setIsRecordingOdo(true);
      await vehicleApi.recordOdometer(vehicleId, {
        reading_km: parseFloat(newReadingKm),
        source: readingSource,
        notes: readingNotes || undefined
      });
      setShowOdometerModal(false);
      setNewReadingKm('');
      setReadingNotes('');
      await loadData();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to record odometer reading.');
    } finally {
      setIsRecordingOdo(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-3 md:p-6 overflow-y-auto">
      <div className="bg-surface rounded-2xl max-w-4xl w-full border border-outline-variant shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 md:p-6 bg-surface-container-low border-b border-outline-variant flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center text-xl font-bold">
              <span className="material-symbols-outlined text-[28px]">directions_car</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-headline-sm font-bold text-on-surface">
                  {vehicle?.vehicle_name || 'Vehicle 360'}
                </h2>
                <span className="bg-primary-container/20 text-primary px-2.5 py-0.5 rounded-full text-xs font-bold font-data-tabular">
                  {vehicle?.registration_number}
                </span>
              </div>
              <p className="text-body-sm text-outline">
                {vehicle?.manufacturer} {vehicle?.model} {vehicle?.variant ? `(${vehicle.variant})` : ''} • {vehicle?.vehicle_type}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-surface-container-high text-outline hover:text-on-surface transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-outline-variant bg-surface-container-lowest px-4 gap-2 overflow-x-auto text-xs md:text-sm font-bold">
          {[
            { id: 'overview', label: 'Specs & Overview', icon: 'info' },
            { id: 'lifecycle', label: 'Lifecycle Status', icon: 'alt_route' },
            { id: 'odometer', label: 'Odometer History', icon: 'speed' },
            { id: 'documents', label: 'Documents & Contracts', icon: 'folder_open' },
            { id: 'tco', label: 'TCO Economics', icon: 'analytics' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'border-primary text-primary font-bold'
                  : 'border-transparent text-outline hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="p-4 md:p-6 overflow-y-auto flex-1 bg-surface">
          {loading ? (
            <div className="p-12 text-center text-outline">Loading Vehicle 360 Profile...</div>
          ) : error ? (
            <div className="p-6 text-center text-error font-bold">{error}</div>
          ) : (
            <>
              {/* TAB 1: Specs & Overview */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-surface-container-low p-3.5 rounded-lg border border-outline-variant">
                      <p className="text-xs text-outline font-bold uppercase">VIN / Chassis</p>
                      <p className="font-bold text-on-surface text-sm font-data-tabular mt-1">{vehicle?.vin || 'N/A'}</p>
                    </div>
                    <div className="bg-surface-container-low p-3.5 rounded-lg border border-outline-variant">
                      <p className="text-xs text-outline font-bold uppercase">Body Type</p>
                      <p className="font-bold text-on-surface text-sm mt-1">{vehicle?.body_type || 'N/A'}</p>
                    </div>
                    <div className="bg-surface-container-low p-3.5 rounded-lg border border-outline-variant">
                      <p className="text-xs text-outline font-bold uppercase">Powertrain</p>
                      <p className="font-bold text-on-surface text-sm mt-1">{vehicle?.powertrain || vehicle?.fuel_type}</p>
                    </div>
                    <div className="bg-surface-container-low p-3.5 rounded-lg border border-outline-variant">
                      <p className="text-xs text-outline font-bold uppercase">Seating</p>
                      <p className="font-bold text-on-surface text-sm mt-1">{vehicle?.seating_capacity ? `${vehicle.seating_capacity} Seats` : 'N/A'}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="border border-outline-variant rounded-lg p-4 bg-surface-container-lowest">
                      <h4 className="font-bold text-on-surface text-sm mb-3 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary text-[18px]">payments</span>
                        Ownership & Acquisition
                      </h4>
                      <dl className="grid grid-cols-2 gap-2 text-xs">
                        <dt className="text-outline">Ownership Type:</dt>
                        <dd className="font-bold text-on-surface text-right">{vehicle?.ownership_type || 'Owned'}</dd>
                        <dt className="text-outline">Acquisition Cost:</dt>
                        <dd className="font-bold text-on-surface text-right font-data-tabular">
                          {vehicle?.acquisition_cost ? `₹${Number(vehicle.acquisition_cost).toLocaleString()}` : 'N/A'}
                        </dd>
                        <dt className="text-outline">Acquisition Date:</dt>
                        <dd className="font-bold text-on-surface text-right">{vehicle?.acquisition_date || 'N/A'}</dd>
                        {vehicle?.lease_provider && (
                          <>
                            <dt className="text-outline">Lease Provider:</dt>
                            <dd className="font-bold text-on-surface text-right truncate">{vehicle.lease_provider}</dd>
                            <dt className="text-outline">Monthly Lease:</dt>
                            <dd className="font-bold text-on-surface text-right font-data-tabular">₹{Number(vehicle.monthly_lease_cost).toLocaleString()}</dd>
                          </>
                        )}
                      </dl>
                    </div>

                    <div className="border border-outline-variant rounded-lg p-4 bg-surface-container-lowest">
                      <h4 className="font-bold text-on-surface text-sm mb-3 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary text-[18px]">speed</span>
                        Telemetry & Engine Hours
                      </h4>
                      <dl className="grid grid-cols-2 gap-2 text-xs">
                        <dt className="text-outline">Current Odometer:</dt>
                        <dd className="font-bold text-on-surface text-right font-data-tabular">{Number(vehicle?.current_odometer_km).toLocaleString()} km</dd>
                        <dt className="text-outline">Engine Hours:</dt>
                        <dd className="font-bold text-on-surface text-right font-data-tabular">{Number(vehicle?.engine_hours || 0).toLocaleString()} hrs</dd>
                        <dt className="text-outline">Capacity:</dt>
                        <dd className="font-bold text-on-surface text-right font-data-tabular">{Number(vehicle?.capacity_kg).toLocaleString()} kg</dd>
                        <dt className="text-outline">Insurance Expiry:</dt>
                        <dd className="font-bold text-on-surface text-right">{vehicle?.insurance_expiry || 'N/A'}</dd>
                      </dl>
                    </div>
                  </div>

                  {vehicle?.notes && (
                    <div className="p-3 bg-surface-container-low border border-outline-variant rounded-lg text-xs">
                      <p className="font-bold text-outline uppercase mb-1">Notes</p>
                      <p className="text-on-surface">{vehicle.notes}</p>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: Lifecycle State Machine */}
              {activeTab === 'lifecycle' && (
                <div className="space-y-6">
                  <div className="p-4 bg-surface-container-low border border-outline-variant rounded-xl flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-outline uppercase">Current Lifecycle State</p>
                      <h3 className="text-title-medium font-bold text-on-surface mt-1">{vehicle?.status}</h3>
                    </div>
                    <span className="bg-primary/10 text-primary font-bold px-3 py-1 rounded-full text-xs">
                      State Machine Enforced
                    </span>
                  </div>

                  {/* Transition Form */}
                  <form onSubmit={handleStatusTransition} className="border border-outline-variant rounded-xl p-4 bg-surface-container-lowest space-y-4">
                    <h4 className="font-bold text-on-surface text-sm flex items-center gap-2">
                      <span className="material-symbols-outlined text-primary text-[18px]">transform</span>
                      Transition Lifecycle Status
                    </h4>

                    {allowedTransitions.length === 0 ? (
                      <p className="text-xs text-outline italic">
                        No state transitions allowed from '{vehicle?.status}'. This state is terminal or locked.
                      </p>
                    ) : (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs font-bold text-outline mb-1">Target Status *</label>
                            <select
                              value={targetStatus}
                              onChange={(e) => setTargetStatus(e.target.value)}
                              required
                              className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface text-xs font-bold"
                            >
                              <option value="">Select target state...</option>
                              {allowedTransitions.map((st) => (
                                <option key={st} value={st}>{st}</option>
                              ))}
                            </select>
                          </div>

                          <div>
                            <label className="block text-xs font-bold text-outline mb-1">Transition Reason</label>
                            <input
                              type="text"
                              placeholder="Reason for lifecycle state change"
                              value={transitionReason}
                              onChange={(e) => setTransitionReason(e.target.value)}
                              className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface text-xs"
                            />
                          </div>
                        </div>

                        {/* Extra metadata fields for Retired / Sold */}
                        {(targetStatus === 'Retired' || targetStatus === 'Sold') && (
                          <div className="grid grid-cols-2 gap-4 pt-2">
                            <div>
                              <label className="block text-xs font-bold text-outline mb-1">Retirement Date</label>
                              <input
                                type="date"
                                value={retiredDate}
                                onChange={(e) => setRetiredDate(e.target.value)}
                                className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface text-xs"
                              />
                            </div>
                            {targetStatus === 'Sold' && (
                              <div>
                                <label className="block text-xs font-bold text-outline mb-1">Sale Price (₹)</label>
                                <input
                                  type="number"
                                  placeholder="250000"
                                  value={salePrice}
                                  onChange={(e) => setSalePrice(e.target.value)}
                                  className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface text-xs"
                                />
                              </div>
                            )}
                          </div>
                        )}

                        <div className="flex justify-end pt-2">
                          <button
                            type="submit"
                            disabled={isTransitioning || !targetStatus}
                            className="bg-primary text-on-primary font-bold text-xs px-4 py-2 rounded hover:opacity-90 disabled:opacity-50 transition-all"
                          >
                            {isTransitioning ? 'Updating State...' : 'Apply Transition'}
                          </button>
                        </div>
                      </>
                    )}
                  </form>
                </div>
              )}

              {/* TAB 3: Odometer History */}
              {activeTab === 'odometer' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-on-surface text-sm">Odometer Reading Log</h4>
                      <p className="text-xs text-outline">Ascending reading sequence enforced</p>
                    </div>
                    <button
                      onClick={() => setShowOdometerModal(true)}
                      className="bg-primary text-on-primary text-xs font-bold px-3 py-1.5 rounded hover:opacity-90 transition-all flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[16px]">add</span>
                      Record Reading
                    </button>
                  </div>

                  {odometerStats && (
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div className="bg-surface-container-low p-3 rounded border border-outline-variant">
                        <span className="text-outline font-bold">Total Readings:</span>
                        <p className="font-bold text-on-surface text-sm">{odometerStats.total_readings}</p>
                      </div>
                      <div className="bg-surface-container-low p-3 rounded border border-outline-variant">
                        <span className="text-outline font-bold">Latest Odometer:</span>
                        <p className="font-bold text-on-surface text-sm font-data-tabular">{Number(odometerStats.current_odometer_km).toLocaleString()} km</p>
                      </div>
                      <div className="bg-surface-container-low p-3 rounded border border-outline-variant">
                        <span className="text-outline font-bold">Total Distance Logged:</span>
                        <p className="font-bold text-primary text-sm font-data-tabular">
                          {odometerStats.total_distance_km ? `${Number(odometerStats.total_distance_km).toLocaleString()} km` : 'N/A'}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="border border-outline-variant rounded-lg overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-surface-container-low text-outline font-bold uppercase border-b border-outline-variant">
                        <tr>
                          <th className="p-3">Recorded At</th>
                          <th className="p-3">Reading (km)</th>
                          <th className="p-3">Source</th>
                          <th className="p-3">Notes</th>
                        </tr>
                      </thead>
                      <tbody>
                        {odometerHistory.length === 0 ? (
                          <tr><td colSpan="4" className="p-6 text-center text-outline">No odometer history recorded yet.</td></tr>
                        ) : (
                          odometerHistory.map((item) => (
                            <tr key={item.id} className="border-b border-outline-variant hover:bg-surface-container-lowest">
                              <td className="p-3 font-data-tabular">{new Date(item.recorded_at).toLocaleString()}</td>
                              <td className="p-3 font-bold font-data-tabular text-on-surface">{Number(item.reading_km).toLocaleString()} km</td>
                              <td className="p-3">
                                <span className="uppercase text-[10px] font-bold bg-surface-container px-2 py-0.5 rounded text-outline">
                                  {item.source}
                                </span>
                              </td>
                              <td className="p-3 text-outline">{item.notes || '-'}</td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Record Odometer Modal */}
                  {showOdometerModal && (
                    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                      <div className="bg-surface rounded-xl p-5 max-w-sm w-full border border-outline-variant shadow-xl">
                        <h3 className="font-bold text-on-surface text-sm mb-3">Record Odometer Reading</h3>
                        <form onSubmit={handleRecordOdometer} className="space-y-3 text-xs">
                          <div>
                            <label className="block font-bold text-outline mb-1">Reading (km) *</label>
                            <input
                              type="number"
                              step="0.1"
                              required
                              placeholder="e.g. 52500"
                              value={newReadingKm}
                              onChange={(e) => setNewReadingKm(e.target.value)}
                              className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface font-data-tabular font-bold"
                            />
                            <p className="text-[10px] text-outline mt-1">Must be $\ge$ {vehicle?.current_odometer_km} km unless source='correction'.</p>
                          </div>

                          <div>
                            <label className="block font-bold text-outline mb-1">Source</label>
                            <select
                              value={readingSource}
                              onChange={(e) => setReadingSource(e.target.value)}
                              className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface font-bold"
                            >
                              <option value="manual">Manual Check</option>
                              <option value="trip">Trip Completion</option>
                              <option value="maintenance">Maintenance Service</option>
                              <option value="telemetry">GPS Telemetry</option>
                              <option value="correction">Correction Override</option>
                            </select>
                          </div>

                          <div>
                            <label className="block font-bold text-outline mb-1">Notes</label>
                            <input
                              type="text"
                              placeholder="Inspection details"
                              value={readingNotes}
                              onChange={(e) => setReadingNotes(e.target.value)}
                              className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                            />
                          </div>

                          <div className="flex justify-end gap-2 pt-2">
                            <button
                              type="button"
                              onClick={() => setShowOdometerModal(false)}
                              className="px-3 py-1.5 border border-outline-variant rounded font-bold"
                            >
                              Cancel
                            </button>
                            <button
                              type="submit"
                              disabled={isRecordingOdo}
                              className="px-3 py-1.5 bg-primary text-on-primary font-bold rounded hover:opacity-90 disabled:opacity-50"
                            >
                              {isRecordingOdo ? 'Saving...' : 'Save Reading'}
                            </button>
                          </div>
                        </form>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 4: Documents & Contracts */}
              {activeTab === 'documents' && (
                <DocumentsPanel vehicleId={vehicleId} onDocumentChange={loadData} />
              )}

              {/* TAB 5: TCO Economics */}
              {activeTab === 'tco' && (
                <div className="space-y-6">
                  {tco ? (
                    <>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3.5 bg-surface-container-low rounded-lg border border-outline-variant">
                          <p className="text-xs font-bold text-outline uppercase">Operating Cost</p>
                          <p className="text-title-medium font-bold text-on-surface font-data-tabular mt-1">
                            ₹{tco.cost_breakdown.total_operating_cost.toLocaleString()}
                          </p>
                        </div>
                        <div className="p-3.5 bg-surface-container-low rounded-lg border border-outline-variant">
                          <p className="text-xs font-bold text-outline uppercase">Total TCO</p>
                          <p className="text-title-medium font-bold text-primary font-data-tabular mt-1">
                            ₹{tco.cost_breakdown.total_tco.toLocaleString()}
                          </p>
                        </div>
                        <div className="p-3.5 bg-surface-container-low rounded-lg border border-outline-variant">
                          <p className="text-xs font-bold text-outline uppercase">Cost / KM</p>
                          <p className="text-title-medium font-bold text-secondary font-data-tabular mt-1">
                            {tco.unit_metrics.cost_per_km !== null ? `₹${tco.unit_metrics.cost_per_km.toFixed(2)}/km` : 'N/A'}
                          </p>
                        </div>
                        <div className="p-3.5 bg-surface-container-low rounded-lg border border-outline-variant">
                          <p className="text-xs font-bold text-outline uppercase">Fuel Cost / KM</p>
                          <p className="text-title-medium font-bold text-on-surface font-data-tabular mt-1">
                            {tco.unit_metrics.fuel_cost_per_km !== null ? `₹${tco.unit_metrics.fuel_cost_per_km.toFixed(2)}/km` : 'N/A'}
                          </p>
                        </div>
                      </div>

                      {/* Detailed Cost Breakdown Table */}
                      <div className="border border-outline-variant rounded-xl p-4 bg-surface-container-lowest">
                        <h4 className="font-bold text-on-surface text-sm mb-3">Cost Component Breakdown</h4>
                        <dl className="grid grid-cols-2 gap-3 text-xs border-t border-outline-variant pt-3">
                          <dt className="text-outline">Acquisition Capital Cost:</dt>
                          <dd className="font-bold text-on-surface text-right font-data-tabular">₹{tco.cost_breakdown.acquisition_cost.toLocaleString()}</dd>
                          <dt className="text-outline">Total Fuel Expense:</dt>
                          <dd className="font-bold text-on-surface text-right font-data-tabular">₹{tco.cost_breakdown.total_fuel_cost.toLocaleString()}</dd>
                          <dt className="text-outline">Total Maintenance & Repairs:</dt>
                          <dd className="font-bold text-on-surface text-right font-data-tabular">₹{tco.cost_breakdown.total_maintenance_cost.toLocaleString()}</dd>
                          <dt className="text-outline">Operational & Toll Expenses:</dt>
                          <dd className="font-bold text-on-surface text-right font-data-tabular">₹{tco.cost_breakdown.total_other_expenses.toLocaleString()}</dd>
                        </dl>
                      </div>
                    </>
                  ) : (
                    <p className="p-6 text-center text-outline text-sm">No TCO cost data available for this vehicle.</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Vehicle360Modal;
