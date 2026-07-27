import React from 'react';
import Modal from './Modal';

const ConfirmLogoutDialog = ({ isOpen, onClose, onConfirm, isLoggingOut }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Sign Out Confirmation" maxWidth="max-w-md">
      <div className="flex flex-col items-center text-center py-2">
        <div className="w-16 h-16 rounded-full bg-primary-container/30 border border-primary/25 flex items-center justify-center mb-4 shadow-inner">
          <span className="material-symbols-outlined text-primary text-[34px] translate-x-[1px]">logout</span>
        </div>
        <h3 className="font-title-md text-lg font-extrabold text-on-surface mb-2">
          Sign out of TransitOps?
        </h3>
        <p className="text-sm text-on-surface-variant mb-6 leading-relaxed px-2">
          Are you sure you want to sign out of your current session? You will need to re-authenticate to access logistics operations.
        </p>
        
        <div className="flex gap-3 w-full">
          <button 
            onClick={onClose}
            disabled={isLoggingOut}
            className="flex-1 px-3 py-2.5 bg-surface-container-high text-on-surface text-sm font-bold whitespace-nowrap rounded-lg hover:bg-surface-variant hover:text-on-surface transition-all disabled:opacity-50 flex items-center justify-center gap-1.5 active:scale-[0.98]"
          >
            <span className="material-symbols-outlined text-[18px]">close</span>
            <span>No, Cancel</span>
          </button>
          <button 
            onClick={onConfirm}
            disabled={isLoggingOut}
            className="flex-1 px-3 py-2.5 bg-primary text-on-primary text-sm font-bold whitespace-nowrap rounded-lg hover:bg-primary-container hover:text-on-primary-container transition-all flex items-center justify-center gap-1.5 disabled:opacity-50 shadow-sm active:scale-[0.98]"
          >
            {isLoggingOut ? (
              <>
                <span className="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
                <span>Signing out...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[18px]">logout</span>
                <span>Yes, Sign Out</span>
              </>
            )}
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default ConfirmLogoutDialog;
