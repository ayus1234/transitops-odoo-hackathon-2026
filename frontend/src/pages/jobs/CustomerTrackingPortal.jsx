import React, { useState } from 'react';
import { 
  Package, Search, MapPin, Truck, Clock, CheckCircle2, 
  AlertCircle, ShieldCheck, ArrowRight, PhoneCall, Navigation, FileCheck
} from 'lucide-react';
import api from '../../services/api';

const CustomerTrackingPortal = () => {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [shipmentData, setShipmentData] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!trackingNumber.trim()) return;
    setLoading(true);
    setError('');
    setShipmentData(null);

    try {
      const response = await api.get(`/jobs/track/${encodeURIComponent(trackingNumber.trim())}`);
      setShipmentData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || `No shipment found matching "${trackingNumber}"`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between">
      {/* Top Portal Header */}
      <header className="bg-slate-800/90 border-b border-slate-800 px-6 py-4 sticky top-0 z-50 backdrop-blur-md">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-600 rounded-xl text-white shadow-lg shadow-blue-600/30">
              <Package className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-white leading-tight">TransitOps Express</h1>
              <p className="text-xs text-slate-400">Live Customer Shipment Tracking</p>
            </div>
          </div>
          <a
            href="/login"
            className="text-xs px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold rounded-lg transition-colors"
          >
            Portal Login
          </a>
        </div>
      </header>

      {/* Main Search & Tracking Content */}
      <main className="max-w-4xl mx-auto w-full px-4 py-8 flex-1 space-y-8">
        {/* Search Hero Box */}
        <div className="text-center space-y-4 max-w-xl mx-auto">
          <span className="px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-semibold rounded-full">
            Real-Time GPS Tracking
          </span>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">Track Your Shipment Status</h2>
          <p className="text-sm text-slate-400">
            Enter your order number or tracking ID below for live GPS location, route progress, and delivery verification.
          </p>

          <form onSubmit={handleSearch} className="flex items-center gap-2 pt-2">
            <div className="relative flex-1">
              <Search className="w-5 h-5 absolute left-3 top-3.5 text-slate-400" />
              <input
                type="text"
                required
                value={trackingNumber}
                onChange={(e) => setTrackingNumber(e.target.value)}
                placeholder="Enter Job # (e.g. JOB-2026-001)"
                className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl flex items-center gap-2 shadow-lg shadow-blue-600/30 transition-all active:scale-95 text-sm"
            >
              {loading ? 'Searching...' : 'Track'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center justify-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Shipment Details Result Card */}
        {shipmentData && (
          <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-2xl space-y-6">
            {/* Header info */}
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-700 pb-4">
              <div>
                <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">Shipment Details</span>
                <h3 className="text-2xl font-bold text-white">{shipmentData.job_number}</h3>
                <p className="text-xs text-slate-400 mt-1">Customer: <span className="text-white font-semibold">{shipmentData.customer_name}</span></p>
              </div>
              <span className={`px-4 py-1.5 text-xs font-bold rounded-full border ${
                shipmentData.status === 'Delivered' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' :
                shipmentData.status === 'In Transit' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' :
                'bg-amber-500/20 text-amber-400 border-amber-500/30'
              }`}>
                {shipmentData.status}
              </span>
            </div>

            {/* Tracking Progress Bar */}
            <div className="py-4">
              <div className="grid grid-cols-4 gap-2 text-center text-xs font-semibold mb-2">
                <span className="text-emerald-400">Order Placed</span>
                <span className={shipmentData.status !== 'Draft' ? 'text-emerald-400' : 'text-slate-500'}>Assigned</span>
                <span className={shipmentData.status === 'In Transit' || shipmentData.status === 'Delivered' ? 'text-emerald-400' : 'text-slate-500'}>In Transit</span>
                <span className={shipmentData.status === 'Delivered' ? 'text-emerald-400' : 'text-slate-500'}>Delivered</span>
              </div>
              <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden flex">
                <div className={`h-full bg-emerald-500 transition-all duration-500 ${
                  shipmentData.status === 'Delivered' ? 'w-full' :
                  shipmentData.status === 'In Transit' ? 'w-3/4' :
                  shipmentData.status === 'Assigned' ? 'w-1/2' : 'w-1/4'
                }`}></div>
              </div>
            </div>

            {/* Route Addresses */}
            <div className="grid md:grid-cols-2 gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-700/50">
              <div className="flex gap-3">
                <MapPin className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-400">Pickup Location</p>
                  <p className="text-sm font-semibold text-white">{shipmentData.source_address}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <MapPin className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-400">Delivery Destination</p>
                  <p className="text-sm font-semibold text-white">{shipmentData.destination_address}</p>
                </div>
              </div>
            </div>

            {/* Vehicle & Driver Card */}
            {shipmentData.vehicle && (
              <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-700/40 flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <Truck className="w-6 h-6 text-blue-400" />
                  <div>
                    <p className="text-xs text-slate-400">Transport Vehicle</p>
                    <p className="text-sm font-bold text-white">{shipmentData.vehicle.name} ({shipmentData.vehicle.registration_number})</p>
                  </div>
                </div>
                {shipmentData.driver && (
                  <div className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
                    <PhoneCall className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Driver Contact: <strong className="text-white">{shipmentData.driver.first_name} ({shipmentData.driver.phone_number || 'En route'})</strong></span>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 p-4 text-center text-xs text-slate-500">
        © 2026 TransitOps ERP. All rights reserved. Secure GPS Customer Tracking Portal.
      </footer>
    </div>
  );
};

export default CustomerTrackingPortal;
