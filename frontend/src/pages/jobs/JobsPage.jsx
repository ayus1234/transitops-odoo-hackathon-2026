import React, { useState, useEffect } from 'react';
import { 
  Package, Search, Plus, Filter, AlertCircle, Clock, MapPin, 
  ChevronRight, ArrowRight, Truck, CheckCircle, XCircle, RefreshCw 
} from 'lucide-react';
import { jobApi } from '../../services/jobApi';
import { useToast } from '../../contexts/ToastContext';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  
  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_contact: '',
    pickup_address: '',
    delivery_address: '',
    cargo_description: '',
    cargo_weight_kg: '',
    cargo_volume_cbm: '',
    priority: 'Normal',
    special_instructions: ''
  });

  const { showToast } = useToast();

  useEffect(() => {
    fetchJobs();
  }, [page, statusFilter, priorityFilter]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const data = await jobApi.getJobs({
        page,
        page_size: 15,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        search: search || undefined
      });
      setJobs(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      showToast(err.response?.data?.error?.message || 'Failed to load jobs', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        ...formData,
        cargo_weight_kg: formData.cargo_weight_kg ? parseFloat(formData.cargo_weight_kg) : null,
        cargo_volume_cbm: formData.cargo_volume_cbm ? parseFloat(formData.cargo_volume_cbm) : null
      };
      await jobApi.createJob(payload);
      showToast('Customer shipping order created successfully', 'success');
      setIsModalOpen(false);
      setFormData({
        customer_name: '',
        customer_contact: '',
        pickup_address: '',
        delivery_address: '',
        cargo_description: '',
        cargo_weight_kg: '',
        cargo_volume_cbm: '',
        priority: 'Normal',
        special_instructions: ''
      });
      fetchJobs();
    } catch (err) {
      showToast(err.response?.data?.error?.message || 'Failed to create job', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'Urgent':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'High':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'Low':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Delivered':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'In Transit':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-400/20';
      case 'Assigned':
        return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
      case 'Cancelled':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
            <Package className="w-7 h-7 text-indigo-400" />
            Jobs & Customer Orders
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage commercial freight bookings, customer shipping requests, and dispatch readiness
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-600/20 transition-all text-sm"
        >
          <Plus className="w-4 h-4" />
          Create Shipping Order
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search job #, customer, address..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-900/60 border border-slate-700 rounded-xl text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto overflow-x-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900/60 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="Assigned">Assigned</option>
            <option value="In Transit">In Transit</option>
            <option value="Delivered">Delivered</option>
            <option value="Cancelled">Cancelled</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-slate-900/60 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Priorities</option>
            <option value="Urgent">Urgent</option>
            <option value="High">High</option>
            <option value="Normal">Normal</option>
            <option value="Low">Low</option>
          </select>

          <button
            onClick={fetchJobs}
            className="p-2 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Jobs Data Table */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/60 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-700/80">
              <tr>
                <th className="px-6 py-4">Job Details</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Route & Cargo</th>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    Loading customer shipping orders...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400">
                    No shipping orders found matching criteria.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-100">{job.job_number}</div>
                      <div className="text-xs text-slate-400 truncate max-w-xs">{job.special_instructions || 'No special notes'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-200">{job.customer_name}</div>
                      <div className="text-xs text-slate-400">{job.customer_contact || 'No contact info'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5 text-xs text-slate-300">
                        <MapPin className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <span className="truncate max-w-[140px]">{job.pickup_address}</span>
                        <ArrowRight className="w-3 h-3 text-slate-500 shrink-0" />
                        <span className="truncate max-w-[140px]">{job.delivery_address}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {job.cargo_description || 'General Cargo'} 
                        {job.cargo_weight_kg ? ` • ${job.cargo_weight_kg} kg` : ''}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getPriorityBadge(job.priority)}`}>
                        {job.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(job.status)}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl">
            <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-100">Create Customer Shipping Order</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Customer Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                    placeholder="e.g. Acme Freight Ltd"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Customer Contact</label>
                  <input
                    type="text"
                    value={formData.customer_contact}
                    onChange={(e) => setFormData({ ...formData, customer_contact: e.target.value })}
                    placeholder="Phone or email"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Pickup Address *</label>
                <input
                  type="text"
                  required
                  value={formData.pickup_address}
                  onChange={(e) => setFormData({ ...formData, pickup_address: e.target.value })}
                  placeholder="Full pickup location address"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Delivery Address *</label>
                <input
                  type="text"
                  required
                  value={formData.delivery_address}
                  onChange={(e) => setFormData({ ...formData, delivery_address: e.target.value })}
                  placeholder="Full destination delivery address"
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Cargo Description</label>
                  <input
                    type="text"
                    value={formData.cargo_description}
                    onChange={(e) => setFormData({ ...formData, cargo_description: e.target.value })}
                    placeholder="Goods / Materials"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Cargo Weight (kg)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.cargo_weight_kg}
                    onChange={(e) => setFormData({ ...formData, cargo_weight_kg: e.target.value })}
                    placeholder="e.g. 15000"
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="Low">Low</option>
                    <option value="Normal">Normal</option>
                    <option value="High">High</option>
                    <option value="Urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Special Instructions</label>
                <textarea
                  rows="2"
                  value={formData.special_instructions}
                  onChange={(e) => setFormData({ ...formData, special_instructions: e.target.value })}
                  placeholder="Handling instructions, temperature constraints, notes..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-xl text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm font-medium transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50"
                >
                  {isSubmitting ? 'Creating...' : 'Create Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
