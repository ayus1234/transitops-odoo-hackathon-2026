import React, { createContext, useContext, useState, useCallback, useRef } from 'react';

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const showToast = useCallback((message, type = 'info') => {
    setToasts(prev => {
      // Prevent duplicate messages from being shown at the same time
      if (prev.some(t => t.message === message)) {
        return prev;
      }
      
      const id = Date.now().toString() + Math.random().toString(36).substring(2);
      
      // Auto remove after 3 seconds
      setTimeout(() => {
        setToasts(current => current.filter(t => t.id !== id));
      }, 3000);

      return [...prev, { id, message, type }];
    });
  }, []);

  return (
    <ToastContext.Provider value={{ showToast, addToast: showToast }}>
      {children}
      {/* Toast Container */}
      <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className={`px-4 py-3 rounded shadow-lg backdrop-blur text-body-sm font-bold flex items-center gap-2 pointer-events-auto transition-all duration-300 transform translate-y-0 opacity-100
              ${toast.type === 'info' ? 'bg-surface-variant text-on-surface-variant border border-outline' : ''}
              ${toast.type === 'success' ? 'bg-primary text-on-primary shadow-primary/20' : ''}
              ${toast.type === 'error' ? 'bg-error text-on-error shadow-error/20' : ''}
            `}
          >
            <span className="material-symbols-outlined text-[20px]">
              {toast.type === 'info' ? 'info' : toast.type === 'success' ? 'check_circle' : 'error'}
            </span>
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
