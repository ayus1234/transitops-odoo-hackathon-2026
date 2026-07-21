import React, { useState, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import BottomNavigation from './BottomNavigation';

const MainLayout = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen bg-background text-on-surface overflow-hidden">
      <Sidebar isMobileMenuOpen={isMobileMenuOpen} setIsMobileMenuOpen={setIsMobileMenuOpen} />
      {/* min-w-0 prevents flex children from overflowing the screen on mobile */}
      <main className="flex-1 flex flex-col min-h-screen relative md:ml-[240px] pb-16 md:pb-0 w-full overflow-x-hidden min-w-0">
        <Navbar />
        {/* Page Content injected via Outlet */}
        <Outlet />
      </main>
      <BottomNavigation toggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)} isMobileMenuOpen={isMobileMenuOpen} />
    </div>
  );
};

export default MainLayout;
