import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { ROUTES } from './utils/constants'
import { PWAHandler } from './components/common/PWAHandler'
import ErrorBoundary from './components/common/ErrorBoundary'
import ToastContainer from './components/common/ToastContainer'

// Layouts (to be created)
import MainLayout from './layouts/MainLayout'
import AuthLayout from './layouts/AuthLayout'

// Pages (to be created)
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import HealthProfileSetupPage from './pages/HealthProfileSetupPage'
import PatientDashboard from './pages/PatientDashboard'
import DoctorDashboard from './pages/DoctorDashboard'
import AdminDashboard from './pages/AdminDashboard'

// Protected Route Component
interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles: string[]
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} replace />
  }

  if (user && !allowedRoles.includes(user.role)) {
    // Redirect to appropriate dashboard based on role
    switch (user.role) {
      case 'patient':
        return <Navigate to={ROUTES.PATIENT_DASHBOARD} replace />
      case 'doctor':
        return <Navigate to={ROUTES.DOCTOR_DASHBOARD} replace />
      case 'admin':
        return <Navigate to={ROUTES.ADMIN_DASHBOARD} replace />
      default:
        return <Navigate to={ROUTES.HOME} replace />
    }
  }

  return <>{children}</>
}

function App() {
  return (
    <ErrorBoundary>
      <PWAHandler />
      <ToastContainer />
      <BrowserRouter>
        <Routes>
          {/* Public routes with main layout */}
          <Route element={<MainLayout />}>
            <Route path={ROUTES.HOME} element={<LandingPage />} />
          </Route>

          {/* Auth routes with auth layout */}
          <Route element={<AuthLayout />}>
            <Route path={ROUTES.LOGIN} element={<LoginPage />} />
            <Route path={ROUTES.SIGNUP} element={<SignupPage />} />
          </Route>

          {/* Health Profile Setup - Protected but without auth layout */}
          <Route path={ROUTES.HEALTH_PROFILE_SETUP} element={
            <ProtectedRoute allowedRoles={['patient']}>
              <HealthProfileSetupPage />
            </ProtectedRoute>
          } />

          {/* Patient routes */}
          <Route
            path="/patient/*"
            element={
              <ProtectedRoute allowedRoles={['patient']}>
                <PatientDashboard />
              </ProtectedRoute>
            }
          />

          {/* Doctor routes */}
          <Route
            path="/doctor/*"
            element={
              <ProtectedRoute allowedRoles={['doctor']}>
                <DoctorDashboard />
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* 404 - Redirect to home */}
          <Route path="*" element={<Navigate to={ROUTES.HOME} replace />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
