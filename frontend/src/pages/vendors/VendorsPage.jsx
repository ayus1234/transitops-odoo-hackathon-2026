import React, { useState, useEffect, useCallback } from 'react';
import vendorApi from '../../services/vendorApi';

const VendorsPage = () => {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filter & Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  // Modal & Scorecard State
  const [showModal, setShowModal] = useState(false);
  const [editingVendor, setEditingVendor] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const [scorecardVendorId, setScorecardVendorId] = useState(null);
  const [scorecardData, setScorecardData] = useState(null);
  const [loadingScorecard, setLoadingScorecard] = useState(false);

  // Form State
  const [formData, setFormData] = useState({
    vendor_code: '',
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    categories: [],
    payment_terms: 'Net 30',
    tax_id: '',
    rating: 5.0,
    notes: '',
  });

  const fetchVendors = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (categoryFilter) params.category = categoryFilter;
      if (activeFilter !== 'All') params.is_active = activeFilter === 'Active';

      const res = await vendorApi.getVendors(params);
      setVendors(res.data.data || []);
    } catch (err) {
      console.error('Failed to load vendors:', err);
      setError('Failed to load vendor directory.');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, categoryFilter, activeFilter]);

  useEffect(() => {
    fetchVendors();
  }, [fetchVendors]);

  const openCreateModal = () => {
    setEditingVendor(null);
    setFormData({
      vendor_code: `VEND-${Math.floor(100 + Math.random() * 900)}`,
      name: '',
      contact_person: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      country: '',
      categories: ['Parts'],
      payment_terms: 'Net 30',
      tax_id: '',
      rating: 5.0,
      notes: '',
    });
    setShowModal(true);
  };

  const openEditModal = (v) => {
    setEditingVendor(v);
    setFormData({
      vendor_code: v.vendor_code,
      name: v.name,
      contact_person: v.contact_person || '',
      email: v.email || '',
      phone: v.phone || '',
      address: v.address || '',
      city: v.city || '',
      state: v.state || '',
      country: v.country || '',
      categories: v.categories || [],
      payment_terms: v.payment_terms || 'Net 30',
      tax_id: v.tax_id || '',
      rating: v.rating ? parseFloat(v.rating) : 5.0,
      notes: v.notes || '',
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      if (editingVendor) {
        await vendorApi.updateVendor(editingVendor.id, formData);
      } else {
        await vendorApi.createVendor(formData);
      }
      setShowModal(false);
      fetchVendors();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to save vendor.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (v) => {
    if (!window.confirm(`Delete vendor ${v.name}?`)) return;
    try {
      await vendorApi.deleteVendor(v.id);
      fetchVendors();
    } catch (err) {
      alert('Failed to delete vendor.');
    }
  };

  const openScorecard = async (vendorId) => {
    try {
      setScorecardVendorId(vendorId);
      setLoadingScorecard(true);
      const res = await vendorApi.getVendorScorecard(vendorId);
      setScorecardData(res.data);
    } catch (err) {
      alert('Failed to fetch scorecard.');
    } finally {
      setLoadingScorecard(false);
    }
  };

  const toggleCategory = (cat) => {
    setFormData((prev) => {
      const exists = prev.categories.includes(cat);
      if (exists) return { ...prev, categories: prev.categories.filter((c) => c !== cat) };
      return { ...prev, categories: [...prev.categories, cat] };
    });
  };

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="font-bold text-headline-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-primary text-[32px]">store</span>
            Vendor & Service Provider Directory
          </h1>
          <p className="text-body-sm text-outline">Manage parts suppliers, service workshops, fuel providers, and contracts.</p>
        </div>

        <button
          onClick={openCreateModal}
          className="bg-primary text-on-primary font-bold px-4 py-2.5 rounded-lg shadow-sm hover:opacity-90 transition-all flex items-center gap-2 text-sm"
        >
          <span className="material-symbols-outlined text-[20px]">add</span>
          Add New Vendor
        </button>
      </div>

      {error && <div className="p-4 bg-error-container text-on-error-container rounded-lg font-bold">{error}</div>}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-surface border border-outline-variant p-4 rounded-xl shadow-xs">
          <p className="text-xs font-bold text-outline uppercase">Total Vendors</p>
          <p className="text-headline-sm font-bold text-on-surface mt-1">{vendors.length}</p>
        </div>
        <div className="bg-surface border border-outline-variant p-4 rounded-xl shadow-xs">
          <p className="text-xs font-bold text-outline uppercase">Active Suppliers</p>
          <p className="text-headline-sm font-bold text-secondary mt-1">
            {vendors.filter((v) => v.is_active).length}
          </p>
        </div>
        <div className="bg-surface border border-outline-variant p-4 rounded-xl shadow-xs">
          <p className="text-xs font-bold text-outline uppercase">Parts Vendors</p>
          <p className="text-headline-sm font-bold text-primary mt-1">
            {vendors.filter((v) => v.categories?.includes('Parts')).length}
          </p>
        </div>
        <div className="bg-surface border border-outline-variant p-4 rounded-xl shadow-xs">
          <p className="text-xs font-bold text-outline uppercase">Service Centers</p>
          <p className="text-headline-sm font-bold text-tertiary mt-1">
            {vendors.filter((v) => v.categories?.includes('Service')).length}
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="flex flex-wrap gap-2 items-center">
          <div className="relative w-full md:w-72">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">search</span>
            <input
              type="text"
              placeholder="Search code, name, contact..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full h-9 pl-9 pr-3 border border-outline-variant rounded-lg bg-surface text-xs text-on-surface"
            />
          </div>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="h-9 px-3 border border-outline-variant rounded-lg bg-surface text-xs font-bold text-on-surface cursor-pointer"
          >
            <option value="">All Categories</option>
            <option value="Parts">Parts</option>
            <option value="Service">Service</option>
            <option value="Fuel">Fuel</option>
            <option value="Tyres">Tyres</option>
            <option value="Insurance">Insurance</option>
          </select>
        </div>
      </div>

      {/* Vendor Table */}
      <div className="bg-surface border border-outline-variant rounded-xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-container-low text-outline font-bold uppercase border-b border-outline-variant">
              <tr>
                <th className="p-3.5">Code</th>
                <th className="p-3.5">Vendor Name</th>
                <th className="p-3.5">Contact Person</th>
                <th className="p-3.5">Categories</th>
                <th className="p-3.5">Rating</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" className="p-12 text-center text-outline">Loading vendor directory...</td></tr>
              ) : vendors.length === 0 ? (
                <tr><td colSpan="7" className="p-12 text-center text-outline">No vendors found.</td></tr>
              ) : (
                vendors.map((v) => (
                  <tr key={v.id} className="border-b border-outline-variant hover:bg-surface-container-lowest transition-colors">
                    <td className="p-3.5 font-bold font-data-tabular text-primary">{v.vendor_code}</td>
                    <td className="p-3.5 font-bold text-on-surface">{v.name}</td>
                    <td className="p-3.5 text-on-surface-variant">{v.contact_person || 'N/A'}</td>
                    <td className="p-3.5">
                      <div className="flex flex-wrap gap-1">
                        {(v.categories || []).map((cat) => (
                          <span key={cat} className="bg-surface-container px-2 py-0.5 rounded text-[10px] font-bold text-outline">
                            {cat}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="p-3.5 font-bold text-amber-600 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[16px] fill-current">star</span>
                      {v.rating ? Number(v.rating).toFixed(1) : '5.0'}
                    </td>
                    <td className="p-3.5">
                      {v.is_active ? (
                        <span className="bg-secondary-container/30 text-secondary px-2 py-0.5 rounded text-[10px] font-bold">Active</span>
                      ) : (
                        <span className="bg-error/10 text-error px-2 py-0.5 rounded text-[10px] font-bold">Inactive</span>
                      )}
                    </td>
                    <td className="p-3.5 text-right">
                      <div className="flex justify-end gap-1">
                        <button
                          onClick={() => openScorecard(v.id)}
                          className="p-1 text-primary hover:bg-primary/10 rounded"
                          title="View Scorecard"
                        >
                          <span className="material-symbols-outlined text-[18px]">analytics</span>
                        </button>
                        <button
                          onClick={() => openEditModal(v)}
                          className="p-1 text-outline hover:text-primary hover:bg-surface-container rounded"
                          title="Edit Vendor"
                        >
                          <span className="material-symbols-outlined text-[18px]">edit</span>
                        </button>
                        <button
                          onClick={() => handleDelete(v)}
                          className="p-1 text-outline hover:text-error hover:bg-error-container rounded"
                          title="Delete Vendor"
                        >
                          <span className="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Vendor Form Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl p-6 max-w-lg w-full border border-outline-variant shadow-xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-title-medium font-bold text-on-surface mb-4">
              {editingVendor ? 'Edit Vendor' : 'Add New Vendor'}
            </h3>

            <form onSubmit={handleSave} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-outline mb-1">Vendor Code *</label>
                  <input
                    type="text"
                    required
                    value={formData.vendor_code}
                    onChange={(e) => setFormData({ ...formData, vendor_code: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface font-bold"
                  />
                </div>
                <div>
                  <label className="block font-bold text-outline mb-1">Company Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. AutoParts India"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface font-bold"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-outline mb-1">Contact Person</label>
                  <input
                    type="text"
                    placeholder="Rajesh Kumar"
                    value={formData.contact_person}
                    onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
                <div>
                  <label className="block font-bold text-outline mb-1">Email</label>
                  <input
                    type="email"
                    placeholder="vendor@company.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-outline mb-1">Categories</label>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {['Parts', 'Service', 'Fuel', 'Tyres', 'Insurance', 'Other'].map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => toggleCategory(cat)}
                      className={`px-3 py-1 rounded text-[11px] font-bold border transition-colors ${
                        formData.categories.includes(cat)
                          ? 'bg-primary text-on-primary border-primary'
                          : 'bg-surface text-outline border-outline-variant'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <label className="block font-bold text-outline mb-1">Tax ID / GSTIN</label>
                  <input
                    type="text"
                    placeholder="GSTIN29ABCDE1234F1Z5"
                    value={formData.tax_id}
                    onChange={(e) => setFormData({ ...formData, tax_id: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
                <div>
                  <label className="block font-bold text-outline mb-1">Payment Terms</label>
                  <input
                    type="text"
                    placeholder="Net 30 / Advance"
                    value={formData.payment_terms}
                    onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-outline-variant rounded text-on-surface font-bold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="px-4 py-2 bg-primary text-on-primary rounded font-bold text-xs hover:opacity-90 disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save Vendor'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Vendor Scorecard Drawer / Modal */}
      {scorecardVendorId && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl p-6 max-w-md w-full border border-outline-variant shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-title-medium font-bold text-on-surface">Vendor Scorecard</h3>
              <button onClick={() => setScorecardVendorId(null)} className="p-1 text-outline">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            {loadingScorecard ? (
              <p className="p-6 text-center text-outline">Loading scorecard...</p>
            ) : scorecardData ? (
              <div className="space-y-4 text-xs">
                <div className="p-3 bg-surface-container-low rounded-lg border border-outline-variant">
                  <h4 className="font-bold text-on-surface text-sm">{scorecardData.vendor.name}</h4>
                  <p className="text-outline">{scorecardData.vendor.vendor_code}</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-surface-container-lowest border rounded text-center">
                    <p className="text-outline font-bold">Purchase Orders</p>
                    <p className="font-bold text-on-surface text-lg">{scorecardData.purchase_orders_count}</p>
                  </div>
                  <div className="p-3 bg-surface-container-lowest border rounded text-center">
                    <p className="text-outline font-bold">Total Commercial Spend</p>
                    <p className="font-bold text-primary text-lg font-data-tabular">₹{Number(scorecardData.total_spend).toLocaleString()}</p>
                  </div>
                </div>

                <div className="p-3 bg-surface-container-lowest border rounded text-center">
                  <p className="text-outline font-bold">Active Linked Contracts</p>
                  <p className="font-bold text-secondary text-lg">{scorecardData.active_contracts_count}</p>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorsPage;
