import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import { useAuthStore } from './store/authStore';
import Login from './pages/auth/Login';
import Dashboard from './pages/dashboard/Dashboard';
import CustomerList from './pages/customers/CustomerList';
import ProductList from './pages/products/ProductList';
import SalesHistory from './pages/sales-history/SalesHistory';
import SOPCycles from './pages/sop/SOPCycles';
import ForecastEntry from './pages/sop/ForecastEntry';
import Reports from './pages/reports/Reports';
import UserManagement from './pages/admin/UserManagement';
import Settings from './pages/admin/Settings';
import Layout from './components/common/Layout';
import ProtectedRoute from './components/common/ProtectedRoute';
import { ROUTES, ROLES } from './config/constants';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const { initAuth, isAuthenticated } = useAuthStore();

  // Initialize auth on app load
  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 6,
          },
        }}
      >
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route
              path={ROUTES.LOGIN}
              element={
                isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Login />
              }
            />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              {/* Redirect root to dashboard */}
              <Route index element={<Navigate to={ROUTES.DASHBOARD} replace />} />

              {/* Dashboard */}
              <Route path="dashboard" element={<Dashboard />} />

              {/* Customers */}
              <Route path="customers" element={<CustomerList />} />

              {/* Products */}
              <Route path="products" element={<ProductList />} />

              {/* Sales History */}
              <Route path="sales-history" element={<SalesHistory />} />

              {/* S&OP - Admin Only */}
              <Route
                path="sop/cycles"
                element={
                  <ProtectedRoute requireRoles={[ROLES.ADMIN]}>
                    <SOPCycles />
                  </ProtectedRoute>
                }
              />

              {/* S&OP - Forecast Entry */}
              <Route path="sop/forecast" element={<ForecastEntry />} />

              {/* Reports */}
              <Route path="reports" element={<Reports />} />

              {/* Admin - Users */}
              <Route
                path="admin/users"
                element={
                  <ProtectedRoute requireRoles={[ROLES.ADMIN]}>
                    <UserManagement />
                  </ProtectedRoute>
                }
              />

              {/* Admin - Settings */}
              <Route
                path="admin/settings"
                element={
                  <ProtectedRoute requireRoles={[ROLES.ADMIN]}>
                    <Settings />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* 404 Not Found */}
            <Route
              path="*"
              element={
                <div style={{ textAlign: 'center', padding: 50 }}>
                  <h1>404</h1>
                  <p>Page not found</p>
                  <a href="/">Go to Dashboard</a>
                </div>
              }
            />
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
