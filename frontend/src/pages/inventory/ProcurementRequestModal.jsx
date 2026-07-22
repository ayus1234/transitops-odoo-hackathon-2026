import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useToast } from '../../contexts/ToastContext';

const ProcurementRequestModal = ({ isOpen, onClose, onCreated }) => {
  const { showToast } = useToast();
  const [loading, setLoading] = useState(false);
  const [parts, setParts] = useState([]);
  
  const [formData, setFormData] = useState({
    part_id: '',
    required_quantity: 1,
    suggested_quantity: '',
    vendor: '',
    estimated_cost: '',
    priority: 'Medium'
  });

  useEffect(() => {
    if (isOpen) {
      // Fetch parts for dropdown
      api.get('/inventory/parts?page_size=100').then(res => {
        setParts(res.data.data || []);
      }).catch(err => {
        console.error('Failed to fetch parts', err);
      });
      // Reset form
      setFormData({
        part_id: '', required_quantity: 1, suggested_quantity: '', vendor: '', estimated_cost: '', priority: 'Medium'
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.part_id) {
      showToast('Please select a part', 'error');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...formData,
        suggested_quantity: formData.suggested_quantity ? parseInt(formData.suggested_quantity) : null,
        estimated_cost: formData.estimated_cost ? parseFloat(formData.estimated_cost) : null
      };
      await api.post('/procurement/create-request', payload);
      showToast('Procurement Request created successfully', 'success');
      onCreated();
      onClose();
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to create request', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="bg-surface rounded-xl shadow-lg overflow-hidden flex flex-col min-w-0 shrink-0" style={{ width: '100%', maxWidth: '500px', minWidth: '320px', maxHeight: '90vh' }}>
        <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-lowest">
          <h2 className="font-headline-sm text-headline-sm font-bold text-on-surface">New Procurement Request</h2>
          <button onClick={onClose} className="text-on-surface-variant hover:text-on-surface transition-colors p-2 -mr-2 rounded-full hover:bg-surface-container-low">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          <div>
            <label className="block text-body-sm font-bold text-on-surface mb-1">Part *</label>
            <select 
              value={formData.part_id} 
              onChange={e => setFormData({...formData, part_id: e.target.value})}
              className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
              required
            >
              <option value="">Select a part...</option>
              {parts.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.part_number})</option>
              ))}
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-body-sm font-bold text-on-surface mb-1">Required Qty *</label>
              <input type="number" min="1" required
                value={formData.required_quantity}
                onChange={e => setFormData({...formData, required_quantity: parseInt(e.target.value)})}
                className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
              />
            </div>
            <div>
              <label className="block text-body-sm font-bold text-on-surface mb-1">Suggested Qty</label>
              <input type="number" min="1"
                value={formData.suggested_quantity}
                onChange={e => setFormData({...formData, suggested_quantity: e.target.value})}
                className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-body-sm font-bold text-on-surface mb-1">Vendor</label>
              <input type="text"
                value={formData.vendor}
                onChange={e => setFormData({...formData, vendor: e.target.value})}
                className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
                placeholder="Preferred Vendor"
              />
            </div>
            <div>
              <label className="block text-body-sm font-bold text-on-surface mb-1">Est. Total Cost (₹)</label>
              <input type="number" step="0.01" min="0"
                value={formData.estimated_cost}
                onChange={e => setFormData({...formData, estimated_cost: e.target.value})}
                className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
              />
            </div>
          </div>

          <div>
            <label className="block text-body-sm font-bold text-on-surface mb-1">Priority</label>
            <select 
              value={formData.priority}
              onChange={e => setFormData({...formData, priority: e.target.value})}
              className="w-full bg-surface border border-outline-variant rounded-lg px-4 py-2 outline-none focus:border-primary transition-colors text-body-md"
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </form>
        <div className="px-6 py-4 border-t border-outline-variant bg-surface-container-lowest flex justify-end gap-3">
          <button type="button" onClick={onClose} className="px-4 py-2 text-on-surface-variant font-bold hover:bg-surface-container-low rounded-lg transition-colors">
            Cancel
          </button>
          <button onClick={handleSubmit} disabled={loading} className="px-4 py-2 bg-primary text-on-primary font-bold rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-2 disabled:opacity-50">
            {loading ? <span className="material-symbols-outlined animate-spin text-[20px]">sync</span> : <span className="material-symbols-outlined text-[20px]">add</span>}
            Create Request
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcurementRequestModal;
