import React, { useState, useEffect, useCallback } from 'react';
import documentApi from '../../services/documentApi';

const DocumentsPanel = ({ vehicleId, driverId, maintenanceId, vendorId, onDocumentChange }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  // Form modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    document_type: 'insurance',
    document_number: '',
    title: '',
    issue_date: '',
    expiry_date: '',
    issuer: '',
    notes: '',
  });
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (vehicleId) params.vehicle_id = vehicleId;
      if (driverId) params.driver_id = driverId;
      if (maintenanceId) params.maintenance_id = maintenanceId;
      if (vendorId) params.vendor_id = vendorId;

      const res = await documentApi.getDocuments(params);
      setDocuments(res.data.data || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents.');
    } finally {
      setLoading(false);
    }
  }, [vehicleId, driverId, maintenanceId, vendorId]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleCreateDocument = async (e) => {
    e.preventDefault();
    try {
      setIsUploading(true);
      let fileMeta = {};

      if (selectedFile) {
        const fileData = new FormData();
        fileData.append('file', selectedFile);
        const uploadRes = await documentApi.uploadFile(fileData);
        fileMeta = {
          file_path: uploadRes.data.file_path,
          file_name: uploadRes.data.file_name,
          file_size_bytes: uploadRes.data.file_size_bytes,
          mime_type: uploadRes.data.mime_type,
        };
      }

      const payload = {
        ...formData,
        ...fileMeta,
        vehicle_id: vehicleId || null,
        driver_id: driverId || null,
        maintenance_id: maintenanceId || null,
        vendor_id: vendorId || null,
      };

      await documentApi.createDocument(payload);
      setShowAddModal(false);
      setFormData({
        document_type: 'insurance',
        document_number: '',
        title: '',
        issue_date: '',
        expiry_date: '',
        issuer: '',
        notes: '',
      });
      setSelectedFile(null);
      fetchDocuments();
      if (onDocumentChange) onDocumentChange();
    } catch (err) {
      alert(err.response?.data?.error?.message || 'Failed to save document.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleVerify = async (docId, state) => {
    try {
      await documentApi.verifyDocument(docId, {
        verification_state: state,
        notes: `Marked as ${state} by manager.`
      });
      fetchDocuments();
      if (onDocumentChange) onDocumentChange();
    } catch (err) {
      alert('Failed to update verification state.');
    }
  };

  const handleDelete = async (docId) => {
    if (!window.confirm('Delete this document?')) return;
    try {
      await documentApi.deleteDocument(docId);
      fetchDocuments();
      if (onDocumentChange) onDocumentChange();
    } catch (err) {
      alert('Failed to delete document.');
    }
  };

  const getStatusBadge = (doc) => {
    if (doc.status === 'Expired' || doc.is_expired) {
      return (
        <span className="bg-error/10 text-error px-2 py-0.5 rounded text-xs font-bold inline-flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-error"></span> Expired
        </span>
      );
    }
    return (
      <span className="bg-secondary-container/30 text-secondary px-2 py-0.5 rounded text-xs font-bold inline-flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-secondary"></span> Active
      </span>
    );
  };

  const getVerificationBadge = (state) => {
    if (state === 'Verified') {
      return <span className="text-xs font-bold text-secondary bg-secondary/10 px-2 py-0.5 rounded">Verified</span>;
    }
    if (state === 'Rejected') {
      return <span className="text-xs font-bold text-error bg-error/10 px-2 py-0.5 rounded">Rejected</span>;
    }
    return <span className="text-xs font-bold text-outline bg-surface-container-high px-2 py-0.5 rounded">Unverified</span>;
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-on-surface text-title-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[20px]">folder_open</span>
          Linked Documents ({documents.length})
        </h3>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary text-on-primary text-xs font-bold px-3 py-1.5 rounded hover:opacity-90 transition-all flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-[16px]">upload_file</span>
          Upload Document
        </button>
      </div>

      {error && <p className="text-xs text-error">{error}</p>}

      {/* Document cards */}
      {loading ? (
        <div className="p-8 text-center text-outline">Loading documents...</div>
      ) : documents.length === 0 ? (
        <div className="p-6 text-center border border-dashed border-outline-variant rounded-lg bg-surface-container-lowest text-outline text-sm">
          No documents uploaded yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {documents.map((doc) => (
            <div key={doc.id} className="border border-outline-variant rounded-lg p-3 bg-surface hover:shadow-sm transition-all flex flex-col justify-between gap-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-outline bg-surface-container px-2 py-0.5 rounded">
                      {doc.document_type}
                    </span>
                    {getStatusBadge(doc)}
                    {getVerificationBadge(doc.verification_state)}
                  </div>
                  <h4 className="font-bold text-on-surface text-sm">{doc.title}</h4>
                  {doc.document_number && (
                    <p className="text-xs text-outline font-data-tabular">No: {doc.document_number}</p>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="text-outline hover:text-error p-1 rounded transition-colors"
                  title="Delete Document"
                >
                  <span className="material-symbols-outlined text-[18px]">delete</span>
                </button>
              </div>

              <div className="text-xs text-on-surface-variant flex flex-wrap gap-x-4 gap-y-1 border-t border-outline-variant/50 pt-2">
                {doc.issuer && <span>Issuer: <b>{doc.issuer}</b></span>}
                {doc.expiry_date && (
                  <span>
                    Expiry: <b className={doc.is_expired ? 'text-error' : ''}>{doc.expiry_date}</b>
                    {doc.days_until_expiry !== null && !doc.is_expired && (
                      <span className="text-outline ml-1">({doc.days_until_expiry}d left)</span>
                    )}
                  </span>
                )}
                {doc.file_name && <span className="truncate max-w-[150px]">File: <b>{doc.file_name}</b></span>}
              </div>

              {/* Action bar */}
              <div className="flex items-center justify-between border-t border-outline-variant/30 pt-2 text-xs">
                <div className="flex items-center gap-1">
                  {doc.verification_state !== 'Verified' && (
                    <button
                      onClick={() => handleVerify(doc.id, 'Verified')}
                      className="text-secondary hover:underline font-bold"
                    >
                      Approve
                    </button>
                  )}
                  {doc.verification_state !== 'Rejected' && (
                    <button
                      onClick={() => handleVerify(doc.id, 'Rejected')}
                      className="text-error hover:underline font-bold ml-2"
                    >
                      Reject
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Document Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl p-6 max-w-md w-full border border-outline-variant shadow-xl">
            <h3 className="text-title-medium font-bold text-on-surface mb-4">Upload Document</h3>
            <form onSubmit={handleCreateDocument} className="flex flex-col gap-3 text-sm">
              <div>
                <label className="block font-bold text-outline text-xs mb-1">Document Type *</label>
                <select
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                >
                  <option value="insurance">Insurance</option>
                  <option value="registration">Registration</option>
                  <option value="fitness">Fitness Certificate</option>
                  <option value="pollution">Pollution Under Control</option>
                  <option value="permit">Route Permit</option>
                  <option value="licence">Licence</option>
                  <option value="warranty">Warranty</option>
                  <option value="lease_contract">Lease Contract</option>
                  <option value="service_agreement">Service Agreement</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-outline text-xs mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Comprehensive Policy 2026"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold text-outline text-xs mb-1">Doc Number</label>
                  <input
                    type="text"
                    placeholder="POL-123456"
                    value={formData.document_number}
                    onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
                <div>
                  <label className="block font-bold text-outline text-xs mb-1">Issuer</label>
                  <input
                    type="text"
                    placeholder="RTO / Insurance Co"
                    value={formData.issuer}
                    onChange={(e) => setFormData({ ...formData, issuer: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-bold text-outline text-xs mb-1">Issue Date</label>
                  <input
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
                <div>
                  <label className="block font-bold text-outline text-xs mb-1">Expiry Date</label>
                  <input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    className="w-full h-9 px-3 border border-outline-variant rounded bg-surface text-on-surface"
                  />
                </div>
              </div>

              <div>
                <label className="block font-bold text-outline text-xs mb-1">File Attachment</label>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                  className="w-full text-xs text-outline"
                />
              </div>

              <div className="flex justify-end gap-2 mt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-1.5 border border-outline-variant rounded text-on-surface font-bold text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading}
                  className="px-4 py-1.5 bg-primary text-on-primary rounded font-bold text-xs hover:opacity-90 disabled:opacity-50"
                >
                  {isUploading ? 'Uploading...' : 'Save Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentsPanel;
