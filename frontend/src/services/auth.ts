import api from './api'
import type { 
  LoginCredentials, 
  SignupData, 
  AuthResponse, 
  User 
} from '@/types/auth'

export const authService = {
  // Sign up new user
  async signup(data: SignupData): Promise<AuthResponse> {
    console.log('Auth service signup called with:', { ...data, password: '***' })
    const response = await api.post('/api/auth/signup', data)
    console.log('Signup response:', response.data)
    // For signup, the backend returns just the user profile
    // We need to login after signup to get tokens
    if (response.data.access_token) {
      // If tokens are included in signup response
      return {
        user: response.data.user,
        tokens: {
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token,
          token_type: response.data.token_type,
        }
      }
    }
    // If no tokens, just return user (will need to login separately)
    return {
      user: response.data,
      tokens: {
        access_token: '',
        refresh_token: '',
        token_type: 'bearer',
      }
    }
  },

  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login', credentials)
    // Transform backend response to match frontend expectations
    return {
      user: response.data.user,
      tokens: {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
      }
    }
  },

  // Logout user
  async logout(): Promise<void> {
    await api.post('/api/auth/logout')
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/auth/me')
    return response.data
  },

  // Refresh access token
  async refreshToken(refreshToken: string): Promise<{ access_token: string }> {
    const response = await api.post('/api/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}
