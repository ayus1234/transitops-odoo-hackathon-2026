import React, { useEffect } from 'react';

const Modal = ({ isOpen, onClose, title, children, maxWidth = 'max-w-md' }) => {
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Map Tailwind max-w classes to explicit pixel values for inline styles
  const getInlineMaxWidth = (widthClass) => {
    if (widthClass.includes('max-w-sm')) return '384px';
    if (widthClass.includes('max-w-md')) return '448px';
    if (widthClass.includes('max-w-lg')) return '512px';
    if (widthClass.includes('max-w-xl')) return '576px';
    if (widthClass.includes('max-w-2xl')) return '672px';
    if (widthClass.includes('max-w-3xl')) return '768px';
    if (widthClass.includes('max-w-4xl')) return '896px';
    return '448px'; // default md
  };

  const inlineMaxWidth = getInlineMaxWidth(maxWidth);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="bg-surface rounded-xl shadow-lg border border-outline-variant flex flex-col animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-hidden shrink-0 mx-2"
        style={{ width: '100%', maxWidth: inlineMaxWidth, minWidth: 'min(100%, 320px)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center px-4 sm:px-lg py-md border-b border-outline-variant bg-surface-container-lowest shrink-0">
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface">{title}</h2>
          <button 
            onClick={onClose}
            className="p-1 rounded-full hover:bg-surface-variant text-on-surface-variant transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <div className="p-4 sm:p-lg overflow-y-auto min-h-0 flex-1">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
