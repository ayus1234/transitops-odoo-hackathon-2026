import React, { useState, useEffect, useCallback } from 'react';
import driverApi from '../../services/driverApi';
import DocumentsPanel from '../../components/documents/DocumentsPanel';

const Driver360Modal = ({ isOpen, onClose, driverId }) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [profile, setProfile] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    if (!driverId) return;
    try {
      setLoading(true);
      setError(null);

      const [pRes, perfRes] = await Promise.all([
        driverApi.getDriver360(driverId),
        driverApi.getDriverPerformance(driverId).catch(() => ({ data: { data: null } }))
      ]);

      setProfile(pRes.data);
      setPerformance(perfRes.data.data);
    } catch (err) {
      console.error('Failed to load Driver 360:', err);
      setError('Failed to load driver profile.');
    } finally {
      setLoading(false);
    }
  }, [driverId]);

  useEffect(() => {
    if (isOpen && driverId) {
      loadData();
    }
  }, [isOpen, driverId, loadData]);

  if (!isOpen) return null;

  const driver = profile?.driver;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-3 md:p-6 overflow-y-auto">
      <div className="bg-surface rounded-2xl max-w-3xl w-full border border-outline-variant shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 md:p-6 bg-surface-container-low border-b border-outline-variant flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xl font-bold">
              {driver?.user?.full_name?.substring(0, 2).toUpperCase() || 'DR'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-headline-sm font-bold text-on-surface">
                  {driver?.user?.full_name || 'Driver 360'}
                </h2>
                <span className="bg-secondary-container/30 text-secondary px-2.5 py-0.5 rounded-full text-xs font-bold font-data-tabular">
                  {driver?.license_number}
                </span>
              </div>
              <p className="text-body-sm text-outline">
                {driver?.license_category} {driver?.license_class ? `(${driver.license_class})` : ''} • {driver?.user?.email}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-surface-container-high text-outline hover:text-on-surface transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-outline-variant bg-surface-container-lowest px-4 gap-2 text-xs md:text-sm font-bold">
          {[
            { id: 'profile', label: 'Profile & Medical', icon: 'person' },
            { id: 'scores', label: 'Performance Scorecard', icon: 'military_tech' },
            { id: 'documents', label: 'Documents', icon: 'folder_open' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 px-3 border-b-2 flex items-center gap-1.5 whitespace-nowrap transition-all ${
                activeTab === tab.id
                  ? 'border-primary text-primary font-bold'
                  : 'border-transparent text-outline hover:text-on-surface'
              }`}
            >
              <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Modal Body */}
        <div className="p-4 md:p-6 overflow-y-auto flex-1 bg-surface">
          {loading ? (
            <div className="p-12 text-center text-outline">Loading Driver 360 Profile...</div>
          ) : error ? (
            <div className="p-6 text-center text-error font-bold">{error}</div>
          ) : (
            <>
              {/* TAB 1: Profile & Medical */}
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 bg-surface-container-low rounded-lg border border-outline-variant">
                      <p className="text-[10px] text-outline font-bold uppercase">License Category</p>
                      <p className="font-bold text-on-surface text-sm mt-0.5">{driver?.license_category}</p>
                    </div>
                    <div className="p-3 bg-surface-container-low rounded-lg border border-outline-variant">
                      <p className="text-[10px] text-outline font-bold uppercase">License Class</p>
                      <p className="font-bold text-on-surface text-sm mt-0.5">{driver?.license_class || 'N/A'}</p>
                    </div>
                    <div className="p-3 bg-surface-container-low rounded-lg border border-outline-variant">
                      <p className="text-[10px] text-outline font-bold uppercase">Blood Group</p>
                      <p className="font-bold text-error text-sm mt-0.5">{driver?.blood_group || 'N/A'}</p>
                    </div>
                    <div className="p-3 bg-surface-container-low rounded-lg border border-outline-variant">
                      <p className="text-[10px] text-outline font-bold uppercase">Medical Expiry</p>
                      <p className="font-bold text-on-surface text-sm mt-0.5">{driver?.medical_fitness_expiry || 'N/A'}</p>
                    </div>
                  </div>

                  <div className="border border-outline-variant rounded-xl p-4 bg-surface-container-lowest">
                    <h4 className="font-bold text-on-surface text-sm mb-3">Licence & Compliance Info</h4>
                    <dl className="grid grid-cols-2 gap-3 text-xs">
                      <dt className="text-outline">License Issue Date:</dt>
                      <dd className="font-bold text-on-surface text-right">{driver?.license_issue_date}</dd>
                      <dt className="text-outline">License Expiry Date:</dt>
                      <dd className="font-bold text-on-surface text-right">{driver?.license_expiry_date}</dd>
                      <dt className="text-outline">Emergency Contact:</dt>
                      <dd className="font-bold text-on-surface text-right">{driver?.emergency_contact || 'N/A'}</dd>
                      <dt className="text-outline">Joined Date:</dt>
                      <dd className="font-bold text-on-surface text-right">{driver?.joined_date}</dd>
                    </dl>
                  </div>
                </div>
              )}

              {/* TAB 2: Performance Scorecard */}
              {activeTab === 'scores' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline-variant">
                      <p className="text-xs font-bold text-outline uppercase">Safety Score</p>
                      <p className="text-title-medium font-bold text-secondary mt-1">{driver?.safety_score}%</p>
                    </div>
                    <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline-variant">
                      <p className="text-xs font-bold text-outline uppercase">Efficiency Score</p>
                      <p className="text-title-medium font-bold text-primary mt-1">{driver?.efficiency_score || 100}%</p>
                    </div>
                    <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline-variant">
                      <p className="text-xs font-bold text-outline uppercase">Compliance Score</p>
                      <p className="text-title-medium font-bold text-on-surface mt-1">{driver?.compliance_score || 100}%</p>
                    </div>
                    <div className="p-3.5 bg-surface-container-low rounded-xl border border-outline-variant">
                      <p className="text-xs font-bold text-outline uppercase">Overall Score</p>
                      <p className="text-title-medium font-bold text-tertiary mt-1">{driver?.overall_score || 100}%</p>
                    </div>
                  </div>

                  <div className="p-4 border border-outline-variant rounded-xl bg-surface-container-lowest text-xs space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-outline font-bold">Total Trips Completed:</span>
                      <span className="font-bold text-on-surface text-sm font-data-tabular">{driver?.total_trips || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-outline font-bold">Current Vehicle Assignment:</span>
                      <span className="font-bold text-primary">{driver?.current_vehicle ? driver.current_vehicle.vehicle_name : 'Unassigned'}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: Documents */}
              {activeTab === 'documents' && (
                <DocumentsPanel driverId={driverId} onDocumentChange={loadData} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Driver360Modal;
