import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import skSK from 'antd/locale/sk_SK';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { LoginPage } from './components/auth/LoginPage';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './components/dashboard/Dashboard';
import { DevicesPage } from './components/devices/DevicesPage';
import { RangesPage } from './components/ranges/RangesPage';
import { DHCPPage } from './components/dhcp/DHCPPage';
import { UsersPage } from './components/users/UsersPage';
import { LogsPage } from './components/logs/LogsPage';
import { SettingsPage } from './components/settings/SettingsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Načítavam...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/devices"
        element={
          <ProtectedRoute>
            <MainLayout>
              <DevicesPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/ranges"
        element={
          <ProtectedRoute>
            <MainLayout>
              <RangesPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/dhcp"
        element={
          <ProtectedRoute>
            <MainLayout>
              <DHCPPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/users"
        element={
          <ProtectedRoute>
            <MainLayout>
              <UsersPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/logs"
        element={
          <ProtectedRoute>
            <MainLayout>
              <LogsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <MainLayout>
              <SettingsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ConfigProvider locale={skSK}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
