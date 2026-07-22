import React from 'react';
import { NavLink } from 'react-router-dom';

const BottomNavigation = ({ toggleMobileMenu, isMobileMenuOpen }) => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
    { name: 'Trips', path: '/trips', icon: 'route' },
    { name: 'Drivers', path: '/drivers', icon: 'person_pin' },
    { name: 'Finance', path: '/expenses', icon: 'payments' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-surface border-t border-outline-variant flex items-center justify-around px-sm z-50 md:hidden">
      {navItems.map((item) => (
        <NavLink
          key={item.name}
          to={item.path}
          className={({ isActive }) =>
            `flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors ${
              isActive && !isMobileMenuOpen ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'
            }`
          }
        >
          {({ isActive }) => (
            <>
              <div className={`px-4 py-1 rounded-full ${isActive && !isMobileMenuOpen ? 'bg-primary-container/20' : ''}`}>
                <span 
                  className="material-symbols-outlined" 
                  style={{ fontVariationSettings: isActive && !isMobileMenuOpen ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {item.icon}
                </span>
              </div>
              <span className={`text-[10px] font-medium ${isActive && !isMobileMenuOpen ? 'font-bold' : ''}`}>
                {item.name}
              </span>
            </>
          )}
        </NavLink>
      ))}
      
      {/* Menu Button */}
      <button
        onClick={toggleMobileMenu}
        className={`flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors ${
          isMobileMenuOpen ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'
        }`}
      >
        <div className={`px-4 py-1 rounded-full ${isMobileMenuOpen ? 'bg-primary-container/20' : ''}`}>
          <span 
            className="material-symbols-outlined" 
            style={{ fontVariationSettings: isMobileMenuOpen ? "'FILL' 1" : "'FILL' 0" }}
          >
            menu
          </span>
        </div>
        <span className={`text-[10px] font-medium ${isMobileMenuOpen ? 'font-bold' : ''}`}>
          Menu
        </span>
      </button>
    </nav>
  );
};

export default BottomNavigation;
