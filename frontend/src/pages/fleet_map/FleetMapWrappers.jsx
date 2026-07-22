import React, { useEffect } from 'react';
import FleetMapView from './FleetMapView';

export const FleetMapModal = ({ onClose }) => {
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      ></div>
      
      {/* Modal Content */}
      <FleetMapView isModal={true} onClose={onClose} />
    </div>
  );
};

export const FullFleetMapPage = () => {
  return (
    <div className="w-full h-full p-4 lg:p-8 animate-fade-in">
      <FleetMapView isModal={false} />
    </div>
  );
};
