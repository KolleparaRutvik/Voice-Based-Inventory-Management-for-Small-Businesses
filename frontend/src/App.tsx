import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import AppLayout from './layouts/AppLayout';
import AuthLayout from './layouts/AuthLayout';

// Route-level code splitting with React.lazy to fix initial page load lag
const LoginPage = lazy(() => import('./pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('./pages/auth/RegisterPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ProductsPage = lazy(() => import('./pages/products/ProductsPage'));
const AddProductPage = lazy(() => import('./pages/products/AddProductPage'));
const ProductDetailPage = lazy(() => import('./pages/products/ProductDetailPage'));
const InventoryPage = lazy(() => import('./pages/inventory/InventoryPage'));
const StockInPage = lazy(() => import('./pages/inventory/StockInPage'));
const StockOutPage = lazy(() => import('./pages/inventory/StockOutPage'));
const TransactionsPage = lazy(() => import('./pages/transactions/TransactionsPage'));
const VoiceAssistantPage = lazy(() => import('./pages/voice/VoiceAssistantPage'));
const BorrowingsPage = lazy(() => import('./pages/borrowings/BorrowingsPage'));
const SuppliersPage = lazy(() => import('./pages/suppliers/SuppliersPage'));
const OrdersPage = lazy(() => import('./pages/orders/OrdersPage'));
const AnalyticsPage = lazy(() => import('./pages/analytics/AnalyticsPage'));
const NotificationsPage = lazy(() => import('./pages/notifications/NotificationsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const MorePage = lazy(() => import('./pages/MorePage'));

function PageLoader() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 space-y-3">
      <div className="w-10 h-10 rounded-2xl gradient-primary flex items-center justify-center animate-pulse shadow-md">
        <svg className="w-5 h-5 text-white animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" strokeOpacity="0.25" />
          <path d="M12 2a10 10 0 0 1 10 10" strokeLinecap="round" />
        </svg>
      </div>
      <p className="text-surface-500 text-xs font-medium tracking-wide">Loading page...</p>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-2xl gradient-primary flex items-center justify-center animate-pulse">
            <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.2 14.47 16 12 16s-4.52-1.8-4.93-4.15a.998.998 0 0 0-.98-.85c-.61 0-1.09.54-1 1.14.49 3 2.89 5.35 5.91 5.78V20c0 .55.45 1 1 1s1-.45 1-1v-2.08a6.993 6.993 0 0 0 5.91-5.78c.1-.6-.39-1.14-1-1.14z"/>
            </svg>
          </div>
          <p className="text-surface-500 text-sm font-medium">Loading Vyapari Voice...</p>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;
  
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Auth Routes */}
        <Route element={<PublicRoute><AuthLayout /></PublicRoute>}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>

        {/* App Routes */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/new" element={<AddProductPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/stock/in" element={<StockInPage />} />
          <Route path="/stock/out" element={<StockOutPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/borrowings" element={<BorrowingsPage />} />
          <Route path="/suppliers" element={<SuppliersPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/voice" element={<VoiceAssistantPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/more" element={<MorePage />} />
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
}

export default App;
