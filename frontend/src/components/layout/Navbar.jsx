import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { useToast } from '../../contexts/ToastContext';
import NotificationCenter from '../notifications/NotificationCenter';
import QuickActionsPanel from '../quick_actions/QuickActionsPanel';

const Navbar = () => {
  const location = useLocation();
  const path = location.pathname.substring(1); // remove leading slash
  const title = path.charAt(0).toUpperCase() + path.slice(1);

  const [isQuickActionsOpen, setIsQuickActionsOpen] = React.useState(false);

  const { showToast } = useToast();

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      showToast('Global Search is coming in v2.0 Enterprise', 'info');
      e.target.value = '';
    }
  };

  React.useEffect(() => {
    // Cleanup any legacy theme classes that might be stuck
    document.documentElement.classList.remove('dark', 'neon');
    localStorage.removeItem('theme');
  }, []);

  return (
    <header className="flex justify-between items-center h-16 px-md w-full sticky top-0 z-50 bg-surface border-b border-outline-variant shadow-sm transition-colors">
      <div className="flex items-center gap-lg flex-1">
        {/* Breadcrumbs */}
        <div className="flex items-center gap-1 md:gap-sm text-on-surface-variant font-title-sm text-title-sm whitespace-nowrap overflow-hidden min-w-0">
          <span className="hidden md:inline cursor-pointer hover:text-primary transition-colors">Workspace</span>
          <span className="hidden md:inline text-outline">/</span>
          <span className="font-bold text-primary border-b-2 border-primary pb-0.5 truncate">{title || 'Dashboard'}</span>
        </div>
      </div>
      <div className="flex items-center gap-2 md:gap-md">
        <div className="flex items-center gap-1 md:gap-sm mr-1 md:mr-2">
          <NotificationCenter />
          <Link to="/help" className="p-1 md:p-2 rounded-full hover:bg-surface-container-high transition-all text-on-surface-variant flex items-center justify-center">
            <span className="material-symbols-outlined">help</span>
          </Link>
        </div>
        {/* Dynamic primary action button */}
        <button onClick={() => setIsQuickActionsOpen(true)} className="bg-primary text-on-primary px-3 md:px-4 py-2 rounded font-bold text-body-sm hover:opacity-90 active:scale-95 transition-all flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto shadow-sm">
          <span className="material-symbols-outlined text-[18px]">add</span>
          <span className="hidden md:inline">New Action</span>
        </button>
      </div>

      <QuickActionsPanel 
        isOpen={isQuickActionsOpen} 
        onClose={() => setIsQuickActionsOpen(false)} 
      />
    </header>
  );
};

export default Navbar;
