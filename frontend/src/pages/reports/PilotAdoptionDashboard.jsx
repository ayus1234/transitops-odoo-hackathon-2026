import React, { useState, useEffect } from 'react';
import { 
  Building2, TrendingUp, Radio, CheckCircle2, Eye, CreditCard, 
  Sparkles, RefreshCw, ShieldCheck, ArrowUpRight, BarChart3
} from 'lucide-react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const PilotAdoptionDashboard = () => {
  const { showError } = useToast();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchPilotMetrics();
  }, []);

  const fetchPilotMetrics = async () => {
    setLoading(true);
    try {
      const response = await api.get('/analytics/pilot-metrics');
      setMetrics(response.data);
    } catch (err) {
      console.error("Error fetching pilot adoption metrics:", err);
      showError("Failed to load pilot adoption metrics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
        <p className="text-sm">Calculating commercial pilot fleet adoption metrics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-6 rounded-2xl border border-slate-800 text-white shadow-2xl flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl border border-emerald-500/30">
            <ShieldCheck className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-extrabold text-white">Commercial Pilot Adoption Control Center</h1>
              <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold rounded-full">
                {metrics?.readiness_verdict}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Data-driven operational validation across active pilot fleets, GPS density, driver POD usage, customer tracking, and trial conversion rates.
            </p>
          </div>
        </div>
        <button
          onClick={fetchPilotMetrics}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Metrics
        </button>
      </div>

      {/* 6 Explicit Commercial Adoption KPIs Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* KPI 1: Active Pilot Fleets / Tenants */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">1. Active Pilot Fleets</span>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
              <Building2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{metrics?.active_pilot_fleets}</span>
            <span className="text-xs text-emerald-600 font-semibold">Live Pilot Tenants</span>
          </div>
          <p className="text-xs text-slate-500">Active commercial fleet accounts generating operational data.</p>
        </div>

        {/* KPI 2: Dispatches per Fleet per Week */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">2. Dispatches / Fleet / Wk</span>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{metrics?.dispatches_per_fleet_per_week}</span>
            <span className="text-xs text-indigo-600 font-semibold">Trips / Wk</span>
          </div>
          <p className="text-xs text-slate-500">Average weekly dispatch execution volume per pilot customer.</p>
        </div>

        {/* KPI 3: Telemetry Pings per Vehicle per Day */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">3. Telemetry Pings / Veh / Day</span>
            <div className="p-2 bg-emerald-50 text-emerald-600 rounded-xl">
              <Radio className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{metrics?.telemetry_pings_per_vehicle_per_day}</span>
            <span className="text-xs text-emerald-600 font-semibold">GPS Pings / Day</span>
          </div>
          <p className="text-xs text-slate-500">IoT location & OBD-II ping density from Geotab, Teltonika & Traccar.</p>
        </div>

        {/* KPI 4: POD Submissions Completed */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">4. POD Submissions Completed</span>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{metrics?.pod_submissions_completed}</span>
            <span className="text-xs text-amber-600 font-semibold">Mobile PODs Uploaded</span>
          </div>
          <p className="text-xs text-slate-500">Driver mobile app geofenced photo & signature delivery verifications.</p>
        </div>

        {/* KPI 5: Tracking Portal Views per Customer */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">5. Tracking Views / Customer</span>
            <div className="p-2 bg-purple-50 text-purple-600 rounded-xl">
              <Eye className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-slate-900">{metrics?.tracking_views_per_customer}</span>
            <span className="text-xs text-purple-600 font-semibold">Views / Order</span>
          </div>
          <p className="text-xs text-slate-500">Shipper & customer engagements on public live tracking URLs.</p>
        </div>

        {/* KPI 6: Overall Scale Readiness */}
        <div className="bg-slate-900 p-5 rounded-2xl border border-slate-800 text-white shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">6. Scaling Readiness Score</span>
            <div className="p-2 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
              <Sparkles className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{metrics?.readiness_score_percent}%</span>
            <span className="text-xs text-emerald-400 font-semibold">Readiness Index</span>
          </div>
          <p className="text-xs text-slate-400">Grounded operational proof that TransitOps is ready for 50+ fleets.</p>
        </div>
      </div>

      {/* Trial-to-Paid Subscription Conversion Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Trial-to-Paid Conversion by Subscription Tier</h3>
            <p className="text-xs text-slate-500">Breakdown of pilot fleet trial accounts converting to paid monthly SaaS plans</p>
          </div>
          <span className="px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-bold rounded-full border border-emerald-200 flex items-center gap-1.5">
            <CreditCard className="w-3.5 h-3.5" />
            Stripe & Razorpay Active
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-bold uppercase tracking-wider border-y border-slate-200">
              <tr>
                <th className="py-3 px-4">Plan Tier</th>
                <th className="py-3 px-4">Pilot Trials Started</th>
                <th className="py-3 px-4">Paid Conversions</th>
                <th className="py-3 px-4">Conversion Rate</th>
                <th className="py-3 px-4">Generated Monthly MRR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-800">
              {metrics?.trial_to_paid_conversions?.map((tier, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900">{tier.plan}</td>
                  <td className="py-3.5 px-4">{tier.trial_count} Fleets</td>
                  <td className="py-3.5 px-4 text-emerald-600 font-bold">{tier.converted_count} Fleets</td>
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-0.5 bg-blue-50 text-blue-700 font-bold rounded-full border border-blue-200">
                      {tier.conversion_rate}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-900">${tier.mrr} / mo</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PilotAdoptionDashboard;
