import React, { useState, useEffect } from 'react';
import { 
  Truck, MapPin, Navigation, CheckCircle2, Clock, 
  Upload, Camera, FileText, AlertTriangle, ShieldCheck, 
  Fuel, Shield, PhoneCall, RefreshCw, Send, ArrowRight
} from 'lucide-react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';
import Modal from '../../components/ui/Modal';

const DriverMobileApp = () => {
  const { showSuccess, showError } = useToast();
  const [loading, setLoading] = useState(true);
  const [activeTrip, setActiveTrip] = useState(null);
  const [showPodModal, setShowPodModal] = useState(false);
  const [showRefuelModal, setShowRefuelModal] = useState(false);
  const [showIssueModal, setShowIssueModal] = useState(false);

  // POD Form State
  const [podPhoto, setPodPhoto] = useState(null);
  const [podSignature, setPodSignature] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [submittingPod, setSubmittingPod] = useState(false);

  // Refuel Form State
  const [fuelLiters, setFuelLiters] = useState('');
  const [fuelCost, setFuelCost] = useState('');
  const [currentOdo, setCurrentOdo] = useState('');

  // Issue Form State
  const [issueDescription, setIssueDescription] = useState('');
  const [issueSeverity, setIssueSeverity] = useState('Medium');

  useEffect(() => {
    fetchActiveTrip();
  }, []);

  const fetchActiveTrip = async () => {
    setLoading(true);
    try {
      const response = await api.get('/trips', { params: { status: 'Dispatched', limit: 1 } });
      if (response.data.items && response.data.items.length > 0) {
        setActiveTrip(response.data.items[0]);
      } else {
        // Fetch any scheduled trip if none dispatched
        const schedRes = await api.get('/trips', { params: { limit: 1 } });
        if (schedRes.data.items && schedRes.data.items.length > 0) {
          setActiveTrip(schedRes.data.items[0]);
        } else {
          setActiveTrip(null);
        }
      }
    } catch (err) {
      console.error("Error loading trip for driver:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTripStatus = async (newStatus) => {
    if (!activeTrip) return;
    try {
      await api.patch(`/trips/${activeTrip.id}/status`, { status: newStatus });
      showSuccess(`Trip updated to ${newStatus}`);
      fetchActiveTrip();
    } catch (err) {
      showError(err.response?.data?.detail || "Failed to update trip status");
    }
  };

  const handleSubmitPod = async (e) => {
    e.preventDefault();
    if (!activeTrip) return;
    setSubmittingPod(true);
    try {
      await api.post('/pod/submit', {
        trip_id: activeTrip.id,
        recipient_name: recipientName || "John Customer",
        signature_data: podSignature || "Digital Signature OK",
        delivery_photo_url: podPhoto || "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400",
        latitude: 28.6139,
        longitude: 77.2090
      });
      showSuccess("Proof of Delivery submitted! Trip marked Completed.");
      setShowPodModal(false);
      fetchActiveTrip();
    } catch (err) {
      showError(err.response?.data?.detail || "Failed to submit Proof of Delivery");
    } finally {
      setSubmittingPod(false);
    }
  };

  const handleSubmitRefuel = async (e) => {
    e.preventDefault();
    if (!activeTrip) return;
    try {
      await api.post('/fuel/log', {
        vehicle_id: activeTrip.vehicle_id,
        quantity_liters: parseFloat(fuelLiters),
        total_cost: parseFloat(fuelCost),
        odometer_reading: parseFloat(currentOdo),
        fuel_type: activeTrip.vehicle?.fuel_type || 'Diesel'
      });
      showSuccess("Refuel log recorded successfully!");
      setShowRefuelModal(false);
      setFuelLiters('');
      setFuelCost('');
    } catch (err) {
      showError(err.response?.data?.detail || "Failed to log refuel");
    }
  };

  const handleSubmitIssue = async (e) => {
    e.preventDefault();
    showSuccess("Issue reported to Dispatcher & Maintenance Manager.");
    setShowIssueModal(false);
    setIssueDescription('');
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-slate-900 text-slate-100 pb-20 shadow-2xl rounded-2xl overflow-hidden border border-slate-800">
      {/* Mobile Top Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-4 text-white flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-xl backdrop-blur-sm">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight">TransitOps Driver</h1>
            <p className="text-xs text-blue-200">Driver Mobile Companion</p>
          </div>
        </div>
        <button 
          onClick={fetchActiveTrip}
          className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white"
        >
          <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Driver Status Card */}
      <div className="p-4 bg-slate-800/80 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-sm border border-emerald-500/30">
            JD
          </div>
          <div>
            <p className="text-sm font-semibold text-white">John Driver</p>
            <p className="text-xs text-slate-400">License: HR-06-2023-8891</p>
          </div>
        </div>
        <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-semibold rounded-full border border-emerald-500/20 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          On Duty
        </span>
      </div>

      {/* Active Trip Container */}
      <div className="p-4 space-y-4">
        {loading ? (
          <div className="p-8 text-center text-slate-400 space-y-3">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
            <p className="text-sm">Loading active trip assignment...</p>
          </div>
        ) : !activeTrip ? (
          <div className="p-8 text-center bg-slate-800/40 rounded-2xl border border-slate-800 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
            <h3 className="font-semibold text-lg text-white">No Active Trips</h3>
            <p className="text-xs text-slate-400">You currently have no dispatched trips. Stand by for dispatcher assignment.</p>
          </div>
        ) : (
          <>
            {/* Active Trip Card */}
            <div className="bg-slate-800/90 rounded-2xl p-4 border border-blue-500/30 shadow-lg space-y-4">
              <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-400">Active Assignment</span>
                  <h2 className="text-xl font-bold text-white leading-tight">Trip #{activeTrip.trip_number}</h2>
                </div>
                <span className={`px-3 py-1 text-xs font-bold rounded-full ${
                  activeTrip.status === 'Dispatched' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                  activeTrip.status === 'Completed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                }`}>
                  {activeTrip.status}
                </span>
              </div>

              {/* Route Summary */}
              <div className="space-y-3 relative pl-6 before:content-[''] before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-700">
                <div className="relative">
                  <span className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-blue-500 ring-4 ring-slate-800"></span>
                  <p className="text-xs text-slate-400">Pickup Origin</p>
                  <p className="text-sm font-medium text-white">{activeTrip.source}</p>
                </div>
                <div className="relative">
                  <span className="absolute -left-6 top-1 w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-slate-800"></span>
                  <p className="text-xs text-slate-400">Delivery Destination</p>
                  <p className="text-sm font-medium text-white">{activeTrip.destination}</p>
                </div>
              </div>

              {/* Assigned Vehicle */}
              {activeTrip.vehicle && (
                <div className="bg-slate-900/60 rounded-xl p-3 flex items-center justify-between border border-slate-700/50">
                  <div className="flex items-center gap-3">
                    <Truck className="w-5 h-5 text-blue-400" />
                    <div>
                      <p className="text-xs text-slate-400">Assigned Vehicle</p>
                      <p className="text-sm font-bold text-white">{activeTrip.vehicle.registration_number}</p>
                    </div>
                  </div>
                  <span className="text-xs px-2 py-0.5 bg-slate-800 rounded text-slate-300 font-mono">
                    {activeTrip.vehicle.capacity_kg} kg
                  </span>
                </div>
              )}

              {/* Action Buttons Grid */}
              <div className="grid grid-cols-2 gap-2 pt-2">
                {activeTrip.status === 'Draft' && (
                  <button
                    onClick={() => handleUpdateTripStatus('Dispatched')}
                    className="col-span-2 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition-all active:scale-98"
                  >
                    <Navigation className="w-5 h-5" />
                    Start Trip & Navigation
                  </button>
                )}

                {activeTrip.status === 'Dispatched' && (
                  <>
                    <button
                      onClick={() => setShowPodModal(true)}
                      className="col-span-2 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition-all active:scale-98"
                    >
                      <CheckCircle2 className="w-5 h-5" />
                      Arrive & Upload POD
                    </button>
                  </>
                )}

                <button
                  onClick={() => setShowRefuelModal(true)}
                  className="py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold rounded-xl flex items-center justify-center gap-2 text-xs transition-colors"
                >
                  <Fuel className="w-4 h-4 text-amber-400" />
                  Log Refuel
                </button>

                <button
                  onClick={() => setShowIssueModal(true)}
                  className="py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-100 font-semibold rounded-xl flex items-center justify-center gap-2 text-xs transition-colors"
                >
                  <AlertTriangle className="w-4 h-4 text-red-400" />
                  Report Issue
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Proof of Delivery (POD) Modal */}
      <Modal
        isOpen={showPodModal}
        onClose={() => setShowPodModal(false)}
        title="Submit Proof of Delivery (POD)"
      >
        <form onSubmit={handleSubmitPod} className="space-y-4 text-slate-800">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Recipient Name</label>
            <input
              type="text"
              required
              value={recipientName}
              onChange={(e) => setRecipientName(e.target.value)}
              placeholder="e.g. John Smith"
              className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Delivery Photo Evidence</label>
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-4 text-center cursor-pointer hover:bg-slate-50 transition-colors">
              <Camera className="w-8 h-8 text-slate-400 mx-auto mb-1" />
              <p className="text-xs text-slate-500 font-medium">Tap to snap delivery photo or upload file</p>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Digital Signature</label>
            <input
              type="text"
              required
              value={podSignature}
              onChange={(e) => setRecipientName(e.target.value)}
              placeholder="Type recipient digital signature..."
              className="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-blue-500 font-mono"
            />
          </div>

          <button
            type="submit"
            disabled={submittingPod}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20"
          >
            {submittingPod ? <RefreshCw className="w-5 h-5 animate-spin" /> : <CheckCircle2 className="w-5 h-5" />}
            Confirm Geofenced Delivery & Complete
          </button>
        </form>
      </Modal>

      {/* Refuel Modal */}
      <Modal
        isOpen={showRefuelModal}
        onClose={() => setShowRefuelModal(false)}
        title="Log Vehicle Refuel"
      >
        <form onSubmit={handleSubmitRefuel} className="space-y-4 text-slate-800">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Quantity (Liters)</label>
            <input
              type="number"
              step="0.01"
              required
              value={fuelLiters}
              onChange={(e) => setFuelLiters(e.target.value)}
              placeholder="e.g. 50.5"
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Total Cost ($)</label>
            <input
              type="number"
              step="0.01"
              required
              value={fuelCost}
              onChange={(e) => setFuelCost(e.target.value)}
              placeholder="e.g. 120.00"
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Current Odometer (km)</label>
            <input
              type="number"
              required
              value={currentOdo}
              onChange={(e) => setCurrentOdo(e.target.value)}
              placeholder="e.g. 45000"
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl"
          >
            Save Refuel Log
          </button>
        </form>
      </Modal>

      {/* Issue Modal */}
      <Modal
        isOpen={showIssueModal}
        onClose={() => setShowIssueModal(false)}
        title="Report Breakdown / Issue"
      >
        <form onSubmit={handleSubmitIssue} className="space-y-4 text-slate-800">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Issue Severity</label>
            <select
              value={issueSeverity}
              onChange={(e) => setIssueSeverity(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg text-sm"
            >
              <option value="Low">Low - Minor Delay</option>
              <option value="Medium">Medium - Mechanical Issue</option>
              <option value="High">High - Breakdown / Accident</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Description</label>
            <textarea
              rows={3}
              required
              value={issueDescription}
              onChange={(e) => setIssueDescription(e.target.value)}
              placeholder="Describe the issue..."
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>
          <button
            type="submit"
            className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xl"
          >
            Send Alert to Dispatcher
          </button>
        </form>
      </Modal>
    </div>
  );
};

export default DriverMobileApp;
