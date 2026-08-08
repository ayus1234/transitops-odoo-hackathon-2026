import React, { useState, useEffect } from 'react';
import { 
  Radio, RefreshCw, AlertTriangle, CheckCircle, Package, Truck, UserCheck, 
  Clock, ArrowRight, Play, CheckCircle2, XCircle, ShieldCheck, MapPin, Zap
} from 'lucide-react';
import { dispatchApi } from '../../services/dispatchApi';
import { useToast } from '../../contexts/ToastContext';

export default function DispatchBoard() {
  const [boardData, setBoardData] = useState({
    kpis: {
      unassigned_jobs_count: 0,
      available_vehicles_count: 0,
      available_drivers_count: 0,
      active_trips_count: 0,
      delayed_trips_count: 0
    },
    unassigned_jobs: [],
    available_vehicles: [],
    available_drivers: [],
    active_trips: []
  });

  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState(null);
  
  // Validation & Dispatch modal states
  const [validationResult, setValidationResult] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isDispatching, setIsDispatching] = useState(false);
  const [dispatchNotes, setDispatchNotes] = useState('');
  
  // Recommendation state
  const [recommendations, setRecommendations] = useState([]);
  const [isRecommending, setIsRecommending] = useState(false);

  const { showToast } = useToast();

  useEffect(() => {
    fetchBoardData();
  }, []);

  const fetchBoardData = async () => {
    setLoading(true);
    try {
      const data = await dispatchApi.getDispatchBoard();
      setBoardData(data);
    } catch (err) {
      showToast('Failed to load dispatch control tower data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchRecommendations = async (jobId) => {
    setIsRecommending(true);
    try {
      const res = await dispatchApi.getRecommendations(jobId);
      setRecommendations(res.recommendations || []);
      if (res.recommendations && res.recommendations.length > 0) {
        showToast(`Found ${res.recommendations.length} intelligent vehicle recommendations!`, 'info');
      }
    } catch (err) {
      showToast('Failed to fetch AI vehicle recommendations', 'error');
    } finally {
      setIsRecommending(false);
    }
  };

  const handleRunValidation = async () => {
    if (!selectedJob || !selectedVehicle || !selectedDriver) return;
    setIsValidating(true);
    try {
      const result = await dispatchApi.validateDispatch({
        job_id: selectedJob.id,
        vehicle_id: selectedVehicle.id,
        driver_id: selectedDriver.id
      });
      setValidationResult(result);
    } catch (err) {
      showToast(err.response?.data?.error?.message || 'Validation failed', 'error');
    } finally {
      setIsValidating(false);
    }
  };

  const handleExecuteDispatch = async () => {
    if (!selectedJob || !selectedVehicle || !selectedDriver) return;
    setIsDispatching(true);
    try {
      await dispatchApi.assignAndDispatch({
        job_id: selectedJob.id,
        vehicle_id: selectedVehicle.id,
        driver_id: selectedDriver.id,
        notes: dispatchNotes || undefined
      });
      showToast(`Job ${selectedJob.job_number} successfully assigned & dispatched!`, 'success');
      setSelectedJob(null);
      setSelectedVehicle(null);
      setSelectedDriver(null);
      setValidationResult(null);
      setDispatchNotes('');
      fetchBoardData();
    } catch (err) {
      showToast(err.response?.data?.error?.message || 'Operational dispatch failed', 'error');
    } finally {
      setIsDispatching(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Control Tower Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
            <Radio className="w-7 h-7 text-cyan-400 animate-pulse" />
            Operations Control Center — Dispatch Board
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time operational dispatch, fleet asset matching, and route execution
          </p>
        </div>
        <button
          onClick={fetchBoardData}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-sm font-medium transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Control Tower
        </button>
      </div>

      {/* Real-time KPI Overview Bar */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-slate-800/80 border border-slate-700/80 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Jobs Waiting</span>
            <Package className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{boardData.kpis.unassigned_jobs_count}</div>
          <div className="text-xs text-amber-400/80 mt-1 font-medium">Pending Dispatch</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Available Vehicles</span>
            <Truck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{boardData.kpis.available_vehicles_count}</div>
          <div className="text-xs text-emerald-400/80 mt-1 font-medium">Ready for Duty</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Available Drivers</span>
            <UserCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{boardData.kpis.available_drivers_count}</div>
          <div className="text-xs text-cyan-400/80 mt-1 font-medium">On Shift & Compliant</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 p-4 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Active Trips</span>
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{boardData.kpis.active_trips_count}</div>
          <div className="text-xs text-indigo-400/80 mt-1 font-medium">In Transit / Dispatched</div>
        </div>

        <div className="bg-slate-800/80 border border-slate-700/80 p-4 rounded-2xl col-span-2 md:col-span-1">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
            <span>Delayed Trips</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{boardData.kpis.delayed_trips_count}</div>
          <div className="text-xs text-red-400/80 mt-1 font-medium">Overdue Expected Arrival</div>
        </div>
      </div>

      {/* 3-Column Operations Control Center */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Column 1: Unassigned Shipping Jobs */}
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 flex flex-col h-[620px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700/80">
            <h3 className="font-semibold text-slate-200 flex items-center gap-2 text-sm">
              <Package className="w-4 h-4 text-amber-400" />
              1. Select Customer Job ({boardData.unassigned_jobs.length})
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto mt-3 space-y-3 pr-1">
            {boardData.unassigned_jobs.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs">
                No unassigned jobs pending dispatch.
              </div>
            ) : (
              boardData.unassigned_jobs.map((job) => {
                const isSelected = selectedJob?.id === job.id;
                return (
                  <div
                    key={job.id}
                    onClick={() => {
                      setSelectedJob(job);
                      setValidationResult(null);
                      setRecommendations([]);
                      handleFetchRecommendations(job.id);
                    }}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-indigo-600/15 border-indigo-500 shadow-md shadow-indigo-500/10'
                        : 'bg-slate-900/60 border-slate-700/60 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-slate-100">{job.job_number}</span>
                      <span className={`px-2 py-0.5 text-[10px] font-semibold rounded-full border ${
                        job.priority === 'Urgent' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                      }`}>
                        {job.priority} Priority
                      </span>
                    </div>

                    <div className="text-xs font-medium text-slate-300 mt-1.5">{job.customer_name}</div>

                    <div className="mt-2 text-[11px] text-slate-400 space-y-1">
                      <div className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-indigo-400 shrink-0" />
                        <span className="truncate">{job.pickup_address}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
                        <span className="truncate">{job.delivery_address}</span>
                      </div>
                    </div>

                    {job.cargo_weight_kg && (
                      <div className="mt-2 flex items-center justify-between">
                        <div className="text-[11px] text-slate-400 bg-slate-800/80 px-2 py-1 rounded-md">
                          Weight: <span className="text-slate-200 font-semibold">{job.cargo_weight_kg} kg</span>
                        </div>
                        {isSelected && (
                          <span className="text-[11px] font-semibold text-indigo-400 flex items-center gap-1">
                            <Zap className="w-3 h-3" /> Auto-Ranking Active
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Column 2: Available Vehicles & Drivers Matching */}
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 flex flex-col h-[620px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700/80">
            <h3 className="font-semibold text-slate-200 flex items-center gap-2 text-sm">
              <Truck className="w-4 h-4 text-emerald-400" />
              2. Select Vehicle & Driver
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto mt-3 space-y-4 pr-1">
            {/* Vehicle Selection Section */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Available Vehicles {recommendations.length > 0 && '(AI Ranked)'}
                </div>
                {isRecommending && (
                  <span className="text-[10px] text-cyan-400 animate-pulse font-medium">Evaluating payload & proximity...</span>
                )}
              </div>
              <div className="space-y-2">
                {boardData.available_vehicles.map((v) => {
                  const isSelected = selectedVehicle?.id === v.id;
                  const rec = recommendations.find(r => r.vehicle_id === v.id);

                  return (
                    <div
                      key={v.id}
                      onClick={() => {
                        setSelectedVehicle(v);
                        setValidationResult(null);
                        if (rec?.suggested_driver_id) {
                          const suggested = boardData.available_drivers.find(d => d.id === rec.suggested_driver_id);
                          if (suggested) setSelectedDriver(suggested);
                        }
                      }}
                      className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-emerald-600/15 border-emerald-500 shadow-md shadow-emerald-500/10'
                          : rec
                          ? 'bg-slate-900/80 border-cyan-500/30 hover:border-cyan-500/60'
                          : 'bg-slate-900/60 border-slate-700/60 hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-100">{v.registration_number}</span>
                        <div className="flex items-center gap-1.5">
                          {rec && (
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold border ${
                              rec.overall_match_score >= 85
                                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                                : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                            }`}>
                              ⚡ {rec.overall_match_score}% Match
                            </span>
                          )}
                          <span className="text-emerald-400 font-medium">{v.capacity_kg ? `${v.capacity_kg} kg cap` : 'N/A'}</span>
                        </div>
                      </div>
                      <div className="text-slate-400 text-[11px] mt-0.5">{v.vehicle_name} ({v.vehicle_type})</div>
                      {rec && rec.match_reasons.length > 0 && (
                        <div className="mt-1.5 text-[10px] text-cyan-300/80 space-y-0.5 bg-slate-950/40 p-1.5 rounded-lg border border-cyan-500/10">
                          {rec.match_reasons.slice(0, 2).map((reason, idx) => (
                            <div key={idx} className="truncate">• {reason}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Driver Selection Section */}
            <div>
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Available Drivers</div>
              <div className="space-y-2">
                {boardData.available_drivers.map((d) => {
                  const isSelected = selectedDriver?.id === d.id;
                  return (
                    <div
                      key={d.id}
                      onClick={() => {
                        setSelectedDriver(d);
                        setValidationResult(null);
                      }}
                      className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-cyan-600/15 border-cyan-500 shadow-md shadow-cyan-500/10'
                          : 'bg-slate-900/60 border-slate-700/60 hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-100">{d.license_number}</span>
                        <span className="text-cyan-400 font-medium">Safety: {d.safety_score}%</span>
                      </div>
                      <div className="text-slate-400 text-[11px] mt-0.5">Category: {d.license_category || 'Commercial'}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Column 3: Active Dispatched Trips & Dispatch Execution */}
        <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 flex flex-col h-[620px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-700/80">
            <h3 className="font-semibold text-slate-200 flex items-center gap-2 text-sm">
              <Zap className="w-4 h-4 text-indigo-400" />
              3. Operational Dispatch Action
            </h3>
          </div>

          <div className="mt-3 flex-1 flex flex-col">
            {/* Selection Summary Box */}
            <div className="bg-slate-900/80 border border-slate-700/80 rounded-xl p-3 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Job:</span>
                <span className="font-bold text-slate-100">{selectedJob ? selectedJob.job_number : 'None selected'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Vehicle:</span>
                <span className="font-bold text-emerald-400">{selectedVehicle ? selectedVehicle.registration_number : 'None selected'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Driver:</span>
                <span className="font-bold text-cyan-400">{selectedDriver ? selectedDriver.license_number : 'None selected'}</span>
              </div>
            </div>

            {/* Validation & Execute Actions */}
            <div className="mt-3 space-y-2">
              <button
                disabled={!selectedJob || !selectedVehicle || !selectedDriver || isValidating}
                onClick={handleRunValidation}
                className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl text-xs font-semibold transition-colors disabled:opacity-40"
              >
                {isValidating ? 'Validating Assets...' : 'Run Pre-Dispatch Safety Check'}
              </button>

              {validationResult && (
                <div className={`p-3 rounded-xl border text-xs space-y-1.5 ${
                  validationResult.valid ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-red-500/10 border-red-500/30 text-red-300'
                }`}>
                  <div className="font-bold flex items-center gap-1.5">
                    {validationResult.valid ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <XCircle className="w-4 h-4 text-red-400" />}
                    {validationResult.valid ? 'Pre-dispatch Checks Passed' : 'Dispatch Validation Errors'}
                  </div>
                  {validationResult.errors.map((err, idx) => (
                    <div key={idx} className="text-[11px]">• {err}</div>
                  ))}
                  {validationResult.utilization_pct > 0 && (
                    <div className="text-[11px] text-slate-300 mt-1">
                      Capacity Utilization: <span className="font-semibold">{validationResult.utilization_pct}%</span>
                    </div>
                  )}
                </div>
              )}

              {validationResult?.valid && (
                <div className="space-y-2 pt-2">
                  <textarea
                    rows="2"
                    placeholder="Optional dispatch notes..."
                    value={dispatchNotes}
                    onChange={(e) => setDispatchNotes(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2 text-xs text-slate-100 focus:outline-none"
                  />
                  <button
                    disabled={isDispatching}
                    onClick={handleExecuteDispatch}
                    className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all flex items-center justify-center gap-2"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    {isDispatching ? 'Dispatching Trip...' : 'EXECUTE DISPATCH'}
                  </button>
                </div>
              )}
            </div>

            {/* Active Trips Feed */}
            <div className="mt-4 pt-3 border-t border-slate-700/80 flex-1 overflow-y-auto">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Active Trips Queue</div>
              <div className="space-y-2">
                {boardData.active_trips.slice(0, 4).map((t) => (
                  <div key={t.id} className="p-2.5 bg-slate-900/60 border border-slate-700/60 rounded-xl text-xs flex justify-between items-center">
                    <div>
                      <div className="font-bold text-slate-200">{t.trip_number}</div>
                      <div className="text-[11px] text-slate-400">{t.source} → {t.destination}</div>
                    </div>
                    <span className="px-2 py-0.5 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded-full text-[10px] font-semibold">
                      {t.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
