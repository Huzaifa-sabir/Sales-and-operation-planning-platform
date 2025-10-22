import { Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/config/constants';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireRoles?: string[];
}

export default function ProtectedRoute({
  children,
  requireAuth = true,
  requireRoles = [],
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuthStore();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  // Redirect to login if authentication is required but user is not authenticated
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }

  // Check role-based access
  if (requireRoles.length > 0 && user) {
    if (!requireRoles.includes(user.role)) {
      // User doesn't have required role - show 403 or redirect
      return (
        <Navigate
          to={ROUTES.DASHBOARD}
          replace
          state={{ error: 'You do not have permission to access this page' }}
        />
      );
    }
  }

  return <>{children}</>;
}
