import React from 'react';
import Modal from '../../components/ui/Modal';

const PurchaseOrderTrackingModal = ({ isOpen, onClose, po }) => {
  if (!po) return null;

  const statuses = ["Processing", "Packed", "Dispatched", "In Transit", "Delivered"];
  const currentIndex = statuses.indexOf(po.shipment_status) !== -1 ? statuses.indexOf(po.shipment_status) : (po.shipment_status === 'Ordered' ? 0 : -1);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Track Shipment">
      <div className="p-md space-y-lg">
        
        <div className="flex justify-between items-center">
          <div>
            <p className="text-label-caps text-on-surface-variant">Tracking Number</p>
            <h3 className="font-title-lg text-title-lg font-bold text-on-surface">{po.tracking_id || 'Pending Assignment'}</h3>
          </div>
          <div className="text-right">
            <p className="text-label-caps text-on-surface-variant">Carrier</p>
            <h3 className="font-title-md text-title-md font-bold text-secondary">TransitLogistics</h3>
          </div>
        </div>

        <div className="relative pt-8 pb-4">
          <div className="absolute top-1/2 left-0 w-full h-1 bg-outline-variant -translate-y-1/2 rounded-full z-0"></div>
          
          <div className="absolute top-1/2 left-0 h-1 bg-primary -translate-y-1/2 rounded-full z-0 transition-all duration-500" 
               style={{ width: currentIndex >= 0 ? `${(currentIndex / (statuses.length - 1)) * 100}%` : '0%' }}></div>

          <div className="relative z-10 flex justify-between items-center w-full">
            {statuses.map((status, index) => {
              const isCompleted = index <= currentIndex;
              const isCurrent = index === currentIndex;
              
              return (
                <div key={status} className="flex flex-col items-center gap-2 w-12">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${isCompleted ? 'bg-primary text-on-primary ring-4 ring-primary-container' : 'bg-surface border-2 border-outline-variant text-outline-variant'}`}>
                    {isCompleted ? <span className="material-symbols-outlined text-[14px]">check</span> : <span className="w-2 h-2 rounded-full bg-outline-variant"></span>}
                  </div>
                  <span className={`text-[11px] font-bold text-center ${isCurrent ? 'text-primary' : (isCompleted ? 'text-on-surface' : 'text-outline')}`}>{status}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-surface-container-lowest p-md rounded-lg border border-outline-variant">
          <p className="text-label-caps text-on-surface-variant mb-4">Latest Updates</p>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-primary mt-1.5"></div>
                <div className="w-0.5 h-full bg-outline-variant my-1"></div>
              </div>
              <div className="pb-4">
                <p className="text-body-sm font-bold text-on-surface">Shipment status updated to {po.shipment_status}</p>
                <p className="text-[11px] text-on-surface-variant">{new Date().toLocaleString()}</p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-2 h-2 rounded-full bg-outline"></div>
              </div>
              <div>
                <p className="text-body-sm font-bold text-on-surface">Order received by vendor</p>
                <p className="text-[11px] text-on-surface-variant">{po.order_date ? new Date(po.order_date).toLocaleString() : 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
      
      <div className="p-md border-t border-outline-variant flex justify-end">
        <button
          onClick={onClose}
          className="h-10 px-md rounded-lg font-bold text-body-md border border-outline hover:bg-surface-container-low transition-colors"
        >
          Close Tracking
        </button>
      </div>
    </Modal>
  );
};

export default PurchaseOrderTrackingModal;
