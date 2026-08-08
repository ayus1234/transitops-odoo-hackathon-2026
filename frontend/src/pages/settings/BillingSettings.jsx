import React, { useState, useEffect } from 'react';
import { 
  CreditCard, ShieldCheck, CheckCircle2, Zap, Building2, 
  ArrowUpRight, ExternalLink, RefreshCw, AlertCircle, Sparkles
} from 'lucide-react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const BillingSettings = () => {
  const { showSuccess, showError } = useToast();
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState([]);
  const [status, setStatus] = useState(null);
  const [selectedGateway, setSelectedGateway] = useState('stripe');
  const [upgradingPlan, setUpgradingPlan] = useState(null);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    setLoading(true);
    try {
      const [plansRes, statusRes] = await Promise.all([
        api.get('/billing/plans'),
        api.get('/billing/status')
      ]);
      setPlans(plansRes.data);
      setStatus(statusRes.data);
    } catch (err) {
      console.error("Error fetching billing data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId) => {
    setUpgradingPlan(planId);
    try {
      const res = await api.post('/billing/create-checkout-session', {
        plan_id: planId,
        gateway: selectedGateway,
        success_url: window.location.href,
        cancel_url: window.location.href
      });
      showSuccess(`Redirecting to ${selectedGateway.toUpperCase()} secure checkout...`);
      setTimeout(() => {
        window.open(res.data.checkout_url, '_blank');
      }, 1000);
    } catch (err) {
      showError("Failed to initiate checkout session");
    } finally {
      setUpgradingPlan(null);
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500" />
        <p className="text-sm">Loading SaaS subscription & billing details...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Subscription Banner */}
      {status && (
        <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 p-6 rounded-2xl border border-slate-800 text-white shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
                <Zap className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">Current Active Plan</span>
                <h2 className="text-2xl font-bold text-white">{status.current_plan}</h2>
                <p className="text-xs text-slate-400">Status: <span className="text-emerald-400 font-semibold">{status.status}</span> • Renews on {new Date(status.renews_at).toLocaleDateString()}</p>
              </div>
            </div>
            <div className="bg-slate-800/80 px-4 py-2 rounded-xl border border-slate-700 text-right">
              <p className="text-xs text-slate-400">Fleet Vehicle Limit</p>
              <p className="text-lg font-bold text-white">{status.vehicles_used} / {status.vehicle_limit} <span className="text-xs text-slate-400 font-normal">Vehicles</span></p>
            </div>
          </div>

          {/* Usage Bar */}
          <div className="w-full bg-slate-700/60 h-2 rounded-full overflow-hidden">
            <div 
              className="bg-blue-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${(status.vehicles_used / status.vehicle_limit) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Payment Gateway Toggle */}
      <div className="flex items-center justify-between bg-slate-100 p-4 rounded-xl border border-slate-200">
        <div>
          <h3 className="text-sm font-bold text-slate-800">Select Payment Gateway</h3>
          <p className="text-xs text-slate-500">Choose your preferred payment processor for monthly subscription billing</p>
        </div>
        <div className="flex items-center gap-2 bg-white p-1 rounded-lg border border-slate-300">
          <button
            onClick={() => setSelectedGateway('stripe')}
            className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all ${
              selectedGateway === 'stripe' ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Stripe (Global)
          </button>
          <button
            onClick={() => setSelectedGateway('razorpay')}
            className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all ${
              selectedGateway === 'razorpay' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Razorpay (India / Asia)
          </button>
        </div>
      </div>

      {/* Pricing Cards Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrent = status?.current_plan === plan.name;
          return (
            <div 
              key={plan.id}
              className={`bg-white rounded-2xl p-6 border transition-all flex flex-col justify-between relative ${
                plan.is_popular 
                  ? 'border-blue-500 shadow-xl ring-2 ring-blue-500/20' 
                  : 'border-slate-200 shadow-sm hover:shadow-md'
              }`}
            >
              {plan.is_popular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-blue-600 text-white text-[10px] font-extrabold uppercase tracking-wider rounded-full shadow-sm flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  Most Popular
                </span>
              )}

              <div className="space-y-4">
                <div>
                  <h3 className="font-bold text-lg text-slate-900">{plan.name}</h3>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-3xl font-extrabold text-slate-900">${plan.price_monthly}</span>
                    <span className="text-xs text-slate-500 font-medium">/ month</span>
                  </div>
                </div>

                <ul className="space-y-2.5 pt-2 border-t border-slate-100 text-xs text-slate-600">
                  {plan.features.map((feat, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-6">
                {isCurrent ? (
                  <button
                    disabled
                    className="w-full py-2.5 bg-slate-100 text-slate-500 font-bold rounded-xl text-xs border border-slate-200 cursor-default"
                  >
                    Current Plan
                  </button>
                ) : (
                  <button
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={upgradingPlan === plan.id}
                    className={`w-full py-2.5 font-bold rounded-xl text-xs flex items-center justify-center gap-2 transition-all ${
                      plan.is_popular 
                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20' 
                        : 'bg-slate-900 hover:bg-slate-800 text-white'
                    }`}
                  >
                    {upgradingPlan === plan.id ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        Upgrade via {selectedGateway === 'stripe' ? 'Stripe' : 'Razorpay'}
                        <ArrowUpRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BillingSettings;
