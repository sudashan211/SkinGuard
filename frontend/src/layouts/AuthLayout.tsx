import { Outlet, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { ROUTES } from '@/utils/constants'

export default function AuthLayout() {
  const { isAuthenticated, user } = useAuthStore()
  const location = useLocation()

  // If already authenticated, redirect to appropriate dashboard
  // UNLESS they're being redirected to the health profile setup page
  if (isAuthenticated && user && location.pathname !== ROUTES.HEALTH_PROFILE_SETUP) {
    switch (user.role) {
      case 'patient':
        return <Navigate to={ROUTES.PATIENT_DASHBOARD} replace />
      case 'doctor':
        return <Navigate to={ROUTES.DOCTOR_DASHBOARD} replace />
      case 'admin':
        return <Navigate to={ROUTES.ADMIN_DASHBOARD} replace />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  )
}
