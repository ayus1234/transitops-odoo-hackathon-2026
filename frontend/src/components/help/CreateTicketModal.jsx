import React, { useState } from 'react';
import Modal from '../ui/Modal';
import { helpApi } from '../../services/helpApi';
import { useToast } from '../../contexts/ToastContext';

const CreateTicketModal = ({ isOpen, onClose, onCreated }) => {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    module_name: 'Dashboard',
    priority: 'Medium',
    description: '',
    attachments: []
  });
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const CATEGORIES = [
    'Technical Issue',
    'Account & Access',
    'Billing',
    'Feature Request',
    'General Inquiry',
    'Other'
  ];

  const MODULES = [
    'Dashboard',
    'Vehicles',
    'Drivers',
    'Trips',
    'Maintenance',
    'Fuel',
    'Expenses',
    'Reports',
    'Settings',
    'Notifications',
    'Quick Actions',
    'Help Center',
    'Other'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.category || !formData.description.trim()) {
      showToast('Please fill out all required fields.', 'error');
      return;
    }

    try {
      setIsSubmitting(true);
      
      // Upload files first if any
      const uploadedUrls = [];
      if (selectedFiles.length > 0) {
        showToast('Uploading attachments...', 'info');
        for (const file of selectedFiles) {
          try {
            const uploadRes = await helpApi.uploadAttachment(file);
            if (uploadRes.data?.success && uploadRes.data?.data?.url) {
              uploadedUrls.push(uploadRes.data.data.url);
            }
          } catch (err) {
            console.error('Failed to upload file', file.name, err);
            showToast(`Failed to upload ${file.name}`, 'error');
          }
        }
      }
      
      // Submit ticket with attachment URLs
      const ticketPayload = { ...formData, attachments: uploadedUrls };
      const res = await helpApi.createTicket(ticketPayload);
      
      if (res.data?.success) {
        showToast(`Ticket created successfully: ${res.data.data.ticket_number}`, 'success');
        onClose();
        // Reset form
        setFormData({
          title: '',
          category: '',
          module_name: 'Dashboard',
          priority: 'Medium',
          description: '',
          attachments: []
        });
        setSelectedFiles([]);
        if (onCreated) onCreated(res.data.data);
      }
    } catch (error) {
      console.error("Failed to create ticket", error);
      showToast('Failed to submit ticket. Please try again.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Submit Support Ticket" maxWidth="min-w-[320px] sm:min-w-[600px] max-w-2xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-on-surface mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="Briefly describe the issue"
            disabled={isSubmitting}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-on-surface mb-1">
              Category *
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={isSubmitting}
            >
              <option value="" disabled>Select category...</option>
              {CATEGORIES.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="module_name" className="block text-sm font-medium text-on-surface mb-1">
              Module *
            </label>
            <select
              id="module_name"
              name="module_name"
              value={formData.module_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={isSubmitting}
            >
              {MODULES.map(mod => (
                <option key={mod} value={mod}>{mod}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-on-surface mb-1">
              Priority *
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              disabled={isSubmitting}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-on-surface mb-1">
            Description *
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={5}
            className="w-full px-3 py-2 border border-outline-variant rounded-md bg-surface text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            placeholder="Please provide as much detail as possible..."
            disabled={isSubmitting}
          />
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-on-surface">
            Attachments
          </label>
          <div className="p-4 border-2 border-dashed border-outline-variant rounded-xl bg-surface-container-lowest text-center hover:bg-surface-container-low transition-colors cursor-pointer relative">
            <input 
              type="file" 
              multiple 
              onChange={(e) => setSelectedFiles(Array.from(e.target.files))}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isSubmitting}
            />
            <span className="material-symbols-outlined text-outline text-3xl mb-1">upload_file</span>
            <p className="text-sm text-on-surface-variant">Drag and drop files here, or click to select</p>
            <p className="text-xs text-outline mt-1">Max 5MB per file. PNG, JPG, PDF.</p>
          </div>
          
          {selectedFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-2">
              {selectedFiles.map((f, i) => (
                <div key={i} className="flex items-center gap-1 bg-surface-container px-3 py-1 rounded-full text-xs font-medium text-on-surface-variant border border-outline-variant">
                  <span className="material-symbols-outlined text-[14px]">description</span>
                  <span className="truncate max-w-[120px]">{f.name}</span>
                  <button 
                    type="button" 
                    onClick={() => setSelectedFiles(prev => prev.filter((_, idx) => idx !== i))}
                    className="ml-1 hover:text-error transition-colors"
                  >
                    <span className="material-symbols-outlined text-[14px]">close</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-surface-container-high text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 bg-primary text-on-primary font-bold rounded hover:opacity-90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="flex items-center gap-2">
                <span className="material-symbols-outlined animate-spin text-sm">refresh</span>
                Submitting...
              </span>
            ) : (
              'Submit Ticket'
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateTicketModal;
