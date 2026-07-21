import React from 'react';
import Modal from './Modal';

const ConfirmDeleteDialog = ({ isOpen, onClose, onConfirm, title, message, isDeleting }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} maxWidth="max-w-sm">
      <div className="flex flex-col items-center text-center">
        <div className="w-16 h-16 rounded-full bg-error-container flex items-center justify-center mb-md">
          <span className="material-symbols-outlined text-error text-[32px]">warning</span>
        </div>
        <p className="text-body-md text-on-surface-variant mb-xl">{message}</p>
        
        <div className="flex gap-md w-full">
          <button 
            onClick={onClose}
            disabled={isDeleting}
            className="flex-1 px-4 py-2 bg-surface-container-high text-on-surface-variant font-bold rounded hover:bg-surface-variant transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm}
            disabled={isDeleting}
            className="flex-1 px-4 py-2 bg-error text-on-error font-bold rounded hover:bg-error/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {isDeleting ? (
              <>
                <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ConfirmDeleteDialog;
