import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { RealTimeSyncProvider } from './contexts/RealTimeSyncContext';
import ProtectedRoute from './components/ProtectedRoute';

// Layout
import MainLayout from './components/layout/MainLayout';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Vehicles from './pages/Vehicles';
import Drivers from './pages/Drivers';
import LicenseCompliance from './pages/drivers/LicenseCompliance';
import SafetyInsights from './pages/drivers/SafetyInsights';
import Trips from './pages/Trips';
import Reports from './pages/Reports';
import FleetCompliance from './pages/reports/FleetCompliance';
import ReportBuilder from './pages/reports/ReportBuilder';
import Maintenance from './pages/Maintenance';
import MaintenanceScheduler from './pages/maintenance/MaintenanceScheduler';
import Technicians from './pages/maintenance/Technicians';
import Tasks from './pages/maintenance/Tasks';
import Fuel from './pages/Fuel';
import Expenses from './pages/Expenses';
import Settings from './pages/Settings';
import ActivityLog from './pages/activity/ActivityLog';
import { FullFleetMapPage } from './pages/fleet_map/FleetMapWrappers';

// Inventory & Procurement
import InventoryDashboard from './pages/inventory/InventoryDashboard';
import ProcurementRequests from './pages/inventory/ProcurementRequests';
import PurchaseOrders from './pages/inventory/PurchaseOrders';
import InventoryHistory from './pages/inventory/InventoryHistory';

// Help Center Pages
import HelpCenter from './pages/help/HelpCenter';
import HelpCategory from './pages/help/HelpCategory';
import HelpArticle from './pages/help/HelpArticle';
import SupportTickets from './pages/help/SupportTickets';
import TicketDetail from './pages/help/TicketDetail';

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <RealTimeSyncProvider>
            <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/vehicles" element={<Vehicles />} />
              <Route path="/drivers" element={<Drivers />} />
              <Route path="/drivers/license-compliance" element={<LicenseCompliance />} />
              <Route path="/drivers/safety-insights" element={<SafetyInsights />} />
              <Route path="/trips" element={<Trips />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/maintenance/scheduler" element={<MaintenanceScheduler />} />
              <Route path="/maintenance/technicians" element={<Technicians />} />
              <Route path="/maintenance/tasks" element={<Tasks />} />
              <Route path="/fuel" element={<Fuel />} />
              <Route path="/expenses" element={<Expenses />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/reports/fleet-compliance" element={<FleetCompliance />} />
              <Route path="/reports/builder" element={<ReportBuilder />} />
              <Route path="/settings" element={<Navigate to="/settings/profile" replace />} />
              <Route path="/settings/profile" element={<Settings />} />
              <Route path="/settings/app" element={<Settings />} />
              <Route path="/settings/org" element={<Settings />} />
              <Route path="/settings/permissions" element={<Settings />} />
              <Route path="/settings/roles" element={<Settings />} />
              <Route path="/settings/custom-roles" element={<Settings />} />
              <Route path="/settings/user-roles" element={<Settings />} />
              <Route path="/activity" element={<ActivityLog />} />
              <Route path="/fleet-map/full" element={<FullFleetMapPage />} />
              
              {/* Inventory & Procurement */}
              <Route path="/inventory/restock" element={<InventoryDashboard />} />
              <Route path="/inventory/procurement" element={<ProcurementRequests />} />
              <Route path="/inventory/purchase-orders" element={<PurchaseOrders />} />
              <Route path="/inventory/history" element={<InventoryHistory />} />
              
              {/* Help Center Routes */}
              <Route path="/help" element={<HelpCenter />} />
              <Route path="/help/category/:categoryId" element={<HelpCategory />} />
              <Route path="/help/article/:slug" element={<HelpArticle />} />
              <Route path="/help/tickets" element={<SupportTickets />} />
              <Route path="/help/tickets/:ticketId" element={<TicketDetail />} />
            </Route>
          </Route>
            </Routes>
          </RealTimeSyncProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
