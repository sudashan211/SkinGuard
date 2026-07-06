import { useAuthStore } from '@/store/authStore'
import { useUIStore } from '@/store/uiStore'
import { authService } from '@/services/auth'
import { useMutation, useQuery } from '@tanstack/react-query'
import type { LoginCredentials, SignupData } from '@/types/auth'
import { useNavigate } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'

// Version: 2.0 - Health Profile Setup Flow
export function useAuth() {
  const navigate = useNavigate()
  const { user, isAuthenticated, login, logout: logoutStore, setLoading } = useAuthStore()
  const { addToast } = useUIStore()

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (data) => {
      login(data.user, data.tokens.access_token, data.tokens.refresh_token)
      addToast({
        type: 'success',
        message: 'Login successful!',
      })
      
      // Redirect based on role
      switch (data.user.role) {
        case 'patient':
          navigate(ROUTES.PATIENT_DASHBOARD)
          break
        case 'doctor':
          navigate(ROUTES.DOCTOR_DASHBOARD)
          break
        case 'admin':
          navigate(ROUTES.ADMIN_DASHBOARD)
          break
      }
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.message || 'Login failed',
      })
    },
  })

  // Signup mutation
  const signupMutation = useMutation({
    mutationFn: (data: SignupData) => authService.signup(data),
    onSuccess: (data) => {
      console.log('[SIGNUP] Success! User role:', data.user.role)
      login(data.user, data.tokens.access_token, data.tokens.refresh_token)
      addToast({
        type: 'success',
        message: 'Account created successfully!',
      })
      
      // Redirect based on role
      switch (data.user.role) {
        case 'patient':
          // Redirect patients to health profile setup using window.location to avoid React Router interference
          console.log('[SIGNUP] Redirecting patient to:', ROUTES.HEALTH_PROFILE_SETUP)
          window.location.href = ROUTES.HEALTH_PROFILE_SETUP
          break
        case 'doctor':
          console.log('[SIGNUP] Redirecting doctor to dashboard')
          navigate(ROUTES.DOCTOR_DASHBOARD)
          break
        case 'admin':
          console.log('[SIGNUP] Redirecting admin to dashboard')
          navigate(ROUTES.ADMIN_DASHBOARD)
          break
      }
    },
    onError: (error: any) => {
      addToast({
        type: 'error',
        message: error.message || 'Signup failed',
      })
    },
  })

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      logoutStore()
      navigate(ROUTES.LOGIN)
      addToast({
        type: 'success',
        message: 'Logged out successfully',
      })
    },
    onError: () => {
      // Logout locally even if API call fails
      logoutStore()
      navigate(ROUTES.LOGIN)
    },
  })

  // Get current user query
  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authService.getCurrentUser(),
    enabled: isAuthenticated,
    retry: false,
  })

  return {
    user,
    isAuthenticated,
    isLoading: loginMutation.isPending || signupMutation.isPending || isLoadingUser,
    login: loginMutation.mutate,
    signup: signupMutation.mutate,
    logout: logoutMutation.mutate,
    currentUser,
  }
}
