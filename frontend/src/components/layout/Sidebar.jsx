import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = ({ isMobileMenuOpen, setIsMobileMenuOpen }) => {
  const { user, logout } = useAuth();

  // Helper to get initials
  const getInitials = (firstName, lastName) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase() || 'JD';
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { name: 'Vehicle Registry', path: '/vehicles', icon: 'local_shipping' },
    { name: 'Driver Management', path: '/drivers', icon: 'person_pin' },
    { name: 'Trip Management', path: '/trips', icon: 'route' },
    { name: 'Maintenance', path: '/maintenance', icon: 'build' },
    { name: 'Fuel Logs', path: '/fuel', icon: 'local_gas_station' },
    { name: 'Expenses', path: '/expenses', icon: 'payments' },
    { name: 'Reports', path: '/reports', icon: 'bar_chart' },
    { name: 'Settings', path: '/settings', icon: 'settings' },
  ];

  const inventoryNavItems = [
    { name: 'Inventory', path: '/inventory/restock', icon: 'inventory_2' },
    { name: 'Procurement', path: '/inventory/procurement', icon: 'shopping_cart' },
    { name: 'Purchase Orders', path: '/inventory/purchase-orders', icon: 'receipt_long' },
    { name: 'Inventory History', path: '/inventory/history', icon: 'history' },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[90] md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
      
      {/* Sidebar Drawer */}
      <aside className={`fixed left-0 top-0 h-full w-[240px] bg-surface-container border-r border-outline-variant flex-col z-[100] transition-transform duration-300 md:translate-x-0 md:flex ${isMobileMenuOpen ? 'translate-x-0 flex' : '-translate-x-full hidden'}`}>
        <div className="p-md flex items-center justify-between gap-sm">
          <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
            <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
              <span className="material-symbols-outlined text-on-primary text-[20px]">local_shipping</span>
            </div>
            <div>
              <h1 className="font-headline-md text-headline-md font-bold text-primary leading-tight">TransitOps</h1>
              <p className="text-[10px] uppercase tracking-wider font-bold text-outline">Logistics ERP</p>
            </div>
          </div>
          <button 
            className="md:hidden text-on-surface-variant hover:text-primary transition-colors"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <nav className="mt-md flex-1 px-sm space-y-1 overflow-y-auto scroll-hide">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-sm px-md py-2.5 rounded transition-all ${
                isActive
                  ? 'text-primary font-bold border-l-4 border-primary bg-primary-container/10 active:scale-[0.99]'
                  : 'hover:bg-surface-variant text-on-surface-variant font-medium'
              }`
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span className="font-body-md text-body-md">{item.name}</span>
          </NavLink>
        ))}
        
        <div className="pt-2 mt-2 border-t border-outline-variant">
          <p className="px-md py-2 text-label-caps text-outline font-bold uppercase tracking-wider text-[10px]">Inventory & Procurement</p>
          {inventoryNavItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-sm px-md py-2.5 rounded transition-all ${
                  isActive
                    ? 'text-tertiary font-bold border-l-4 border-tertiary bg-tertiary-container/10 active:scale-[0.99]'
                    : 'hover:bg-surface-variant text-on-surface-variant font-medium'
                }`
              }
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="font-body-md text-body-md">{item.name}</span>
            </NavLink>
          ))}
        </div>
      </nav>
      
      <div className="p-md border-t border-outline-variant mt-auto bg-surface-container-low cursor-pointer hover:bg-surface-variant transition-colors" onClick={logout}>
        <div className="flex flex-wrap md:flex-nowrap items-center gap-sm w-full md:w-auto">
          <div className="w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center text-primary font-bold text-xs shrink-0">
            {getInitials(user?.first_name, user?.last_name)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-body-sm font-bold text-on-surface truncate">
              {user ? `${user.first_name} ${user.last_name}` : 'Arjun Dispatcher'}
            </p>
            <p className="text-[10px] uppercase tracking-wider text-outline truncate group-hover:text-error transition-colors">
              Sign Out
            </p>
          </div>
        </div>
      </div>
    </aside>
    </>
  );
};

export default Sidebar;
